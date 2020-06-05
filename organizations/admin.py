""" Django admin pages for organization models """
from django.contrib import admin
from organizations.models import (Organization, OrganizationCourse, UserOrganizationMapping)
from django.utils.translation import ugettext_lazy as _


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """ Admin for the Organization model. """
    actions = ['activate_selected', 'deactivate_selected']
    list_display = ('name', 'short_name', 'logo', 'active',)
    list_filter = ('active',)
    ordering = ('name', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('name', 'short_name',)
    actions = ['activate_selected', 'deactivate_selected']

    def get_actions(self, request):
        actions = super(OrganizationAdmin, self).get_actions(request)

        # Remove the delete action.
        del actions['delete_selected']

        return actions

    def activate_selected(self, request, queryset):
        """ Activate the selected entries. """
        queryset.update(active=True)
        count = queryset.count()

        if count == 1:
            message = _('1 organization entry was successfully activated')
        else:
            message = _('{count} organization entries were successfully activated')
            message.format(count=count)  # pylint: disable=no-member

        self.message_user(request, message)

    def deactivate_selected(self, request, queryset):
        """ Deactivate the selected entries. """
        queryset.update(active=False)
        count = queryset.count()

        if count == 1:
            message = _('1 organization entry was successfully deactivated')
        else:
            message = _('{count} organization entries were successfully deactivated')
            message.format(count=count)  # pylint: disable=no-member

        self.message_user(request, message)

    deactivate_selected.short_description = _('Deactivate selected entries')
    activate_selected.short_description = _('Activate selected entries')


@admin.register(OrganizationCourse)
class OrganizationCourseAdmin(admin.ModelAdmin):
    """ Admin for the CourseOrganization model. """
    list_display = ('course_id', 'organization', 'active')
    ordering = ('course_id', 'organization__name',)
    search_fields = ('course_id', 'organization__name', 'organization__short_name',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Only display active Organizations.
        if db_field.name == 'organization':
            kwargs['queryset'] = Organization.objects.filter(active=True).order_by('name')

        return super(OrganizationCourseAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(UserOrganizationMapping)
class UserOrganizationMappingAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'username',
        'organization_name',
        'is_active',
        'is_amc_admin',
    ]

    search_fields = [
        'user__email',
        'user__username',
        'organization__name',
        'organization__short_name',
    ]

    list_filter = [
        'is_active',
        'is_amc_admin',
    ]

    def email(self, mapping):
        return mapping.user.email

    def username(self, mapping):
        return mapping.user.username

    def organization_name(self, mapping):
        return mapping.organization.short_name
