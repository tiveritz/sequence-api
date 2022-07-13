from django.contrib import admin

from api.models.step import LinkedStep, Step
from api.models.sequence import Sequence


admin.site.register(LinkedStep)
admin.site.register(Sequence)
admin.site.register(Step)
