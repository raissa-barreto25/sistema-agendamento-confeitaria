from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, Cliente, Pedido, Produto, ItemPedido, VariacaoProduto


def home(request):
    return render(request, 'home.html')

def novo_pedido(request):
    pedido = Pedido.objects.create()
    return redirect('pedido_servico', pedido_id=pedido.id)

def pedido_servico(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    tipos = [('KIT', 'kit festa'), ('BOLO', 'bolo'), ('DOCES', 'doces'), ('SALGADOS', 'salgados'), ('CUPCAKE', 'cupcake'), ('CASEIRINHO', 'Caseirinho')]

    if request.method == "POST":
        tipo = request.POST.get('tipo')
        pedido.servico = tipo
        pedido.save(update_fields=['servico'])
        return redirect('listar_produtos', pedido_id=pedido.id, tipo=tipo)
    return render (request, 'pedido/servico.html', {'pedido':pedido, 'tipos': tipos})

def listar_produtos(request, pedido_id, tipo):
    pedido =get_object_or_404(Pedido, id=pedido_id)
    produtos = Produto.objects.filter(tipo=tipo)

    return render (request, 'pedido/listar_produtos.html', {'pedido': pedido, 'produtos':produtos})

def escolher_variacao(request, produto_id, pedido_id):
    produto = get_object_or_404(Produto, id=produto_id)
    pedido = get_object_or_404 (Pedido, id=pedido_id)
    variacoes = produto.variacoes.all()

    if request.method == "POST":
        variacao_id = request.POST.get('variacao')
        quantidade = int(request.POST.get('quantidade', 1))
        variacao = get_object_or_404(VariacaoProduto, id=variacao_id)

        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            variacao=variacao,
            quantidade=quantidade
        )
        return  redirect('pedido_personalizado', pedido_id=pedido.id)
    return render (request, 'pedido/escolher_variacao.html', {
        'pedido':pedido,
        'produto': produto,
        'variacoes': variacoes
    })