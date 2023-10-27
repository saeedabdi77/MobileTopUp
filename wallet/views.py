from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from wallet.serializers import DepositSerializer, TopUpSerializer


class DepositView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DepositSerializer


class TopUpView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TopUpSerializer
