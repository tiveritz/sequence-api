from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from api.views.api_root import APIRoot
from api.views.general_views import StatisticView
from api.views.sequence_views import SequenceListView, SequenceView
from api.views.step_views import (StepListView,
                                  StepView,
                                  StepLinkableListView,
                                  SubstepAddView,
                                  SubstepDeleteView,
                                  SubstepOrderView,
                                  StepUsageView)


app_name = 'api'
urlpatterns = [
    path('',
         APIRoot.as_view(),
         name='root'),

    path('sequences/',
         SequenceListView.as_view(),
         name='sequence-list'),
    path('sequences/<uuid:uuid>/',
         SequenceView.as_view(),
         name='sequence'),

    path('steps/',
         StepListView.as_view(),
         name='step-list'),
    path('steps/<uuid:uuid>/',
         StepView.as_view(),
         name='step'),
    path('steps/<uuid:uuid>/linkable/',
         StepLinkableListView.as_view(),
         name='step-linkable'),
    path('steps/<uuid:uuid>/steps/add/',
         SubstepAddView.as_view(),
         name='step-add'),
    path('steps/<uuid:uuid>/steps/order/',
         SubstepOrderView.as_view(),
         name='step-order'),
    path('steps/<uuid:uuid>/steps/delete/',
         SubstepDeleteView.as_view(),
         name='step-delete'),
    path('steps/<uuid:uuid>/usage/',
         StepUsageView.as_view(),
         name='step-usage'),

    path('statistics/',
         StatisticView.as_view(),
         name='statistics')]

urlpatterns = format_suffix_patterns(urlpatterns)
