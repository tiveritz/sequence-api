from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views



urlpatterns = [
    path('', views.APIRoot.as_view(), name = 'root'),
    path('statistics/', views.StatisticView.as_view(), name = 'statistics'),
    path('howtos/', views.HowToListView.as_view(), name = 'how-to-list'),
    path('howtos/<str:uri_id>/', views.HowToDetailView.as_view(), name = 'how-to-detail'),
    path('howtos/<str:uri_id>/steps', views.HowToStepView.as_view(), name = 'how-to-step'),
    path('steps/', views.StepListView.as_view(), name = 'step-list'),
    path('steps/<str:uri_id>/', views.StepDetailView.as_view(), name = 'step-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)