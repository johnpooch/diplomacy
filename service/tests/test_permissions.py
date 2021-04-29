from django.test import RequestFactory, TestCase

from service import permissions
from core import models
from core.tests import DiplomacyTestCaseMixin


class TestUserIsNationState(TestCase, DiplomacyTestCaseMixin):

    permission_class = permissions.UserIsNationState

    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/')
        self.user = self.create_test_user()
        self.request.user = self.user
        self.view = None

    def check_object_permission(self, obj):
        permission = self.permission_class()
        return permission.has_object_permission(self.request, self.view, obj)

    def test_nation_state_is_user(self):
        nation_state = models.NationState(user=self.user)
        self.assertTrue(self.check_object_permission(nation_state))

    def test_nation_state_not_user(self):
        nation_state = models.NationState()
        self.assertFalse(self.check_object_permission(nation_state))
