"""Django admin customization"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin page for user"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = ((None, {
        'fields': (
            'email',
            'password',
        ),
    }),
        (
        _('permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }
    ), (
        _('important dates'), {
            'fields': (
                'last_login',
            ),
        }
    ),
    )

    readonly_fields = ['last_login']

    add_fieldsets = (
        (None,

         {
             'classes': ('wide',),
             'fields': (
                 'email',
                 'password1',
                 'password2',
                 'name',
                 'is_active',
                 'is_staff',
                 'is_superuser',
             ),
         }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Stream)
admin.site.register(models.Movie)
admin.site.register(models.Review)