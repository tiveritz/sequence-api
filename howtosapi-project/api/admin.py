from django.contrib import admin


from .models import (HowTo,
                     Step,
                     HowToStep,
                     SuperStep,
                     Explanation,
                     StepModule,
                     Image)

admin.site.register(HowTo)
admin.site.register(Step)
admin.site.register(HowToStep)
admin.site.register(SuperStep)
admin.site.register(Explanation)
admin.site.register(StepModule)
admin.site.register(Image)
