from django.contrib.auth import get_user_model, authenticate
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.authtoken.models import Token

# Récupération du modèle CustomUser
User = get_user_model()


# Création d'un User
# ==================

class UserCreationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=5,)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'telephone', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        if 'telephone' in validated_data:
            user.telephone = validated_data['telephone']
            user.save()
        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'telephone': user.telephone if hasattr(user, 'telephone') else None,
        }


#  Get ALL users :
# ==================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name',
                  'telephone', 'profile_image', 'is_premium', 'is_active')

# Update d'un User :
# ====================


class UserUpdateSerializer(serializers.ModelSerializer):
    is_superuser = serializers.BooleanField(read_only=True)
    is_premium = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ("id", 'email', 'first_name', 'last_name',
                  'telephone', 'profile_image', 'is_superuser', 'is_premium')
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        if 'email' in validated_data:
            instance.email = validated_data['email']
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
        if 'telephone' in validated_data:
            instance.telephone = validated_data['telephone']
        # if 'profile_image' in validated_data:
        #     instance.profile_image = validated_data['profile_image']
        if 'profile_image' in validated_data:
            old_image_path = instance.profile_image.name  # change .path to .name
            instance.profile_image = validated_data['profile_image']
            # Si l'ancienne image n'est pas l'image par défaut
            if old_image_path != 'default_images/user.png':  # remove the leading slash
                default_storage.delete(old_image_path)
        instance.save()
        return instance


# Update du mdp d'un user :
# ============================


class PasswordUpdateSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=5)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

# Login => Création d'un AuthToken :
# ===========================


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, data):
        user = authenticate(username=data.get('email'),
                            password=data.get('password'))
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Email/password incorrects.")

    def create(self, validated_data):
        token, created = Token.objects.get_or_create(
            user=validated_data['user'])
        return token
