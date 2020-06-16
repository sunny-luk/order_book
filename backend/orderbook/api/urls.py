from django.urls import path
from . import views

urlpatterns = [
    path('create_order/', views.CreateOrderAPIView.as_view(), name='create_order'),
    path('cancel_order/<str:order_id>/', views.CancelOrderAPIView.as_view(), name='cancel_order')
]