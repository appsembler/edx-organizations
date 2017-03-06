
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

