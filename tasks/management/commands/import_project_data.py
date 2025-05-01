from datetime import datetime
from django.core.management.base import BaseCommand
from projects.models import Employee, Project
from tasks.models import Executor, Task, Priority, Status, SprintTask, Sprint
from django.contrib.auth.models import Group
from django.utils import timezone
import pandas as pd
from datasets import load_dataset
from django.contrib.auth import get_user_model
User = get_user_model()

class Command(BaseCommand):
    help = 'Импорт данных из датасета'

    def handle(self, *args, **kwargs):
        ds = load_dataset("JohnVans123/ProjectManagement")
        df = pd.DataFrame(ds['train'])
        df = df.rename(columns={
            'Priority': 'priority',
            'Task Status': 'status',
            'Assigned To': 'assignee_email',
            'Start Date': 'start_time',
            'End Date': 'end_time',
            'Task ID': 'task_id',
            'Task Name': 'task_name',
            'Project Name': 'project_name',
            'Project ID': 'project_id',
        })
        df['author_email'] = df['assignee_email']
        df['description'] = ''
        employee_load = df.groupby('assignee_email')['task_id'].count().to_dict()
        df['current_load'] = df['assignee_email'].map(employee_load).fillna(0)
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce', dayfirst=True)
        df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce', dayfirst=True)
        df['start_time'] = df['start_time'].apply(
            lambda x: timezone.make_aware(x) if not pd.isnull(x) else x
        )
        df['end_time'] = df['end_time'].apply(
            lambda x: timezone.make_aware(x) if not pd.isnull(x) else x
        )
        default_group, _ = Group.objects.get_or_create(name="Default Group")
        user_emails = set(df['assignee_email'].dropna())
        users_db = {}
        for email in user_emails:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    name=email.split('@')[0],
                    password=User.objects.make_random_password()
                )
                user.groups.add(default_group)
            else:
                user = User.objects.get(email=email)
            users_db[email] = user

        STATUS_MAPPING = {
            'Pending': 'required check',
            'In Progress': 'active',
            'Behind': 'planned',
            'On Track': 'required check',
            'Completed': 'completed',
            'On Hold': 'archived'
        }

        statuses = {}
        status_names = df['status'].dropna().unique()
        for original_status_name in status_names:
            status_name = STATUS_MAPPING.get(original_status_name, original_status_name)
            status_obj, _ = Status.objects.get_or_create(type=status_name)
            statuses[original_status_name] = status_obj

        valid_priorities = ['high', 'medium', 'low', 'default']
        df['priority'] = df['priority'].str.strip().str.lower().replace({
            'med': 'medium',
            'high': 'high',
            'low': 'low',
            'default': 'default'
        }).fillna('default')

        priorities = {}
        for priority_name in df['priority'].unique():
            if priority_name not in valid_priorities:
                priority_name = 'default'
            priority_obj, _ = Priority.objects.get_or_create(type=priority_name)
            priorities[priority_name] = priority_obj

        project_names = df['project_name'].dropna().unique()
        projects_db = {}
        for project_name in project_names:
            project, _ = Project.objects.get_or_create(
                name=project_name,
                start_time=timezone.make_aware(datetime(2023, 7, 8),
                                               timezone.get_current_timezone()),
                group=default_group
            )
            projects_db[project_name] = project

        for project in projects_db.values():
            Sprint.objects.get_or_create(
                project=project,
                name=f"Основной спринт {project.name}",
                start_time=project.start_time,
                end_time=project.end_time
            )

        employees_db = {}
        for _, entry in df.iterrows():
            assignee_email = entry.get('assignee_email')
            project_name = entry.get('project_name')
            if pd.notna(assignee_email) and pd.notna(project_name):
                user = users_db.get(assignee_email)
                project = projects_db.get(project_name)
                if user and project:
                    employee, _ = Employee.objects.get_or_create(user=user, project=project)
                    employee.current_load = entry.get('current_load', 0)
                    employee.save()
                    employees_db[(assignee_email, project_name)] = employee

        tasks_to_create = []
        for idx, entry in df.iterrows():
            project = projects_db.get(entry.get('project_name'))
            if not project:
                continue

            status_obj = statuses.get(entry.get('status'))
            priority_obj = priorities.get(entry.get('priority'))

            start_time = entry.get('start_time')
            end_time = entry.get('end_time')
            if start_time and end_time and start_time > end_time:
                continue

            author_email = entry.get('author_email')
            project_name = entry.get('project_name')
            author_employee = employees_db.get((author_email, project_name)) \
                if author_email and project_name else None

            task = Task(
                name=entry.get('task_name', ''),
                description=entry.get('description', ''),
                priority=priority_obj,
                status=status_obj,
                start_time=start_time,
                end_time=end_time,
                author=author_employee
            )
            tasks_to_create.append(task)

        Task.objects.bulk_create(tasks_to_create)

        task_id_mapping = {}
        for idx, task in enumerate(tasks_to_create):
            original_task_id = df.iloc[idx]['task_id']
            task_id_mapping[original_task_id] = task.id

        sprint_tasks_to_create = []
        for idx, entry in df.iterrows():
            original_task_id = entry.get('task_id')
            new_task_id = task_id_mapping.get(original_task_id)
            if not new_task_id:
                continue

            task = Task.objects.get(id=new_task_id)
            project = projects_db.get(entry.get('project_name'))
            if not project:
                continue

            sprint = Sprint.objects.filter(project=project).first()
            if sprint:
                sprint_tasks_to_create.append(SprintTask(task=task, sprint=sprint))

        SprintTask.objects.bulk_create(sprint_tasks_to_create)

        executors_to_create = []
        for idx, entry in df.iterrows():
            original_task_id = entry.get('task_id')
            new_task_id = task_id_mapping.get(original_task_id)
            if not new_task_id:
                continue

            task = Task.objects.get(id=new_task_id)
            assignee_email = entry.get('assignee_email')
            project_name = entry.get('project_name')

            if pd.notna(assignee_email) and pd.notna(project_name):
                employee = employees_db.get((assignee_email, project_name))
                if employee:
                    executors_to_create.append(Executor(task=task, employee=employee))

        Executor.objects.bulk_create(executors_to_create)
        self.stdout.write(self.style.SUCCESS('Импорт завершен успешно'))
