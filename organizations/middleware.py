from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.site_configuration.helpers import is_site_configuration_enabled
from openedx.core.djangoapps.site_configuration.models import SiteConfiguration


class OrganizationMiddleware(object):
    """
    Organization middleware
    """
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        # FIXME: Figure out how to choose an Organization here once we allow a user to
        # have multiple organizations
        request.session['organization'] = request.user.organizations.all().first()
        return


class CurrentSiteByCourseOrgMiddleware(object):
    """
    Add the current Site to the request by course org.
    Add this via the EXTRA_MIDDLEWARE_CLASSES ENV_TOKEN: e.g., 
        ['organizations.middleware.CurrentSiteByCourseOrgMiddleware',]
    )
    """
    def process_request(self, request):
        if is_site_configuration_enabled():
            course_id = request.session.get('course_id', None)  # via courseware.middleware
            if not course_id:
                return
            org = CourseKey.from_string(course_id).org

            # TODO: this is ugly. borrowed from our SiteConfiguration.get_value_by_org
            # can't defer page_elements with jsonfield 2.0.2 and Django 1.11 https://github.com/rpkilby/jsonfield/issues/198
            for configuration in SiteConfiguration.objects.filter(values__contains=org, enabled=True).defer('sass_variables').all():
                course_org_filter = configuration.get_value('course_org_filter', [])
                if not isinstance(course_org_filter, list):
                    course_org_filter = [course_org_filter]
                if org in course_org_filter:
                    # TODO: assumes one match only. handle edge case
                    site = configuration.site
                    break

            if site:
                request.site = site
        else:
            # preserve request.site set from django.contrib.sites.middleware
            return
