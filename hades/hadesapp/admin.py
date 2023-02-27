from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import *
from .forms import UpdateCustomUserForm, CreateCustomUserForm


# Register your models here.

class CustomUserAdmin(DjangoUserAdmin):
    add_form = CreateCustomUserForm
    form = UpdateCustomUserForm
    model = CustomUser
    list_display = ["email", "username"]
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            'Additional information',
            {
                'fields': (
                    'date_of_birth',
                    'gender',
                    'about_me',
                    'followers',
                    'profile_pic',
                ),
            },
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
         ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Developer)
admin.site.register(Game)
admin.site.register(Genre)
admin.site.register(GameAttachments)
