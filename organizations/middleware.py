"""
Tahoe middlewares for the organizations app.
"""


class OrganizationMiddleware(object):
    """
    Organization middleware
    """

    def process_request(self, request):
        """
        Populate the session with 'organization' variable.

        Deprecated: Proably we should remove this middleware
                    since we have the `get_current_organization` helper. -- Omar.
        """
        if not request.user.is_authenticated():
            return
        # FIXME: Figure out how to choose an Organization here once we allow a user to
        # have multiple organizations
        request.session['organization'] = request.user.organizations.all().first()
