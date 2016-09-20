from django.contrib import admin
import models

admin.site.register(models.Project)
admin.site.register(models.Priority)
admin.site.register(models.TaskStatus)
admin.site.register(models.Phase)
admin.site.register(models.Task)
