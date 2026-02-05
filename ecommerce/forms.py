from .models import Cliente, Pedido, ItemPedido, ItemPedidoDoce, ItemPedidoSalgado, Produto
from django.forms import ModelForm, inlineformset_factory
from django import forms

class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'email']

class DataPedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['data_entrega']

class QuantidadeForm(forms.Form):
    quantidade = forms.IntegerField(min_value=1)

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'data_entrega', 'observacoes', 'status']

    def clean_data_entrega(self):
        data = self.cleaned_data.get('data_entrega')
        if not data:
            return data
        
        pedido_fake = Pedido(data_entrega=data)
        pedido_fake.clean()
        return data
    
class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'variacao', 'quantidade', 'massa', 'recheio', 'tema', 'observacao', 'imagem_referencia',]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['massa'].required = False
        self.fields['recheio'].required = False
        self.fields['tema'].required = False

        produto = None

        if self.instance.pk:
            produto = self.instance.produto

        else:
            produto_id = self.data.get('produto')
            if produto_id:
                try:
                    produto = Produto.objects.get(pk=produto_id)
                except Produto.DoesNotExist:
                    pass
        
        if not produto:
            return
        
        if produto.tipo == 'KIT':
            self.fields['massa'].required = True
            self.fields['recheio'].required = True
            self.fields['tema'].required = True

        if produto.tipo in ['BOLO', 'CUPCAKE', 'CASEIRINHO']:
            self.fields['massa'].required = True
            self.fields['recheio'].required = True
            self.fields['tema'].widget = forms.HiddenInput()

class ItemPedidoDoceForm(forms.ModelForm):
    class Meta:
        model = ItemPedidoDoce
        fields = ['sabor', 'quantidade']

class ItemPedidoSalgadoForm(forms.ModelForm):
    class Meta:
        model = ItemPedidoSalgado
        fields = ['sabor', 'quantidade']

ItemPedidoDoceFormSet = inlineformset_factory(
    ItemPedido,
    ItemPedidoDoce,
    form=ItemPedidoDoceForm,
    extra=1,
    can_delete=True
)

ItemPedidoSalgadoFormSet = inlineformset_factory(
    ItemPedido,
    ItemPedidoSalgado,
    form=ItemPedidoSalgadoForm,
    extra=1,
    can_delete=True
)
