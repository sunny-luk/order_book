import decimal
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from ..models import Side, OrderBook, Level, Order, OrderStatus


client = APIClient()


class TestCreateOrderView(APITestCase):

    def test_process_order(self):
        order = {
            'order_id': 'K00001',
            'side': Side.buy.value,
            'price': 12.34,
            'quantity': 50
        }
        response = client.post(reverse('create_order'), data=json.dumps(order), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], 'order accepted')

        ob = OrderBook.objects.get(side=Side.buy.value)
        self.assertTrue(ob.id)
        lv = Level.objects.get(side=Side.buy.value, price=order['price'])
        self.assertTrue(lv.id)
        self.assertFalse(lv.empty())
        o = lv.orders.active_orders().first()
        self.assertTrue(o.id)
        self.assertEqual(o.quantity, 50)
        self.assertAlmostEqual(o.price, decimal.Decimal(order['price']))


class TestCancelOrderView(APITestCase):

    def test_cancel_non_existing_order(self):
        response = client.post(reverse('cancel_order', kwargs={'order_id': 'something_wrong'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['msg'], 'cannot cancel order that does not exist')

    def test_cancel_final_order(self):
        o = Order.create_order('12345', price=12.345, quantity=500, side=Side.buy)
        o.status = OrderStatus.filled.value
        o.save()
        self.assertTrue(o.final)
        response = client.post(reverse('cancel_order', kwargs={'order_id': '12345'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['msg'], 'order is done, cannot cancel')