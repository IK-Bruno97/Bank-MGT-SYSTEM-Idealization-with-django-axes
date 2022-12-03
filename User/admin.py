from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):
    model = NewUser
    search_fields = ('email', 'phone', 'first_name',)
    list_filter = ('email', 'phone', 'first_name', 'is_active', 'is_staff')
    ordering = ('-start_date',)
    list_display = ('email', 'phone', 'first_name',
                    'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'first_name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'first_name', 'password1', 'password2', 'is_active', 'is_staff')}
         ),
    )



admin.site.register(AccountBalance)
admin.site.register(Transfer)
admin.site.register(Deposit)
admin.site.register(NewUser, UserAdminConfig)

