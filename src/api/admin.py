from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from api_base.forms import UserAdminChangeForm, UserAdminCreationForm
from api_user.models import Profile, User


class ProfileInLine(admin.TabularInline):
    model = Profile


class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ('email', 'admin')
    list_filter = ('admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )

    inlines = [ProfileInLine]
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
