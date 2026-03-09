from rest_framework import serializers
from .models import Transaction, SavingsGoal, CategoryBudget, Subscription

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


# --- YENİ EKLENEN SERIALIZER'LAR ---

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