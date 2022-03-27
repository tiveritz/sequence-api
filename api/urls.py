from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (api_root, general_views, sequence_views, step_views,
                    explanation_views, media_views, guide_views,)


urlpatterns = [
    # API root
    path('',
         api_root.APIRoot.as_view(),
         name='root'),

    # General Views
    path('statistics/',
         general_views.StatisticView.as_view(),
         name='statistics'),

    # Sequence Views
    path('sequences/',
         sequence_views.SequenceListView.as_view(),
         name='sequence-list'),
    path('sequences/<str:api_id>/',
         sequence_views.SequenceDetailView.as_view(),
         name='sequence-detail'),
    path('sequences/<str:api_id>/steps/',
         sequence_views.SequenceStepView.as_view(),
         name='sequence-step'),
    path('sequences/<str:api_id>/steps/<str:step_api_id>/',
         sequence_views.SequenceStepDetailView.as_view(),
         name='sequence-step-detail'),
    path('sequences/<str:api_id>/linkable/',
         sequence_views.SequenceLinkableView.as_view(),
         name='sequence-linkable'),
    path('sequences/<str:api_id>/publish/',
         sequence_views.SequencePublishView.as_view(),
         name='sequence-publish'),

    # Step Views
    path('steps/',
         step_views.StepListView.as_view(),
         name='step-list'),
    path('steps/<str:api_id>/',
         step_views.StepDetailView.as_view(),
         name='step-detail'),
    path('steps/<str:api_id>/steps/',
         step_views.SubstepView.as_view(),
         name='sub-step'),
    path('steps/<str:api_id>/modules/',
         step_views.StepModuleView.as_view(),
         name='step-module'),
    path('steps/<str:api_id>/steps/<str:step_api_id>/',
         step_views.SuperDetailView.as_view(),
         name='super-detail'),
    path('steps/<str:api_id>/linkable/',
         step_views.StepLinkableView.as_view(),
         name='step-linkable'),
    path('steps/<str:api_id>/linkablemodules/',
         step_views.StepLinkableModulesView.as_view(),
         name='step-linkable-modules'),
    path('steps/<str:api_id>/linkableimages/',
         step_views.StepLinkableImagesView.as_view(),
         name='step-linkable-images'),

    # Decision Views
    path('steps/<str:api_id>/decisions/',
         step_views.DecisionView.as_view(),
         name='decision-step'),
    path('steps/<str:api_id>/linkable-decisions/',
         step_views.DecisionLinkableView.as_view(),
         name='decision-linkable'),

    # Explanation Views
    path('explanation/',
         explanation_views.ExplanationView.as_view(),
         name='explanation'),
    path('explanation/<str:api_id>/',
         explanation_views.ExplanationDetailView.as_view(),
         name='explanation-detail'),

    # Guide Views
    path('guides/sequences/<str:space>/',
         guide_views.SequenceGuideListView.as_view(),
         name='sequence-guide-list'),
    #path('guides/sequence/step/',
    #     guide_views.StepGuideListView.as_view(),
    #     name='step-guide-list'),
    path('guides/sequence/<str:api_id>/<str:space>/',
         guide_views.SequenceGuideView.as_view(),
         name='sequence-guide'),
    path('guides/sequence/<str:step_api_id>/',
         guide_views.StepGuideView.as_view(),
         name='step-guide'),

    # Media Views
    path('media/images/',
         media_views.ImageView.as_view(),
         name='images'),
    path('media/images/<str:api_id>',
         media_views.ImageDetailView.as_view(),
         name='image-detail'),
    path('media/<str:api_id>.<str:media_type>/',
         media_views.ImageRenderView.as_view(),
         name='images-render'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
