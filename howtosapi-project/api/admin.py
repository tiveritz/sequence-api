from django.contrib import admin


from .models import (HowTo,
                     HowToUriId,
                     Step,
                     StepUriId,
                     HowToStep,
                     Super,
                     Explanation,
                     ExplanationUriId,
                     StepExplanation,
                     Image)

admin.site.register(HowTo)
admin.site.register(HowToUriId)
admin.site.register(Step)
admin.site.register(StepUriId)
admin.site.register(HowToStep)
admin.site.register(Super)
admin.site.register(Explanation)
admin.site.register(ExplanationUriId)
admin.site.register(StepExplanation)
admin.site.register(Image)
