from django.contrib import admin

# Register your models here.
from Bot.models import Client, Site

admin.site.register(Client)
admin.site.register(Site)