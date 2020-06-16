# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import OrderBook, Side


class OrderbookConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'orderbook'
        self.room_group_name = 'ob_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        # send initial data to new joiner of the group
        self.send(text_data=json.dumps({
            'type': 'orderbook_data',
            'data': {
                'buy': OrderBook.get_levels(Side.buy),
                'sell': OrderBook.get_levels(Side.sell)
            }
        }))

    def refresh_orderbook(self, event):
        # broadcast message to all group members
        self.send(text_data=json.dumps({
            'type': 'orderbook_data',
            'data': {
                'buy': OrderBook.get_levels(Side.buy),
                'sell': OrderBook.get_levels(Side.sell)
            }
        }))


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # # Receive message from WebSocket
    # def receive(self, text_data):
    #     print(text_data)
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']
    #
    #     # Send message to room group
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             'type': 'order_update',
    #             'message': message
    #         }
    #     )

    def send_data(self, data):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'order_book_data',
                'data': data
            }
        )

    # Receive message from room group
    def order_update(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
