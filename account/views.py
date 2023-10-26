from account.serializers import SignUpSerializer
from rest_framework.generics import CreateAPIView


class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
