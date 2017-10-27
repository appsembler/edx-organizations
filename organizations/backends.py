from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from openedx.core.djangoapps.theming.helpers import get_current_site
from openedx.core.djangoapps.site_configuration.helpers import is_site_configuration_enabled, get_value

from hr_management.models import HrManager

from .models import UserOrganizationMapping

class DefaultSiteBackend(ModelBackend):
    """
    User can log in to the default/root site (edx.appsembler.com) because it is required during the signup.
    Also, superusers (appsembler admins) can log into any site.
    """
    def authenticate(self, username=None, password=None, **kwargs):
        user = super(DefaultSiteBackend, self).authenticate(username, password, **kwargs)
        # superuser can log into any microsite
        site = get_current_site()
        is_default_site = site.id == settings.SITE_ID
        if user:
            if is_default_site:
                return user
            # superusers and staff users can access any site
            if user.is_superuser or user.is_staff: 
                return user
        return None


class OrganizationMemberBackend(ModelBackend):
    """
    Extension of the regular ModelBackend that will check what Organizations are tied to the
    current microsite and compare that to the Organizations the user trying to log in belongs to.
    If there is a match between the two, the user is allowed to log in.
    """
    def authenticate(self, username=None, password=None, **kwargs):
        user = super(OrganizationMemberBackend, self).authenticate(username, password, **kwargs)
        # superuser can log into any microsite
        site = get_current_site()
        is_default_site = site.id == settings.SITE_ID
        if not is_default_site and is_site_configuration_enabled() and user and not user.is_superuser:
            user_organizations = set(user.organizations.values_list('short_name', flat=True))
            site_organization = get_value('course_org_filter')

            # check if user is manager of microsite
            hr_manager = HrManager.objects.filter(user=user, organization__short_name=site_organization)
            if hr_manager:
                return user

            #make sure user has been granted permission to log into microsite
            mapping = UserOrganizationMapping.objects.filter(
                    organization__short_name=site_organization,
                    user=user
                ) 
            if not mapping or not mapping.first().is_active:
                return None

            if site_organization in user_organizations:
                return user

        return None


class SiteMemberBackend(ModelBackend):
    """
    Extension of the regular ModelBackend that will check whether the user is a member of the currently
    active site.
    """
    def authenticate(self, username=None, password=None, **kwargs):
        user = super(SiteMemberBackend, self).authenticate(username, password, **kwargs)
        # superuser can log into any microsite
        site = get_current_site()
        is_default_site = site.id == settings.SITE_ID
        if not is_default_site and is_site_configuration_enabled() and user and not user.is_superuser:
            if user.id in site.usersitemapping_set.select_related('user').values_list('user__id',flat=True):
                return user
        return None
