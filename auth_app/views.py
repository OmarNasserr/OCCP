from rest_framework.decorators import api_view
from rest_framework.response import Response
from .jwt import CustomTokenObtainPairSerializer
from .serializers import RegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


@api_view(['Post', ])
def registration_view(request):
    if request.method == 'POST':

        serializer = RegistrationSerializer(data=request.data)

        data = {}
        serializer.is_valid(raise_exception=True)

        account = serializer.save(serializer.validated_data)

        data['message'] = 'Registration Successful.'
        data['username'] = account.username

        # JWT token
        refresh = CustomTokenObtainPairSerializer.get_token(account)

        data['token'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

        return Response(data, status=201)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user.token_version += 1  # Increment the token version to invalidate old tokens
            user.save()
            return Response(data={
                "message": "Logged out successfully.",
                "status": 200
            }, status=200)
        except Exception as e:
            return Response(data={
                "message": str(e),
                "status": 400
            }, status=400)
