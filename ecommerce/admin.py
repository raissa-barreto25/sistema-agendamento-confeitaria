from django.contrib import admin
from .models import Cliente, Categoria, Pedido, Produto, ItemPedido, VariacaoProduto, Sabor, ItemPedidoDoce, ItemPedidoSalgado

admin.site.register(Cliente)
admin.site.register(Categoria)
admin.site.register(Pedido)
admin.site.register(Produto)
admin.site.register(ItemPedido)
admin.site.register(VariacaoProduto)
admin.site.register(Sabor)
admin.site.register(ItemPedidoDoce)
admin.site.register(ItemPedidoSalgado)