from django.contrib import admin
from .models import (LinkedStep,
                     Sequence,
                     Step)


admin.site.register(LinkedStep)
admin.site.register(Sequence)
admin.site.register(Step)
