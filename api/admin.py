from django.contrib import admin


from .models import (Sequence, SequenceStep, Step, SuperStep, Explanation,
                     StepModule, DecisionStep, Module, Image, SequenceGuide,
                     SequenceGuideStep,)

admin.site.register(Sequence)
admin.site.register(Step)
admin.site.register(SequenceStep)
admin.site.register(SuperStep)
admin.site.register(DecisionStep)
admin.site.register(Explanation)
admin.site.register(StepModule)
admin.site.register(Module)
admin.site.register(Image)
admin.site.register(SequenceGuide)
admin.site.register(SequenceGuideStep)
