from unittest.mock import MagicMock, patch
from django.test import SimpleTestCase
from users.models import User, Group, GroupUser

class GroupUserModelTest(SimpleTestCase):
    @patch('users.models.User.objects.create')
    @patch('users.models.Group.objects.create')
    @patch('users.models.GroupUser.objects.create')
    def test_group_user_creation(self, mock_group_user_create, mock_group_create, mock_user_create):
        mock_user = MagicMock()
        mock_user.email = "groupuser@example.com"
        mock_user.name = "Group User"
        mock_user.password = "pass"

        mock_group = MagicMock()
        mock_group.name = "Test Group"

        mock_group_user = MagicMock()
        mock_group_user.user = mock_user
        mock_group_user.group = mock_group

        mock_user_create.return_value = mock_user
        mock_group_create.return_value = mock_group
        mock_group_user_create.return_value = mock_group_user

        created_user = User.objects.create(
            email="groupuser@example.com",
            name="Group User",
            password="pass"
        )
        created_group = Group.objects.create(name="Test Group")
        group_user = GroupUser.objects.create(
            user=created_user,
            group=created_group
        )

        mock_user_create.assert_called_once_with(
            email="groupuser@example.com",
            name="Group User",
            password="pass"
        )
        mock_group_create.assert_called_once_with(name="Test Group")
        mock_group_user_create.assert_called_once_with(
            user=created_user,
            group=created_group
        )

        self.assertEqual(group_user.user.name, "Group User")
        self.assertEqual(group_user.group.name, "Test Group")
