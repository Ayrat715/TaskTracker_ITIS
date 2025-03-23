from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from projects.models import Project, Employee
from tasks.models import Sprint, Task, Status, Priority, SprintTask

User = get_user_model()

class SprintViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', name='Test User',
                                             password='password')
        self.client.force_authenticate(user=self.user)
        self.group = Group.objects.create(name="Test Group")
        self.project = Project.objects.create(name='Test Project', description='Project Description',
                                              group_id=self.group.id, start_time=timezone.now(),
                                              end_time=timezone.now() + timezone.timedelta(days=7))
        self.sprint_data = {
            'name': 'Test Sprint',
            'description': 'Sprint Description',
            'start_time': '2025-01-01T10:00:00Z',
            'end_time': '2025-01-10T10:00:00Z',
            'project': self.project.id
        }

    def test_create_sprint(self):
        response = self.client.post('/api/sprints/', self.sprint_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.sprint_data['name'])

    def test_create_sprint_invalid(self):
        self.sprint_data['start_time'] = '2025-01-15T10:00:00Z'  # позже end_time
        response = self.client.post('/api/sprints/', self.sprint_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_sprint(self):
        sprint = Sprint.objects.create(**{
            'name': 'Initial Sprint',
            'description': 'Initial Desc',
            'start_time': '2025-02-01T10:00:00Z',
            'end_time': '2025-02-10T10:00:00Z',
            'project': self.project
        })
        update_data = {
            'name': 'Updated Sprint',
            'end_time': '2025-02-15T10:00:00Z'
        }
        response = self.client.patch(f'/api/sprints/{sprint.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sprint.refresh_from_db()
        self.assertEqual(sprint.name, 'Updated Sprint')
        self.assertEqual(str(sprint.end_time), '2025-02-15 10:00:00+00:00')

    def test_update_sprint_invalid_dates(self):
        self.sprint_data["project"] = Project.objects.get(id=4)
        sprint = Sprint.objects.create(**self.sprint_data)

        invalid_data = {
            'start_time': '2025-01-15T10:00:00Z',
            'end_time': '2025-01-10T10:00:00Z'
        }
        response = self.client.put(f'/api/sprints/{sprint.id}/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


class TaskViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com',
                                             name='Test User', password='password')
        self.client.force_authenticate(user=self.user)
        self.group = Group.objects.create(name="Test Group")
        self.project = Project.objects.create(name='Test Project', description='Project Description',
                                              group_id=self.group.id, start_time=timezone.now(),
                                              end_time=timezone.now() + timezone.timedelta(days=7) )
        self.sprint = Sprint.objects.create(
            name='Sprint 1', description='Sprint Desc',
            start_time='2025-01-01T10:00:00Z', end_time='2025-01-10T10:00:00Z',
            project=self.project
        )
        self.employee = Employee.objects.create(user=self.user, project=self.project)
        self.status = Status.objects.create(type='active')
        self.priority = Priority.objects.create(type='high')
        self.task_data = {
            'name': 'Test Task',
            'description': 'Task Description',
            'status': self.status.id,
            'given_time': '2025-01-01T08:00:00Z',
            'start_time': '2025-01-01T10:00:00Z',
            'end_time': '2025-01-05T10:00:00Z',
            'author': self.user.id,
            'priority': self.priority.id,
            'sprint': [self.sprint.id],
            'executor': self.employee.id
        }

    def test_create_task(self):
        response = self.client.post('/api/tasks/', self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.task_data['name'])

    def test_create_task_invalid_executor(self):
        other_group = Group.objects.create(name="Other Group")
        other_project = Project.objects.create(name='Other Project', description='Other Desc',
                                               group_id=other_group.id, start_time=timezone.now(),
                                               end_time=timezone.now() + timezone.timedelta(days=7) )
        other_employee = Employee.objects.create(user=self.user, project=other_project)
        self.task_data['executor'] = other_employee.id
        response = self.client.post('/api/tasks/', self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('executor', response.data)

    def test_update_task(self):
        task = Task.objects.create(
            name='Initial Task',
            description='Initial Desc',
            status=self.status,
            author=self.user,
            executor=self.employee,
            priority=self.priority,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=7),
            given_time=timezone.now() + timezone.timedelta(days=7)
        )
        SprintTask.objects.create(sprint=self.sprint, task=task)

        new_sprint = Sprint.objects.create(
            name='Sprint 2',
            description='New Sprint',
            start_time=timezone.make_aware(timezone.datetime(2025, 2,
                                                             1, 10, 0)),
            end_time=timezone.make_aware(timezone.datetime(2025, 2,
                                                           10, 10, 0)),
            project=self.project
        )
        update_data = {
            'name': 'Updated Task',
            'description': 'New Description',
            'sprint_ids': [new_sprint.id],
            'end_time': "2025-08-10T10:00:00Z"
        }
        response = self.client.put(f'/api/tasks/{task.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.name, 'Updated Task')
        sprint_task = SprintTask.objects.filter(task=task).first()
        self.assertIsNotNone(sprint_task)
        self.assertEqual(sprint_task.sprint.id, new_sprint.id)

    def test_update_task_invalid_sprint(self):
        task = Task.objects.create(**{
            'name': 'Test Task',
            'description': 'Desc',
            'status': self.status,
            'author': self.user,
            'executor': self.employee,
            'priority': self.priority,
            'end_time': timezone.now() + timezone.timedelta(days=7),
            'start_time': timezone.now(),
            'given_time': timezone.now() + timezone.timedelta(days=3)
        })
        invalid_data = {
            'sprint': [999]
        }
        response = self.client.patch(f'/api/tasks/{task.id}/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('sprint', response.data)

    def test_update_task_invalid_executor(self):
        task = Task.objects.create(**{
            'name': 'Test Task',
            'description': 'Desc',
            'status': self.status,
            'author': self.user,
            'executor': self.employee,
            'priority': self.priority,
            'given_time': timezone.now() + timezone.timedelta(days=3),
            'start_time': timezone.now(),
            'end_time': timezone.now() + timezone.timedelta(days=7)
        })
        other_group = Group.objects.create(name="Other Group")
        other_project = Project.objects.create(
            name='Other Project',
            group_id=other_group.id,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=7)
        )
        other_employee = Employee.objects.create(user=self.user, project=other_project)
        update_data = {
            'executor': other_employee.id
        }
        response = self.client.patch(f'/api/tasks/{task.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('executor', response.data)

    def test_update_task_invalid_dates(self):
        task = Task.objects.create(**{
            'name': 'Test Task',
            'description': 'Desc',
            'status': self.status,
            'author': self.user,
            'executor': self.employee,
            'priority': self.priority,
            'start_time': '2025-01-01T10:00:00Z',
            'end_time': '2025-01-05T10:00:00Z',
            'given_time': timezone.now() + timezone.timedelta(days=3)
        })
        invalid_data = {
            'start_time': '2025-01-10T10:00:00Z',
            'end_time': '2025-01-05T10:00:00Z'
        }
        response = self.client.patch(f'/api/tasks/{task.id}/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
