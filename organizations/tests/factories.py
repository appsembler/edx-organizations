"""
Provides factory for User.
"""
# pylint: disable=too-few-public-methods
import uuid

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
import factory
from factory.django import DjangoModelFactory

from organizations.models import Organization, UserOrganizationMapping


class UserFactory(DjangoModelFactory):
    """ User creation factory."""
    class Meta(object):  # pylint: disable=missing-docstring
        model = User
        django_get_or_create = ('email', 'username')

    username = factory.Sequence(u'robot{0}'.format)
    email = factory.Sequence(u'robot+test+{0}@edx.org'.format)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    first_name = factory.Sequence(u'Robot{0}'.format)
    last_name = 'Test'
    is_staff = False
    is_active = True
    is_superuser = False

    @factory.post_generation
    def organizations(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for org in extracted:
                UserOrganizationMapping.objects.get_or_create(organization=org, user=self)


class SiteFactory(DjangoModelFactory):
    """
    Factory for django.contrib.sites.models.Site
    """
    class Meta(object):
        model = Site
        # django_get_or_create = ('domain',)

    name = factory.Sequence("test microsite {0}".format)
    domain = factory.Sequence("test-site{0}.testserver".format)

    @factory.post_generation
    def organizations(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for org in extracted:
                self.organizations.add(org)


class OrganizationFactory(DjangoModelFactory):
    """ Organization creation factory."""
    class Meta(object):  # pylint: disable=missing-docstring
        model = Organization

    name = factory.Sequence(u'organization name {}'.format)
    short_name = factory.Sequence(u'name{}'.format)
    description = factory.Sequence(u'description{}'.format)
    logo = None
    active = True
    edx_uuid = factory.LazyAttribute(lambda a: str(uuid.uuid4()))
