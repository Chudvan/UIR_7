from django.urls import path
from .views import api_pumps, api_petrols, SessionView, \
    OrderOtherView, OrderPetrolView, ScanView

urlpatterns = [
    path('pumps/', api_pumps),
    path('petrols/', api_petrols),
    path('session/', SessionView.as_view()),
    path('orderother/', OrderOtherView.as_view()),
    path('orderpetrol/', OrderPetrolView.as_view()),
    path('scan/', ScanView.as_view()),
]
