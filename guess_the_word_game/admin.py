from django.contrib import admin

from .models import GameScore, CurrentSession

admin.site.register(GameScore)
admin.site.register(CurrentSession)
