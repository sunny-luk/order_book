from django.test import TestCase

from .models import *

# Create your tests here.


def create_order(order_id: str, side: Side, price: float, quantity: int):
    """helper function to create (and save) an order to database"""
    return Order.create_order(order_id=order_id, side=side, price=price, quantity=quantity)


def create_level(price: float, side: Side):
    """helper function to create (and save) and level to database"""
    return Level.create_level(price, side)


class BaseTestCase(TestCase):
    pass


class TestOrderModel(BaseTestCase):

    def test_order_create_and_fill(self):
        o = create_order("K00001", Side.sell, 12.3, 100)
        o.save()
        self.assertEqual(o.filled, False)

        o.fill(20, 11)
        self.assertEqual(o.leave_qty, 80)
        self.assertEqual(o.status, OrderStatus.partial_fill.value)

        o.fill(80, 11.4)
        self.assertEqual(o.leave_qty, 0)
        self.assertEqual(o.status, OrderStatus.filled.value)


class TestLevelModel(BaseTestCase):

    def test_level_add_exception_px(self):
        lv = Level.create_level(12.3, Side.sell)
        order = Order.create_order("K00001", Side.sell, 12.4, 100)
        with self.assertRaises(Exception) as e_info:
            lv.add(order)
            assert (e_info == 0)

    def test_level_add_exception_side(self):
        lv = Level.create_level(12.3, Side.buy)
        order = Order.create_order("K00001", Side.sell, 12.3, 100)
        with self.assertRaises(Exception) as e_info:
            lv.add(order)
            self.assertEqual(e_info, 0)

    def test_level_add(self):
        lv = Level.create_level(12.3, Side.sell)
        order = Order.create_order("K00001", Side.sell, 12.3, 100)
        lv.add(order)
        self.assertEqual(lv.orders.active_orders().count(), 1)

    def test_match_buy(self):
        lv = Level.create_level(12.3, Side.buy)
        o1 = create_order("K00001", Side.buy, 12.3, 40)
        o2 = create_order("K00002", Side.sell, 12.2, 100)
        lv.add(o1)
        self.assertTrue(lv.can_match(o2))
        lv.match(o2)
        self.assertEqual(len(lv.orders.active_orders()),  0)
        self.assertEqual(o2.status, OrderStatus.partial_fill.value)
        self.assertEqual(o2.leave_qty, 60)

    def test_match_sell(self):
        lv = Level.create_level(12.3, Side.sell)
        o1 = Order.create_order("K00001", Side.sell, 12.3, 40)
        o2 = Order.create_order("K00002", Side.buy, 12.8, 100)

        lv.add(o1)
        self.assertTrue(lv.can_match(o2))

        lv.match(o2)
        self.assertEqual(len(lv.orders.active_orders()), 0)
        self.assertEqual(o2.status, OrderStatus.partial_fill.value)
        self.assertEqual(o2.leave_qty, 60)

    def test_no_match_buy(self):
        lv = Level.create_level(12.3, Side.buy)
        o1 = Order.create_order("K00001", Side.buy, 12.3, 40)
        o2 = Order.create_order("K00002", Side.sell, 12.5, 100)

        lv.add(o1)
        self.assertFalse(lv.can_match(o2))

    def test_no_match_sell(self):
        lv = Level.create_level(12.3, Side.sell)
        o1 = Order.create_order("K00001", Side.sell, 12.3, 40)
        o2 = Order.create_order("K00002", Side.buy, 12.2, 100)

        lv.add(o1)
        self.assertFalse(lv.can_match(o2))


class TestOrderBook(BaseTestCase):

    def test_cancel(self):
        o = Order.create_order('00010', Side.sell, 12.3, 40)
        ob = OrderBook.objects.create(side=Side.sell.value)
        ob.add(o)
        lv = Level.objects.get(side=Side.sell.value, price=o.price)
        self.assertEqual(o.level, lv)
        ob.cancel(o)
        self.assertEqual(o.level, None)
        self.assertTrue(o.status, OrderStatus.cancelled.value)

    # def test_cancel_partial_fill(self):
    #     orders = []
    #     orders.append(Order.create_order('0', Side.sell, 12.3, 40))        # 0
    #     orders.append(Order.create_order('1', Side.sell, 12.3, 40))        # 1
    #     orders.append(Order.create_order('2', Side.sell, 12.4, 40))        # 2
    #     orders.append(Order.create_order('3', Side.sell, 12.5, 40))        # 3
    #     orders.append(Order.create_order('4', Side.buy, 12.3, 20))         # 4, 0 partial filled
    #                                              # 5, cancel 0
    #     orders.append(Order.create_order(Order(self.next_id(), Side.buy, 12.5, 20))         # 6, 1 partial filled
    #
    #     engine = Engine()
    #     for action in a:
    #         engine.process(action)
    #
    #     assert(a[0].leave_qty == 0)
    #     assert(a[0].status == OrderStatus.cancelled)
    #     assert(a[0].avg_fill_price == 12.3)
    #     assert(a[0].acum_amount == 12.3 * 20)
    #
    #     assert(a[1].leave_qty == 20)
    #     assert(a[1].status == OrderStatus.partial_fill)
    #     assert(a[1].avg_fill_price == 12.3)
    #     assert(a[1].acum_amount == 12.3 * 20)
    #
    #     assert(a[4].leave_qty == 0)
    #     assert(a[4].status == OrderStatus.filled)
    #
    #     assert(a[6].leave_qty == 0)
    #     assert(a[6].status == OrderStatus.filled)

