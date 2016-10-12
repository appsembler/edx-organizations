from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

from microsite_configuration import microsite
from microsite_configuration.models import Microsite


class OrganizationMemberMicrositeBackend(ModelBackend):
    """
    Extension of the regular ModelBackend that will check what Organizations are tied to the
    current microsite and compare that to the Organizations the user trying to log in belongs to.
    If there is a match between the two, the user is allowed to log in.
    """
    def authenticate(self, username=None, password=None, **kwargs):
        user = super(OrganizationMemberMicrositeBackend, self).authenticate(username, password, **kwargs)
        # superuser can log into any microsite
        if microsite.is_request_in_microsite() and user and not user.is_superuser:
            current_microsite = Microsite.get_microsite_for_domain(microsite.get_value('site_domain'))
            user_organizations = set(user.organizations.values_list('short_name', flat=True))
            microsite_organizations = current_microsite.get_organizations()
            if not user_organizations.intersection(microsite_organizations):
                raise PermissionDenied
        return user
