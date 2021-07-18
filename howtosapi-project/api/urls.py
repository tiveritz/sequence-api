from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (api_root, general_views, howto_views, step_views,
                    explanation_views)


urlpatterns = [
    # API root
    path('',
         api_root.APIRoot.as_view(),
         name = 'root'),
    
    # General Views
    path('statistics/',
         general_views.StatisticView.as_view(),
         name = 'statistics'),
    
    # How To Views
    path('howtos/',
         howto_views.HowToListView.as_view(),
         name = 'how-to-list'),
    path('howtos/<str:uri_id>/',
         howto_views.HowToDetailView.as_view(),
         name = 'how-to-detail'),
    path('howtos/<str:uri_id>/steps/',
         howto_views.HowToStepView.as_view(),
         name = 'how-to-step'),
    path('howtos/<str:uri_id>/steps/<str:step_uri_id>/',
         howto_views.HowToStepDetailView.as_view(),
         name = 'how-to-step-detail'),
    path('howtos/<str:uri_id>/linkable/',
         howto_views.HowToLinkableView.as_view(),
         name = 'how-to-linkable'),
    
    # Step Views
    path('steps/',
         step_views.StepListView.as_view(),
         name = 'step-list'),
    path('steps/<str:uri_id>/',
         step_views.StepDetailView.as_view(),
         name = 'step-detail'),
    path('steps/<str:uri_id>/steps/',
         step_views.SubstepView.as_view(),
         name = 'sub-step'),
    path('steps/<str:uri_id>/explanations/',
         step_views.StepExplanationView.as_view(),
         name = 'step-explanation'),
    path('steps/<str:uri_id>/steps/<str:step_uri_id>/',
         step_views.SuperDetailView.as_view(),
         name = 'super-detail'),
    path('steps/<str:uri_id>/linkable/',
         step_views.StepLinkableView.as_view(),
         name = 'step-linkable'),
    path('steps/<str:uri_id>/linkablemodules/',
         step_views.StepLinkableModulesView.as_view(),
         name = 'step-linkable-modules'),

    # Explanation Views
    path('explanation/',
         explanation_views.ExplanationView.as_view(),
         name = 'explanation'),
    path('explanation/<str:uri_id>/',
         explanation_views.ExplanationDetailView.as_view(),
         name = 'explanation-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

'''
    path('explanation/text/',
         explanation_views.ExplanationView.as_view(),
         name = 'explanation-text'
         ),
    path('explanation/code/',
         explanation_views.ExplanationView.as_view(),
         name = 'explanation-code'
         ),
'''