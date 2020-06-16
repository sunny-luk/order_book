import decimal
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

from ..models import Order, OrderBook, Side


def refresh_orderbook():
    async_to_sync(channel_layer.group_send)('ob_orderbook', {
        'type': 'refresh_orderbook'
    })


class CreateOrderAPIView(APIView):

    def post(self, request, *args, **kwargs):
        order_data = request.data
        if Order.objects.filter(order_id=order_data['order_id']):
            return Response({'msg': 'duplicated order_id'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        order = Order.create_order(order_data['order_id'], Side(order_data['side']), decimal.Decimal(order_data['price']),
                                   decimal.Decimal(order_data['quantity']))

        my_book = OrderBook.objects.get_or_create(side=order.side)[0]
        op_book = OrderBook.objects.get_or_create(side=Side(order.side).opposite().value)[0]

        op_book.match(order)
        if not order.filled:
            my_book.add(order)

        refresh_orderbook()

        return Response({'msg': 'order accepted'}, status=status.HTTP_200_OK)


class CancelOrderAPIView(APIView):

    def post(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)
        except ObjectDoesNotExist:
            return Response({'msg': 'cannot cancel order that does not exist'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if order.final:
            return Response({'msg': 'order is done, cannot cancel'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        book = OrderBook.objects.get_or_create(side=order.side)[0]
        book.cancel(order)
        refresh_orderbook()
        return Response({'msg': 'order cancelled'}, status=status.HTTP_200_OK)




