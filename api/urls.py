from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (api_root, general_views, howto_views, step_views,
                    explanation_views, media_views, guide_views,)


urlpatterns = [
    # API root
    path('', api_root.APIRoot.as_view(), name='root'),
    
    # General Views
    path('statistics/', general_views.StatisticView.as_view(), name='statistics'),
    
    # How To Views
    path('howtos/', howto_views.HowToListView.as_view(), name='how-to-list'),
    path('howtos/<str:uri_id>/', howto_views.HowToDetailView.as_view(), name='how-to-detail'),
    path('howtos/<str:uri_id>/steps/', howto_views.HowToStepView.as_view(), name='how-to-step'),
    path('howtos/<str:uri_id>/steps/<str:step_uri_id>/', howto_views.HowToStepDetailView.as_view(), name='how-to-step-detail'),
    path('howtos/<str:uri_id>/linkable/', howto_views.HowToLinkableView.as_view(), name='how-to-linkable'),
    path('howtos/<str:uri_id>/publish/', howto_views.HowToPublishView.as_view(), name='how-to-publish'),
    
    # Step Views
    path('steps/', step_views.StepListView.as_view(), name='step-list'),
    path('steps/<str:uri_id>/', step_views.StepDetailView.as_view(), name='step-detail'),
    path('steps/<str:uri_id>/steps/', step_views.SubstepView.as_view(), name='sub-step'),
    path('steps/<str:uri_id>/modules/', step_views.StepModuleView.as_view(), name='step-module'),
    path('steps/<str:uri_id>/steps/<str:step_uri_id>/', step_views.SuperDetailView.as_view(), name='super-detail'),
    path('steps/<str:uri_id>/linkable/', step_views.StepLinkableView.as_view(), name='step-linkable'),
    path('steps/<str:uri_id>/linkablemodules/', step_views.StepLinkableModulesView.as_view(), name='step-linkable-modules'),
    path('steps/<str:uri_id>/linkableimages/', step_views.StepLinkableImagesView.as_view(), name='step-linkable-images'),

    # Explanation Views
    path('explanation/', explanation_views.ExplanationView.as_view(), name='explanation'),
    path('explanation/<str:uri_id>/', explanation_views.ExplanationDetailView.as_view(), name='explanation-detail'),

    # Guide Views
    path('guides/howtos/<str:space>/', guide_views.HowToGuideListView.as_view(), name='howto-guide-list'),
    path('guides/howto/step/', guide_views.StepGuideListView.as_view(), name='step-guide-list'),
    path('guides/howto/<str:uri_id>/<str:space>/', guide_views.HowToGuideView.as_view(), name='howto-guide'),
    path('guides/howto/<str:howto_uri_id>/<str:step_uri_id>/<str:ref_id>/', guide_views.StepGuideView.as_view(), name='step-guide'),

    # Media Views
    path('media/images/', media_views.ImageView.as_view(), name='images'),
    path('media/images/<str:uri_id>', media_views.ImageDetailView.as_view(), name='image-detail'),
    path('media/<str:uri_id>.<str:media_type>/', media_views.ImageRenderView.as_view(), name='images-render'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
