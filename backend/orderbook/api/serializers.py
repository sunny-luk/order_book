from rest_framework.serializers import ModelSerializer, SerializerMethodField

from ..models import Level, Order


class OrderSerializer(ModelSerializer):

    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'side',
            'price',
            'quantity',
            'leave_qty',
            'status',
            'acum_amount',
            'timestamp',
            'avg_fill_price'
        ]


class LevelSerializer(ModelSerializer):
    orders = OrderSerializer(many=True)
    quantity = SerializerMethodField()

    def get_quantity(self, obj):
        if obj.quantity:
            return float(obj.quantity)
        else:
            return 0

    class Meta:
        model = Level
        fields = [
            'id',
            'side',
            'price',
            'orders',
            'quantity'
        ]
