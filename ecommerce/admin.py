from django.contrib import admin
from .models import Cliente, Categoria, Pedido, Produto, ItemPedido, VariacaoProduto, Sabor

admin.site.register(Cliente)
admin.site.register(Categoria)
admin.site.register(Pedido)
admin.site.register(Produto)
admin.site.register(ItemPedido)
admin.site.register(VariacaoProduto)
admin.site.register(Sabor)