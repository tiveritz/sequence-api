from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from api import views


router = DefaultRouter()
router.register(r'howtos', views.HowToViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/', views.StatisticView.as_view(), name='statistics')
]
