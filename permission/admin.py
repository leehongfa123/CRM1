from django.contrib import admin

# Register your models here.
from permission.models import Role, Permission
admin.site.register(Role)
admin.site.register(Permission)
