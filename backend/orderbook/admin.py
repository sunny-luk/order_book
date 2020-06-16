from django.contrib import admin

from .models import *

# Register your models here.


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'price', 'quantity', 'leave_qty']


@admin.register(Level)
class LevelModelAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderBook)
class OrderBookModelAdmin(admin.ModelAdmin):
    pass