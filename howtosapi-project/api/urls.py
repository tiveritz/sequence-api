from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views



urlpatterns = [
    path('', views.APIRoot.as_view(), name = 'root'),
    path('statistics/', views.StatisticView.as_view(), name = 'statistics'),
    path('howtos/', views.HowToListView.as_view(), name = 'how-to-list'),
    path('howtos/<int:pk>', views.HowToDetailView.as_view(), name = 'how-to-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)