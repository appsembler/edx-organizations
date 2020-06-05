"""
Database ORM models managed by this Django app
Please do not integrate directly with these models!!!  This app currently
offers one programmatic API -- api.py for direct Python integration.
"""
import re
import uuid
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel


class Organization(TimeStampedModel):
    """
    An Organization is a representation of an entity which publishes/provides
    one or more courses delivered by the LMS. Organizations have a base set of
    metadata describing the organization, including id, name, and description.
    """
    name = models.CharField(max_length=255, db_index=True)
    short_name = models.CharField(
        max_length=255, db_index=True, verbose_name='Short Name',
        help_text=_('Please do not use spaces or special characters. Only allowed special characters '
                    'are period (.), hyphen (-) and underscore (_).')
    )
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(
        upload_to='organization_logos',
        help_text=_('Please add only .PNG files for logo images. This logo will be used on certificates.'),
        null=True, blank=True, max_length=255
    )
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UserOrganizationMapping',
        related_name="organizations"
    )
    sites = models.ManyToManyField(
        'sites.Site',
        related_name='organizations',
    )
    edx_uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    def __unicode__(self):
        return u"{name} ({short_name})".format(name=self.name, short_name=self.short_name)

    def get_tier_for_org(self):
        from tiers.models import Tier
        t = Tier.objects.defer('organization').get(organization__edx_uuid=self.edx_uuid)
        tier_object = Tier(name=t.name,
                tier_enforcement_exempt=t.tier_enforcement_exempt,
                tier_enforcement_grace_period=t.tier_enforcement_grace_period,
                tier_expires_at=t.tier_expires_at,
                organization=self)
        return tier_object

    def clean(self):
        if not re.match("^[a-zA-Z0-9._-]*$", self.short_name):
            raise ValidationError(_('Please do not use spaces or special characters in the short name '
                                    'field. Only allowed special characters are period (.), hyphen (-) '
                                    'and underscore (_).'))


class OrganizationCourse(TimeStampedModel):
    """
    An OrganizationCourse represents the link between an Organization and a
    Course (via course key). Because Courses are not true Open edX entities
    (in the Django/ORM sense) the modeling and integrity is limited to that
    of specifying course identifier strings in this model.
    """
    course_id = models.CharField(max_length=255, db_index=True, verbose_name='Course ID')
    organization = models.ForeignKey(Organization, db_index=True)
    active = models.BooleanField(default=True)

    class Meta(object):
        """ Meta class for this Django model """
        unique_together = (('course_id', 'organization'),)
        verbose_name = _('Link Course')
        verbose_name_plural = _('Link Courses')


@python_2_unicode_compatible
class UserOrganizationMapping(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    organization = models.ForeignKey(Organization)
    is_active = models.BooleanField(default=True)
    is_amc_admin = models.BooleanField(default=False)

    def __str__(self):
        return 'UserOrganizationMapping<{email}, {organization}>'.format(
            email=self.user.email,
            organization=self.organization.short_name,
        )


class UserSiteMapping(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    site = models.ForeignKey(Site)
    is_active = models.BooleanField(default=True)
    is_amc_admin = models.BooleanField(default=False)
