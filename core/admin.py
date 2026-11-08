from django.contrib import admin
from .models import Domaine, Controle, Evaluation, Risque

admin.site.register(Domaine)
admin.site.register(Controle)
admin.site.register(Evaluation)
admin.site.register(Risque)