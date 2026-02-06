from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('pedido/novo/', views.novo_pedido, name='novo_pedido'),
    path('pedido/<int:pedido_id>/', views.pedido_detalhe, name='pedido_detalhe'),
    path('pedido/<int:pedido_id>/finalizar', views.pedido_finalizar, name='pedido_finalizar'),
    path('pedido/<int:pedido_id>/produtos/<str:tipo>/', views.listar_produtos, name='listar_produtos'),
    path('pedido/<int:pedido_id>/produto/<int:produto_id>/variacao', views.escolher_variacao, name='escolher_variacao'),
    path('item/<int:item_id>/editar/', views.item_pedido_editar, name='item_pedido_editar'),
    path('item/<int:item_id>/remover/', views.item_pedido_remover, name='item_pedido_remover'),
]