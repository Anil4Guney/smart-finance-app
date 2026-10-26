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
    """Recurring income/expense plan (salary, rent, bills, subscriptions, installments)."""
    remaining_installments = serializers.IntegerField(read_only=True)
    effective_category = serializers.CharField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id',
            'name',
            'amount',
            'transaction_type',
            'kind',
            'category',
            'effective_category',
            'due_date',
            'total_installments',
            'installments_paid',
            'remaining_installments',
            'icon',
            'color_class',
            'is_active',
            'auto_pay',
            'last_billed_date',
            'created_at'
        ]
        read_only_fields = ['id', 'installments_paid', 'last_billed_date', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def validate(self, attrs):
        kind = attrs.get('kind', getattr(self.instance, 'kind', Subscription.Kind.SUBSCRIPTION))
        total = attrs.get('total_installments', getattr(self.instance, 'total_installments', None))
        if kind == Subscription.Kind.INSTALLMENT:
            if not total or not 1 <= total <= 120:
                raise serializers.ValidationError(
                    {'total_installments': 'Installment plans need between 1 and 120 payments.'}
                )
            paid = getattr(self.instance, 'installments_paid', 0)
            if total < paid:
                raise serializers.ValidationError(
                    {'total_installments': f'{paid} installments are already paid.'}
                )
        else:
            attrs['total_installments'] = None
        if kind == Subscription.Kind.SALARY:
            attrs['transaction_type'] = Transaction.TransactionType.INCOME
        elif kind in (Subscription.Kind.RENT, Subscription.Kind.BILL,
                      Subscription.Kind.SUBSCRIPTION, Subscription.Kind.INSTALLMENT):
            # Rent is treated as an expense (the user pays it)
            attrs['transaction_type'] = Transaction.TransactionType.EXPENSE
        return attrs

    def create(self, validated_data):
        # Planı ekleyen kullanıcıyı otomatik olarak ata
        validated_data['user'] = self.context['request'].user
        validated_data['billing_day'] = validated_data['due_date'].day
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Kullanıcı ödeme tarihini değiştirirse fatura günü de onu takip eder
        if 'due_date' in validated_data:
            validated_data['billing_day'] = validated_data['due_date'].day
        # Raising the number of installments re-opens a finished plan
        total = validated_data.get('total_installments', instance.total_installments)
        if total and total > instance.installments_paid and 'total_installments' in validated_data:
            validated_data.setdefault('is_active', True)
        return super().update(instance, validated_data)
