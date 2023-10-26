from django.urls import path
from rest_framework import routers
from wallet.views import DepositView


router = routers.DefaultRouter()

urlpatterns = router.urls + [
    path('deposit/', DepositView.as_view(), name='deposit'),
]
