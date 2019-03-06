from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from openedx.core.djangoapps.theming.helpers import get_current_site
from openedx.core.djangoapps.site_configuration.helpers import is_site_configuration_enabled, get_value


class DefaultSiteBackend(ModelBackend):
    """
    User can log in to the default/root site (edx.appsembler.com) because it is required during the signup.
    Also, superusers (appsembler admins) can log into any site.
    """
    def authenticate(self, *args, **kwargs):
        user = super(DefaultSiteBackend, self).authenticate(*args, **kwargs)
        # superuser can log into any microsite
        site = get_current_site()
        is_default_site = site.id == settings.SITE_ID
        if user:
            if is_default_site:
                return user
            if user.is_superuser:
                return user
        return None


class OrganizationMemberBackend(ModelBackend):
    """
    Extension of the regular ModelBackend that will check what Organizations are tied to the
    current microsite and compare that to the Organizations the user trying to log in belongs to.
    If there is a match between the two, the user is allowed to log in.
    """
    def authenticate(self, *args, **kwargs):
        user = super(OrganizationMemberBackend, self).authenticate(*args, **kwargs)
        # superuser can log into any microsite
        site = get_current_site()
        is_default_site = site.id == settings.SITE_ID
        if not is_default_site and is_site_configuration_enabled() and user and not user.is_superuser:
            user_organizations = set(user.organizations.values_list('short_name', flat=True))
            site_organization = get_value('course_org_filter')
            if site_organization in user_organizations:
                return user
        return None


class SiteMemberBackend(ModelBackend):
    """
    Extension of the regular ModelBackend that will check whether the user is a member of the currently
    active site.
    """
    def authenticate(self, *args, **kwargs):
        user = super(SiteMemberBackend, self).authenticate(*args, **kwargs)
        # superuser can log into any microsite
        site = get_current_site()
        is_default_site = site.id == settings.SITE_ID
        if not is_default_site and is_site_configuration_enabled() and user and not user.is_superuser:
            if user.id in site.usersitemapping_set.select_related('user').values_list('user__id',flat=True):
                return user
        return None
