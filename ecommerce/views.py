from django.shortcuts import render, redirect, get_object_or_404
from .forms import PedidoForm, ItemPedidoDoceFormSet, ItemPedidoSalgadoFormSet, ItemPedidoForm
from .models import Categoria, Cliente, Pedido, Produto, ItemPedido, VariacaoProduto, ItemPedidoSalgado, ItemPedidoDoce


def home(request):
    return render(request, 'home.html')

def novo_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.status = 'rascunho'
            pedido.save()
            return redirect('pedido_detalhe', pedido_id=pedido.id)
    else:
        form = PedidoForm()
    return render (request, 'pedido/novo_pedido.html', {'form' : form})


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

        item = ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            variacao=variacao,
            quantidade=quantidade
        )

        if produto.tipo in ['KIT', 'BOLO', 'CUPCAKE', 'CASEIRINHO']:
            return redirect('item_pedido_editar', item_id=item.id)
        
        return  redirect('pedido_detalhe', pedido_id=pedido.id)
    return render (request, 'pedido/escolher_variacao.html', {
        'pedido':pedido,
        'produto': produto,
        'variacoes': variacoes
    })

def pedido_detalhe(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    return render(request, 'pedido/detalhe.html', {'pedido': pedido})

def item_pedido_editar(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id)
    doce_formset= None
    salgado_formset = None

    if request.method == 'POST':
        form = ItemPedidoForm(request.POST, request.FILES, instance=item)

        if item.produto.tipo == 'KIT':
            doce_formset = ItemPedidoDoceFormSet(request.POST, instance=item)
            salgado_formset = ItemPedidoSalgadoFormSet(request.POST, instance=item)

            if form.is_valid() and doce_formset.is_valid() and salgado_formset.is_valid():
                form.save()
                doce_formset.save()
                salgado_formset.save()
                return redirect('pedido_detalhe', pedido_id=item.pedido.id)
        else:
            if form.is_valid():
                form.save()
                return redirect('pedido_detalhe', pedido_id=item.pedido.id)
    else:
        form = ItemPedidoForm(instance=item)

        if item.produto.tipo == 'KIT':
            doce_formset = ItemPedidoDoceFormSet(instance=item)
            salgado_formset = ItemPedidoSalgadoFormSet(instance=item)

    return render (request, 'pedido/item_editar.html', {'item':item, 'form':form, 'doce_formset':doce_formset, 'salgado_formset':salgado_formset})

def item_pedido_remover(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemPedido, id=item_id)
        pedido_id = item.pedido.id

        item.delete()
        return redirect('pedido_detalhe', pedido_id=pedido_id)

def pedido_finalizar(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if pedido.status != 'rascunho':
        return redirect('pedido_detalhe', pedido_id=pedido.id)

    if not pedido.itens.exists():
        return redirect('pedido_detalhe', pedido_id=pedido.id)
    
    pedido.status = 'finalizado'
    pedido.save()

    return redirect('pedido_detalhe', pedido_id=pedido.id)