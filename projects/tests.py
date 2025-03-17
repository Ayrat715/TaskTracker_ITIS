from django.test import TestCase
from users.models import User, Group
from projects.models import Project, ProjectRole, Employee
from django.utils.timezone import now, timedelta


class ProjectModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="Development Team")
        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            start_time=now(),
            end_time=now() + timedelta(days=30),
            group=self.group
        )

    def test_project_creation(self):
        self.assertEqual(self.project.name, "Test Project")
        self.assertEqual(self.project.description, "A test project")
        self.assertEqual(self.project.group.name, "Development Team")

class ProjectRoleModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="QA Team")
        self.project = Project.objects.create(
            name="QA Project",
            description="A QA test project",
            start_time=now(),
            end_time=now() + timedelta(days=15),
            group=self.group
        )
        self.role = ProjectRole.objects.create(name="Tester", project=self.project)

    def test_project_role_creation(self):
        self.assertEqual(self.role.name, "Tester")
        self.assertEqual(self.role.project.name, "QA Project")

class EmployeeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@example.com", name="John Doe", password="securepass")
        self.group = Group.objects.create(name="Engineering Team")
        self.project = Project.objects.create(
            name="Backend Project",
            description="A backend project",
            start_time=now(),
            end_time=now() + timedelta(days=45),
            group=self.group
        )
        self.role = ProjectRole.objects.create(name="Backend Developer", project=self.project)
        self.employee = Employee.objects.create(user=self.user, project=self.project, role=self.role)

    def test_employee_creation(self):
        self.assertEqual(self.employee.user.name, "John Doe")
        self.assertEqual(self.employee.project.name, "Backend Project")
        self.assertEqual(self.employee.role.name, "Backend Developer")

    def test_default_current_load(self):
        self.assertEqual(self.employee.current_load, 0)

    def test_completed_tasks_count(self):
        self.assertEqual(self.employee.completed_tasks_count, 0)

    def test_average_completion_time(self):
        self.assertEqual(self.employee.average_completion_time, 0)
