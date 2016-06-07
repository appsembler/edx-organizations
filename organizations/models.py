# pylint: disable=no-init
# pylint: disable=old-style-class
# pylint: disable=too-few-public-methods
"""
Database ORM models managed by this Django app
Please do not integrate directly with these models!!!  This app currently
offers one programmatic API -- api.py for direct Python integration.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from microsite_configuration import microsite
from model_utils.models import TimeStampedModel

from microsite_configuration.models import Microsite


class Organization(TimeStampedModel):
    """
    An Organizatio is a representation of an entity which publishes/provides
    one or more courses delivered by the LMS. Organizations have a base set of
    metadata describing the organization, including id, name, and description.
    """
    name = models.CharField(verbose_name="Long name", max_length=255, db_index=True)
    short_name = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    logo = models.ImageField(
        upload_to='organization_logos',
        help_text=_(u'Please add only .PNG files for logo images.'),
        null=True, blank=True, max_length=255
    )
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UserOrganizationMapping',
        related_name="organizations"
    )

    def __unicode__(self):
        return u"{}".format(self.name)


class OrganizationCourse(TimeStampedModel):
    """
    An OrganizationCourse represents the link between an Organization and a
    Course (via course key). Because Courses are not true Open edX entities
    (in the Django/ORM sense) the modeling and integrity is limited to that
    of specifying course identifier strings in this model.
    """
    course_id = models.CharField(max_length=255, db_index=True)
    organization = models.ForeignKey(Organization, db_index=True)
    active = models.BooleanField(default=True)

    class Meta:
        """ Meta class for this Django model """
        unique_together = (("course_id", "organization"),)
        verbose_name = _('Link Course')
        verbose_name_plural = _('Link Courses')


class UserOrganizationMapping(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    organization = models.ForeignKey(Organization)
    is_active = models.BooleanField(default=False)


@receiver(signals.post_save, sender=User)
def my_callback(sender, **kwargs):
    user = kwargs.get('instance')
    if microsite.is_request_in_microsite() and user and not user.is_superuser:
        current_microsite = Microsite.get_microsite_for_domain(microsite.get_value('site_domain'))
        microsite_organizations = current_microsite.get_organizations()
        for organization_name in microsite_organizations:
            try:
                organization = Organization.objects.get(short_name=organization_name)
            except Organization.DoesNotExist:
                continue
            user_org, created = UserOrganizationMapping.objects.get_or_create(
                user=user, organization=organization)
