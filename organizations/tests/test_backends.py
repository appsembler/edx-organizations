"""
Appsembler: Tests for Auth backend functionality.
"""
import mock

from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from factories import OrganizationFactory, SiteFactory, UserFactory
from organizations import backends


@override_settings(SITE_ID=1000)
@mock.patch('organizations.backends.is_site_configuration_enabled', return_value=True)
class TestAuthBackends(TestCase):
    def setUp(self):
        super(TestAuthBackends, self).setUp()
        self.orgMemberBackend = backends.OrganizationMemberBackend()
        self.orgA = OrganizationFactory(short_name='orgA')
        self.orgB = OrganizationFactory(short_name='orgB')
        self.orgC = OrganizationFactory(short_name='orgC')
        self.orgD = OrganizationFactory(short_name='orgD')
        self.userA = UserFactory.create(username='userA', organizations=(self.orgA,))
        self.userB = UserFactory.create(username='userB', organizations=(self.orgB, self.orgC))
        self.superUser = UserFactory.create(username='superuser')
        self.superUser.is_superuser = True
        self.superUser.save()
        self.siteFoo = SiteFactory.create(domain='foo.dev', name='foo.dev', organizations=(self.orgA,))
        self.siteBar = SiteFactory.create(domain='bar.dev', name='bar.dev', organizations=(self.orgB, self.orgC))
        self.siteBaz = SiteFactory.create(domain='baz.dev', name='baz.dev', organizations=(self.orgD,))
        self.request = RequestFactory().post('dummy_url')

        patcher1 = mock.patch('organizations.backends.get_current_site')
        self.mock_get_current_site = patcher1.start()
        self.addCleanup(patcher1.stop)
        patcher2 = mock.patch('organizations.backends.get_value')
        self.mock_get_value = patcher2.start()
        self.addCleanup(patcher2.stop)
        # set return_values in each test method as needed

    def test_org_member_auth_with_single_organization(self, _):
        """
        Verify authentication where Site has single org.
        """
        self.mock_get_current_site.return_value = self.siteFoo
        self.mock_get_value.return_value = ('orgA')  # mocked course_org_filter value
        # plain user member of org in Site's configuration should pass
        authed = self.orgMemberBackend.authenticate(self.request, username='userA', password='test')
        self.assertEqual(authed, self.userA)
        # plain user not member of org in Site's configuration should fail
        authed = self.orgMemberBackend.authenticate(self.request, username='userB', password='test')
        self.assertEqual(authed, None)
        self.assertTrue(False)

    def test_org_member_auth_fails_if_siteconfig_does_not_have_org(self, _):
        """
        The course_org_filter on the Site's SiteConfiguration must include the Org's short name.
        """
        # why are we even using the course_org filter when we can just look up the Site's related Orgs?
        self.mock_get_current_site.return_value = self.siteFoo
        self.mock_get_value.return_value = ''
        authed = self.orgMemberBackend.authenticate(self.request, username='userA', password='test')
        self.assertEqual(authed, None)

    def test_superuser_member_accesses_all(self, _):
        """
        Verify a superuser user can authenticate to any Site.
        """
        self.mock_get_current_site.return_value = self.siteBaz
        self.mock_get_value.return_value = ('')
        authed = self.orgMemberBackend.authenticate(self.request, username='superuser', password='test')
        self.assertEqual(authed, self.superUser)

    def test_org_member_auth_with_multiple_organizations(self, _):
        """
        Verify authentication passes for organization member where Site has multiple orgs,
        but only if feature is enabled.
        """
        self.mock_get_current_site.return_value = self.siteBar
        self.mock_get_value.return_value = ('orgA', 'orgB')

        with override_settings(FEATURES={'TAHOE_ALLOW_MULTIPLE_COURSE_ORGS_PER_ORGANIZATION': False}):
            authed = self.orgMemberBackend.authenticate(self.request, username='userB', password='test')
            self.assertEqual(authed, None)

        with override_settings(FEATURES={'TAHOE_ALLOW_MULTIPLE_COURSE_ORGS_PER_ORGANIZATION': True}):
            authed = self.orgMemberBackend.authenticate(self.request, username='userB', password='test')
            self.assertEqual(authed, self.userB)
