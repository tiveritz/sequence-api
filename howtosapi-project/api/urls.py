from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views



urlpatterns = [
    path('', views.APIRoot.as_view(), name = 'root'),
    path('statistics/', views.StatisticView.as_view(), name = 'statistics'),
    path('howtos/', views.HowToListView.as_view(), name = 'how-to-list'),
    path('howtos/<str:uri_id>/', views.HowToDetailView.as_view(), name = 'how-to-detail'),
    path('howtos/<str:uri_id>/steps', views.HowToStepView.as_view(), name = 'how-to-step'),
    path('howtos/<str:uri_id>/steps/<str:step_uri_id>/', views.HowToStepDetailView.as_view(), name = 'how-to-step-detail'),
    path('howtos/<str:uri_id>/linkable/', views.HowToLinkableView.as_view(), name = 'how-to-linkable'),
    path('steps/', views.StepListView.as_view(), name = 'step-list'),
    path('steps/<str:uri_id>/', views.StepDetailView.as_view(), name = 'step-detail'),
    path('steps/<str:uri_id>/steps', views.SubstepView.as_view(), name = 'sub-step'),
    path('steps/<str:uri_id>/steps/<str:step_uri_id>/', views.SuperDetailView.as_view(), name = 'super-detail'),
    path('steps/<str:uri_id>/linkable/', views.StepLinkableView.as_view(), name = 'step-linkable'),

    path('explanation/', views.ExplanationView.as_view(), name = 'explanation'),
    path('explanation/<str:uri_id>/', views.ExplanationDetailView.as_view(), name = 'explanation-detail'),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)