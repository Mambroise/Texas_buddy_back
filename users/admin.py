# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :users/admin.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.user import User
from planners.admin import TripInLine


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.user import User
from planners.admin import TripInLine


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions', 'interests') 
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Informations personnelles',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'phone',
                    'address',
                    'country',
                    'sign_up_number',
                    'interests',  
                )
            }
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_staff',
                    'is_active',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    inlines = [TripInLine]

