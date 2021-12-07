from django.contrib import admin


from .models import (HowTo,
                     Step,
                     HowToStep,
                     SuperStep,
                     Explanation,
                     StepModule,
                     DecisionStep,
                     Module,
                     Image,
                     HowToGuide,
                     HowToGuideStep,)

admin.site.register(HowTo)
admin.site.register(Step)
admin.site.register(HowToStep)
admin.site.register(SuperStep)
admin.site.register(DecisionStep)
admin.site.register(Explanation)
admin.site.register(StepModule)
admin.site.register(Module)
admin.site.register(Image)
admin.site.register(HowToGuide)
admin.site.register(HowToGuideStep)

