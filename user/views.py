from rest_framework import generics, permissions, authentication, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserCreationSerializer, UserSerializer, UserUpdateSerializer, PasswordUpdateSerializer, LoginSerializer
from django.contrib.auth import get_user_model


User = get_user_model()

# Verifie que l'utilisateur est un super_user
# -----------------------


class IsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


# Création d'un user (CREATE):
# ----------------------


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    # Tout le monde peut créer un user.
    permission_classes = [permissions.AllowAny]


# Update d'un user (GET/PUT/DELETE):
# -------------------


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]


class UserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    # Token obligatoire
    authentication_classes = [authentication.TokenAuthentication]
    # seuls les users authentifiés peuvent update leur profil.
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # retourne le user connecté.


# Update Spécifique MDP :
# --------------------------

class PasswordUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PasswordUpdateSerializer
    # token obligatoire
    authentication_classes = [authentication.TokenAuthentication]
    # seuls les users authentifiés peuvent update le mdp.
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # retourne le user connecté.

# DeleteUser par superuser :
# =============================


class UserDeleteView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsSuperUser]

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Création d'un Token (connexion) :
# ----------------------------------

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=status.HTTP_200_OK)


# Suppression d'un Token (Déconnexion) :
# ---------------------------------------
# Il ne s'agit pas d'un JWT, sa durée est indéterminée, jusqu'à sa suppression


class LogoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
