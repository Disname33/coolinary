from django.contrib import admin

from .models import Player, Round, Riddle, RoundPlayer

admin.site.register(Player)
admin.site.register(Round)
admin.site.register(Riddle)
admin.site.register(RoundPlayer)
