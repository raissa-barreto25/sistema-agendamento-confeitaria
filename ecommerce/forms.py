from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Pedido
from django.forms import ModelForm
from django import forms

class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'email']

class DataPedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['data_entrega']

class PersonalizacaoPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['observacoes']

class QuantidadeForm(forms.Form):
    quantidade = forms.IntegerField(min_value=1)