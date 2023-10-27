from django.urls import path
from rest_framework import routers
from wallet.views import DepositView, TopUpView


router = routers.DefaultRouter()

urlpatterns = router.urls + [
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('topup/', TopUpView.as_view(), name='top_up'),
]
