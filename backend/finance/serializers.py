from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model
from .models import Transaction, SavingsGoal, CategoryBudget, Subscription

User = get_user_model()

# --- 🚀 YENİ: DJOSER İÇİN ÖZEL KULLANICI SERIALIZER'LARI ---

# 1. Kayıt Olurken (Register) Ad ve Soyadı kabul etmesi için
class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')

# 2. Profil güncellerken ve veri çekerken Ad ve Soyadı vermesi için
class CustomUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


# --- MEVCUT SENİN SERIALIZER'LARIN ---

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'title',
            'amount',
            'transaction_type',
            'date',
            'category',
            'description',
        ]
    
    def create(self, validated_data):
        # İşlemi yapan kullanıcıyı otomatik olarak ata
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = ['id', 'title', 'target_amount', 'current_amount', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # İşlemi yapan kullanıcıyı otomatik olarak ata
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CategoryBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryBudget
        fields = ['id', 'category', 'limit_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Bütçeyi oluşturan kullanıcıyı otomatik olarak ata
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'id', 
            'name', 
            'amount', 
            'due_date', 
            'icon', 
            'color_class', 
            'is_active', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Aboneliği ekleyen kullanıcıyı otomatik olarak ata
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)