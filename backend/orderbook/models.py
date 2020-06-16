import decimal
from enum import Enum

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Sum, Prefetch
from django.db.models.signals import post_save

# Create your models here.

channel_layer = get_channel_layer()

epsilon = 0.000001


class BaseModel(models.Model):
    class Meta:
        abstract = True


class Side(Enum):
    buy = 1
    sell = -1

    def opposite(self):
        return Side(self.value * -1)


class OrderStatus(Enum):
    open = 0
    partial_fill = 1
    filled = 2
    cancelled = 3


class MatchResult(Enum):
    error = -1
    complete = 0
    continuation = 1


class OrderManager(models.Manager):

    def active_orders(self):
        """return queryset of new or not fully filled orders"""
        return self.get_queryset().exclude(status__in=[OrderStatus.cancelled.value, OrderStatus.filled.value])


class Order(BaseModel):
    order_id = models.CharField(max_length=255)
    side = models.IntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=10)
    quantity = models.DecimalField(max_digits=30, decimal_places=10)
    leave_qty = models.DecimalField(max_digits=30, decimal_places=10, null=True, blank=True)
    status = models.IntegerField(default=OrderStatus.open.value)
    acum_amount = models.DecimalField(max_digits=30, decimal_places=10, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    avg_fill_price = models.DecimalField(max_digits=30, decimal_places=10, default=0)

    level = models.ForeignKey('Level', null=True, blank=True, related_name='orders', on_delete=models.CASCADE)

    objects = OrderManager()

    @classmethod
    def create_order(cls, order_id: str, side: Side, price: float, quantity: int):
        o = cls(order_id=order_id, side=side.value, price=price, quantity=quantity)
        o.leave_qty = quantity
        o.save()
        return o

    def fill(self, quantity, price):
        if quantity > 0:
            self.acum_amount += decimal.Decimal(quantity) * decimal.Decimal(price)
            self.leave_qty = self.leave_qty - quantity
            acum_qty = self.quantity - self.leave_qty
            self.avg_fill_price = self.acum_amount / acum_qty

            if abs(self.leave_qty) < epsilon:
                self.status = OrderStatus.filled.value
                self.leave_qty = 0
            else:
                self.status = OrderStatus.partial_fill.value
            self.save()

    @property
    def filled(self):
        return self.status == OrderStatus.filled

    @property
    def final(self):
        return self.status == OrderStatus.cancelled.value or self.status == OrderStatus.filled.value

    class Meta:
        ordering = ['price', 'timestamp']


class LevelManager(models.Manager):

    def ordered_levels(self, side: Side):
        if side == Side.buy:
            return self.get_queryset().order_by('-price')
        elif side == Side.sell:
            return self.get_queryset().order_by('price')


class Level(models.Model):
    price = models.DecimalField(max_digits=30, decimal_places=10)
    side = models.IntegerField()

    book = models.ForeignKey('OrderBook', null=True, blank=True, related_name='levels', on_delete=models.CASCADE)
    objects = LevelManager()

    @classmethod
    def create_level(cls, price: float, side: Side):
        lv = cls(price=price, side=side.value)
        lv.save()
        return lv

    @property
    def quantity(self):
        return self.orders.active_orders().all().aggregate(Sum('leave_qty'))['leave_qty__sum']

    def can_match(self, order: Order):
        # Try to match with the best price of the opposite orderbook
        assert (self.side * order.side == -1)  # must be different side
        return order.price * order.side >= self.price * order.side

    def match(self, o_taker: Order):
        orders = self.orders.active_orders()
        for o_maker in orders:
            matched_qty = min(o_taker.leave_qty, o_maker.leave_qty)
            o_taker.fill(matched_qty, self.price)
            o_maker.fill(matched_qty, self.price)

            if o_taker.filled:
                # matching completed
                return MatchResult.complete
        return MatchResult.continuation

    def add(self, order: Order):
        assert (order.price == self.price)
        assert (order.side == self.side)
        order.level = self
        order.save()
        self.save()

    def cancel(self, order: Order):
        order.level = None
        order.status = OrderStatus.cancelled.value
        order.leave_qty = 0
        order.save()

    def empty(self):
        return not self.orders.active_orders().exists()


class OrderBook(BaseModel):
    side = models.IntegerField()

    def add(self, order: Order):
        assert(order.filled == False)
        level_qs = self.levels.filter(price=order.price)
        if not level_qs.exists():
            lv = Level.create_level(price=order.price, side=Side(order.side))
            lv.book = self
            lv.save()
        else:
            lv = level_qs.first()
        lv.add(order)

    def match(self, order: Order):
        removed_px = []
        for lv in self.levels.ordered_levels(side=Side(order.side).opposite()):
            if not lv.can_match(order):
                break
            result = lv.match(order)
            if lv.empty():
                removed_px.append(lv.price)
            if result == MatchResult.complete:
                break

    def cancel(self, order: Order):
        lv = self.levels.get(price=order.price)
        lv.cancel(order)

    @classmethod
    def get_levels(cls, side: Side, depth: int=5):
        ob = cls.objects.get_or_create(side=side.value)[0]
        levels = ob.levels.ordered_levels(side=side).prefetch_related(
            Prefetch(
                'orders',
                queryset=Order.objects.exclude(leave_qty=0)
            )
        )
        qs = [lv for lv in levels if lv.empty() is False][:depth]
        from .api.serializers import LevelSerializer
        serializer = LevelSerializer(qs, many=True)
        return serializer.data
