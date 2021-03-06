import jwt

from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User
from authors.settings import SECRET_KEY
from authors.apps.profiles.models import Profile

from .backends import JWTAuthentication

from authors.apps.profiles.models import Profile

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.RegexField(
        regex=r"^(?!.*([A-Za-z\d])\1{2})(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,128}$",
        max_length=128,
        min_length=8,
        write_only=True,
        required=True,
        error_messages={
            'max_length': 'Password cannot be more than 128 characters',
            'min_length': 'Password must contain at least 8 characters',
            'required': 'Password is required',
            'invalid': 'Password must contain a number and a letter and that are not repeating more that twice'
        }
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Sorry this Email exists, kindly login',
            )
        ],
        error_messages={
            'required': 'Email is required for registration',
        }
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(max_length=50)
    username = serializers.CharField(max_length=20, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError(
                'A user with this email was not found.'
            )
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'Incorrect password.'
            )

        # payload = jwt_payload_handler(user)
        # token = jwt.encode(payload, settings.SECRET_KEY)

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )
        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': JWTAuthentication.encode_token(self, user.pk)
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=False)
    username = serializers.CharField(required=False)

    def validate(self, data):
        email = data.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError(
                'A user with this email was not found.')
        token = default_token_generator.make_token(user)
        payload = {
            'token': token,
            'email': email,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY).decode('UTF-8')
        return dict(email=email, token=token, username=user.username)


class ResetUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.RegexField(
        regex=r"^(?!.*([A-Za-z\d])\1{2})(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,128}$",
        max_length=128,
        min_length=8,
        write_only=True,
        required=True,
        error_messages={
            'max_length': 'Password cannot be more than 128 characters',
            'min_length': 'Password must contain at least 8 characters',
            'invalid': 'Password must contain a number and a letter and that are not repeating more that two times'
        }
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True)

    def validate(self, data):
        new_password = data.get('new_password', None)
        confirm_password = data.get('confirm_password', None)

        token = self.context.get('token')

        if new_password != confirm_password:
            raise serializers.ValidationError('Passwords don\'t match.')

        payload = jwt.decode(token, SECRET_KEY)
        email = payload['email']
        default_token = payload['token']
        user = User.objects.get(email=email)
        if not (default_token_generator.check_token(user, default_token)):
            raise serializers.ValidationError(
                "You either have an invalid token or the token has expired.")
        user.set_password(new_password)
        user.save()

        return data


class SocialSignInSignOutSerializer(serializers.Serializer):
    """ This classs Jsonifies and validates token from 
        social providers such as facebook, google and twitter
    """
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(
        max_length=1024, required=True, trim_whitespace=True)
    access_token_secret = serializers.CharField(
        max_length=300, allow_null=True, default=None, trim_whitespace=True)
        