# class TestFull:
#     def next_id(self):
#         self._id += 1
#         return self._id
#
#     def reset_id(self):
#         self._id = -1
#
#     def test_cancel(self):
#         self.reset_id()
#         a = []
#         a.append(Order(0, Side.sell, 12.3, 40))
#         a.append(Cancel(0))
#
#         engine = Engine()
#         for act in a:
#             engine.process(act)
#
#         assert (a[0].status == OrderStatus.cancelled)
#
#     def test_cancel_partial_fill(self):
#         self.reset_id()
#         a = []
#         a.append(Order(self.next_id(), Side.sell, 12.3, 40))  # 0
#         a.append(Order(self.next_id(), Side.sell, 12.3, 40))  # 1
#         a.append(Order(self.next_id(), Side.sell, 12.4, 40))  # 2
#         a.append(Order(self.next_id(), Side.sell, 12.5, 40))  # 3
#         a.append(Order(self.next_id(), Side.buy, 12.3, 20))  # 4, 0 partial filled
#         a.append(Cancel(0))  # 5, cancel 0
#         a.append(Order(self.next_id(), Side.buy, 12.5, 20))  # 6, 1 partial filled
#
#         engine = Engine()
#         for action in a:
#             engine.process(action)
#
#         assert (a[0].leave_qty == 0)
#         assert (a[0].status == OrderStatus.cancelled)
#         assert (a[0].avg_fill_price == 12.3)
#         assert (a[0].acum_amount == 12.3 * 20)
#
#         assert (a[1].leave_qty == 20)
#         assert (a[1].status == OrderStatus.partial_fill)
#         assert (a[1].avg_fill_price == 12.3)
#         assert (a[1].acum_amount == 12.3 * 20)
#
#         assert (a[4].leave_qty == 0)
#         assert (a[4].status == OrderStatus.filled)
#
#         assert (a[6].leave_qty == 0)
#         assert (a[6].status == OrderStatus.filled)
#
#     def test_trade_buy(self):
#         self.reset_id()
#         a = []
#         a.append(Order(self.next_id(), Side.sell, 12.3, 40))
#         a.append(Order(self.next_id(), Side.sell, 12.3, 40))
#         a.append(Order(self.next_id(), Side.sell, 12.4, 40))
#         a.append(Order(self.next_id(), Side.sell, 12.5, 40))
#         a.append(Order(self.next_id(), Side.buy, 12.2, 100))
#         a.append(Order(self.next_id(), Side.buy, 12.6, 100))
#
#         engine = Engine()
#         for action in a:
#             engine.process(action)
#
#         assert (a[2].leave_qty == 20)
#         assert (a[4].leave_qty == 100)
#         assert (a[5].leave_qty == 0)
#
#     def test_trade_sell_multilevel(self):
#         self.reset_id()
#         a = []
#         a.append(Order(self.next_id(), Side.sell, 12.3, 40))  # 0
#         a.append(Order(self.next_id(), Side.sell, 12.3, 40))  # 1
#         a.append(Order(self.next_id(), Side.sell, 12.4, 40))  # 2
#         a.append(Order(self.next_id(), Side.sell, 12.5, 40))  # 3
#         a.append(Order(self.next_id(), Side.buy, 12.0, 100))  # 4
#         a.append(Order(self.next_id(), Side.buy, 10.0, 100))  # 5
#         a.append(Order(self.next_id(), Side.sell, 10.0, 150))  # 6
#
#         engine = Engine()
#         for action in a:
#             engine.process(action)
#
#         assert (a[4].leave_qty == 0)
#         assert (a[4].status == OrderStatus.filled)
#         assert (a[4].avg_fill_price == 12.0)
#
#         assert (a[5].leave_qty == 50)
#         assert (a[5].status == OrderStatus.partial_fill)
#         assert (a[5].avg_fill_price == 10.0)
#
#         assert (a[6].leave_qty == 0)
#         assert (a[6].avg_fill_price == pytest.approx(11.333333))
#
#     def test_trade_buy_two(self):
#         self.reset_id()
#         a = []
#         a.append(Order(self.next_id(), Side.sell, 12.3, 40))  # 0
#         a.append(Order(self.next_id(), Side.sell, 12.3, 40))  # 1
#         a.append(Order(self.next_id(), Side.sell, 12.4, 40))  # 2
#         a.append(Order(self.next_id(), Side.sell, 12.5, 40))  # 3
#         a.append(Order(self.next_id(), Side.buy, 12.0, 100))  # 4
#         a.append(Order(self.next_id(), Side.buy, 10.0, 100))  # 5
#         a.append(Order(self.next_id(), Side.buy, 12.4, 80))  # 6
#
#         engine = Engine()
#         for action in a:
#             engine.process(action)
#
#         assert (a[0].leave_qty == 0)
#         assert (a[0].status == OrderStatus.filled)
#         assert (a[0].avg_fill_price == 12.3)
#
#         assert (a[1].leave_qty == 0)
#         assert (a[1].status == OrderStatus.filled)
#         assert (a[1].avg_fill_price == 12.3)
#
#         assert (a[6].leave_qty == 0)
#         assert (a[6].status == OrderStatus.filled)
#         assert (a[6].avg_fill_price == 12.3)
#
