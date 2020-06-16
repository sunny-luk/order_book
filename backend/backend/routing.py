from channels.routing import ProtocolTypeRouter

from orderbook.consumers import OrderbookConsumer

application = ProtocolTypeRouter({
    'websocket': OrderbookConsumer
})