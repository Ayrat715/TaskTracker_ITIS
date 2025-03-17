from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta
from django.test import TestCase
from projects.models import Employee, Project, ProjectRole
from users.models import User, Group
from tasks.models import (TaskCategory, Status, Priority, Sprint, Task, Executor, SprintTask, Comment)


class PriorityModelTest(TestCase):
    def test_priority_creation(self):
        priority, created = Priority.objects.get_or_create(type="high")
        self.assertEqual(priority.type, "high")
        self.assertEqual(priority.weight, 4)

    def test_priority_validation(self):
        priority = Priority(type="medium", weight=5)
        with self.assertRaises(ValidationError):
            priority.clean()

    def test_save_priority(self):
        priority, created = Priority.objects.get_or_create(type="low")
        self.assertEqual(priority.weight, 2)


class ExecutorModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="Test Group")
        self.user = User.objects.create_user(
            email="executor@example.com",
            name="nastya",
            password="testpass123"
        )
        self.project = Project.objects.create(
            name="Test Project",
            start_time=now(),
            end_time=now() + timedelta(days=30),
            group=self.group
        )
        self.role = ProjectRole.objects.create(name="Developer", project=self.project)
        self.employee = Employee.objects.create(
            user=self.user,
            project=self.project,
            role=self.role
        )
        self.status, created = Status.objects.get_or_create(type="active")
        self.priority, _ = Priority.objects.get_or_create(type="default", defaults={"weight": 1})
        self.task = Task.objects.create(
            name="Task A", description="Some task", status=self.status,
            given_time=now(), start_time=now(), end_time=now() + timedelta(days=1),
            author=self.user, priority=self.priority
        )

    def test_executor_creation(self):
        executor = Executor.objects.create(employee=self.employee, task=self.task)
        self.assertEqual(Executor.objects.count(), 1)
        self.assertEqual(executor.task, self.task)
        self.assertEqual(executor.employee, self.employee)


class CommentModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="Test Group")
        self.user = User.objects.create(name="commenter")
        self.project = Project.objects.create(
            name="Test Project",
            start_time=now(),
            end_time=now() + timedelta(days=30),
            group=self.group
        )
        self.role = ProjectRole.objects.create(name="Developer", project=self.project)
        self.employee = Employee.objects.create(
            user=self.user,
            project=self.project,
            role=self.role
        )
        self.status, _ = Status.objects.get_or_create(type="active")
        self.priority, _ = Priority.objects.get_or_create(type="default", defaults={"weight": 1})
        self.task = Task.objects.create(
            name="Task B", description="Another task", status=self.status,
            given_time=now(), start_time=now(), end_time=now() + timedelta(days=2),
            author=self.user, priority=self.priority
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            title="Needs work",
            body="Fix some issues",
            employee=self.employee,
            task=self.task
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.task, self.task)
        self.assertEqual(comment.employee, self.employee)
