from django.contrib import admin

from .models import GameScore, EnterWords, CurrentSession

admin.site.register(GameScore)
admin.site.register(EnterWords)
admin.site.register(CurrentSession)
