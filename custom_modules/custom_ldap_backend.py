# custom_ldap_backend.py

from django_auth_ldap.backend import LDAPBackend, _LDAPUser
from django.conf import settings
from django.contrib.auth.models import Group
import logging

logger = logging.getLogger(__name__)


class CustomLDAPUser(_LDAPUser):
    def _get_or_create_user(self, force_save=False):
        user, created = super()._get_or_create_user(force_save)
        # Additional custom logic, e.g., add user to specific Django groups based on LDAP group membership
        return user, created

    def _mirror_groups(self):
        """
        Mirrors the user's LDAP groups, meaning:
        1. If a name is in AUTH_LDAP_GROUP_MAPPINGS, use the mapped name.
        2. Otherwise, ignore the group.
        """
        # Get the desired group names
        desired_group_names = set(settings.AUTH_LDAP_GROUP_MAPPINGS.values())
        logger.info(f"Desired group names: {desired_group_names}")

        current_group_names = set(self._get_groups().get_group_names())
        logger.info(f"Current LDAP group names for user: {current_group_names}")

        current_group_names = current_group_names & desired_group_names
        logger.info(f"Filtered group names to be mirrored: {current_group_names}")
        # Mirror only the groups that are in our desired list
        current_group_names = set(self._get_groups().get_group_names())
        current_group_names = current_group_names & desired_group_names

        # The rest of the logic remains the same
        mirrored_groups = set()
        for group in self._user.groups.all():
            if group.name not in current_group_names:
                self._user.groups.remove(group)
            else:
                mirrored_groups.add(group.name)

        for group_name in current_group_names:
            if group_name not in mirrored_groups:
                group, created = Group.objects.get_or_create(name=group_name)
                self._user.groups.add(group)



class CustomLDAPBackend(LDAPBackend):
    def get_or_create_user(self, username, ldap_user):
        return ldap_user.get_or_create_user()
