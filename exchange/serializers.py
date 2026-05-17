from rest_framework import serializers
from .models import (
    User, PaymentMethod, Item, Tag, ItemTag,
    Proposal, Transaction, Review, Notification
)
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'username', 'password', 'password_confirm',
            'full_name', 'city', 'state', 'country', 'zip_code', 'bio',
            'profile_picture_url', 'average_rating', 'date_joined',
            'terms_agreed', 'is_staff', 'is_active',
        ]
        extra_kwargs = {
            'user_id': {'read_only': True},
            'average_rating': {'read_only': True},
            'date_joined': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
            'email': {'required': True},
            'username': {'required': True},
        }

    def get_full_name(self, obj):
        return obj.get_full_name()
    def get_profile_picture_url(self, obj):
        if not obj.profile_picture:
            return None
        request = self.context.get('request')
        url = obj.profile_picture.url
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

class PaymentMethodSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = PaymentMethod
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Item
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ItemTagSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

    class Meta:
        model = ItemTag
        fields = '__all__'

class ProposalSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    class Meta:
        model = Proposal
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    proposal = serializers.PrimaryKeyRelatedField(queryset=Proposal.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    reviewee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    transaction = serializers.PrimaryKeyRelatedField(queryset=Transaction.objects.all())

    class Meta:
        model = Review
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Notification
        fields = '__all__'