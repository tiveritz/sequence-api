from django.contrib import admin


from .models import HowTo, HowToUriId, Step, StepUriId, HowToStep, Super

admin.site.register(HowTo)
admin.site.register(HowToUriId)
admin.site.register(Step)
admin.site.register(StepUriId)
admin.site.register(HowToStep)
admin.site.register(Super)