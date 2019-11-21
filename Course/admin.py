from django.contrib import admin

# Register your models here.
from . import models

for model_str in models.__all__:
    model = getattr(models, model_str)
    admin.site.register(model)
