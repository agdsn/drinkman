from django.contrib import admin

from . import models

admin.site.register(models.Item)
admin.site.register(models.User)
admin.site.register(models.Transaction)
admin.site.register(models.Stock)
admin.site.register(models.Location)
