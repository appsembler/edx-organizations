"""
Authentication backends for Tahoe's multi-tenancy.
"""

from django.conf import settings
from django.contrib.auth.backends import AllowAllUsersModelBackend, ModelBackend
from openedx.core.djangoapps.theming.helpers import get_current_site  # pylint: disable=import-error
from openedx.core.djangoapps.site_configuration.helpers import (  # pylint: disable=import-error
    is_site_configuration_enabled,
    get_value,
)


class DefaultSiteBackend(ModelBackend):
    """
    User can log in to the default/root site (edx.appsembler.com) because it is required during the signup.
    Also, superusers (appsembler admins) can log into any site.
    """

    def authenticate(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Authenticate superusers only.
        """
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


class OrganizationMemberBackend(AllowAllUsersModelBackend):
    """Backend for organization based authentication

    This class is an extension of Django's `AllowAllUserModelBackend`

    This class checks that the user to authenticate belongs to one of the
    organizations in the specified site

    This class extends `AllowAllUserModelBackend` instead of `ModelBackend`
    because users need to be able to authenticate when the `user.is_active` is
    `False`. The reason for this is that Open edX has an email verification
    scheme that uses `User.is_active` in order to prevent user activity until
    the users have verified their email. Effectively, edx-platform LMS user
    authentication state is used to manage authorization state.

    The key problem is that Django's `django.contrib.auth.backends.ModelBackend`
    is called with `not user.is_active` and Ironwood introduced a check to test
    authentication on a not yet authorized user. This breaks Tahoe multisite
    behavior. Extending `AllowAllUsersModelBackend` restores correct behavior.

    For further reference, see settings files and read Django documentation for
    `AUTHENTICATION_BACKENDS`
    """
    def authenticate(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Authenticate organization learners.
        """
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

    Deprecated: Should be removed because `UserSiteMapping` should be removed.
    """

    def authenticate(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Authenticate organization learners.
        """
        user = super(SiteMemberBackend, self).authenticate(*args, **kwargs)
        # superuser can log into any microsite
        site = get_current_site()
        is_default_site = site.id == settings.SITE_ID
        if not is_default_site and is_site_configuration_enabled() and user and not user.is_superuser:
            if user.id in site.usersitemapping_set.select_related('user').values_list('user__id', flat=True):
                return user
        return None
