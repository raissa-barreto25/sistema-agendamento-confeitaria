from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nome
    
class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class Produto(models.Model):
    tipo_choices = [('KIT', 'kit festa'), ('BOLO', 'bolo'), ('DOCES', 'doces'), ('SALGADOS', 'salgados'), ('CUPCAKE', 'cupcake'), ('CASEIRINHO', 'caseirinho')]
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=tipo_choices)

    def __str__(self):
        return f"{self.nome} - ({self.get_tipo_display()})"
    
class Sabor(models.Model):
    tipo_choices = [('recheio_bolo', 'Recheio de Bolo'), ('recheio_cupcake', 'Recheio do Mini Cupcake'), ('recheio_caseirinho', 'Recheio do Caseirinho'), ('massa_bolo', 'Massa do Bolo'), ('massa_caseirinho', 'Massa do Caseirinho'), ('massa_cupcake', 'Massa do Mini Cupcake'), ('doce', 'Doces'), ('salgado', 'Salgados')]
    nome = models.CharField(max_length=30)
    tipo = models.CharField(max_length=50, choices=tipo_choices)
    observacao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nome} - ({self.get_tipo_display()})"
    
class VariacaoProduto(models.Model):
    produto = models.ForeignKey (Produto, on_delete=models.CASCADE, related_name='variacoes')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    peso_kg = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f'{self.produto.nome} - {self.nome} - {self.preco}'

class Pedido(models.Model):
    status_choise = [('rascunho', 'Rascunho'), ('finalizado', 'Finalizado'), ('cancelado', 'Cancelado')]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    data_entrega = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    criando_em = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    evento_calendar_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=status_choise, default='rascunho')


    LIMITE_POR_DIA = 7

    def clean(self):
        if not self.data_entrega.weekday() in [6, 0]:
            raise ValidationError ("Não realizamos agendamentos aos domingos e segundas.")
        
        data_minima = date.today() + timedelta(days=2)

        if self.data_entrega < data_minima:
            raise ValidationError ("Pedidos devem ser realizado com no mínino 02 dias de antecedencia.")
            
        total_no_dia = Pedido.objects.filter(data_entrega=self.data_entrega).exclude(pk=self.pk).count()

        if total_no_dia >= self.LIMITE_POR_DIA:
            raise ValidationError ("Limite de pedidos para essa data foi atingida.")
    
    def calcular_total(self):
        total = Decimal("0.00")

        for item in self.itens.all():
            total += item.valor_total
        
        self.valor_total = total
        self.save(update_fields=["valor_total"])

    def __str__(self):
        return f"Pedido # {self.id}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    variacao = models.ForeignKey(VariacaoProduto, on_delete=models.PROTECT, null=True, blank=True)       
    quantidade = models.PositiveIntegerField(default=1)

    # Personalizações
    massa = models.ForeignKey(Sabor, on_delete=models.SET_NULL, null=True, blank=True, related_name='itens_massa')
    recheio = models.ForeignKey(Sabor, on_delete=models.SET_NULL, null=True, blank=True, related_name='itens_recheio')
    tema = models.CharField(max_length=100, blank=True)
    imagem_referencia = models.ImageField(upload_to='referencias/', blank=True, null=True)

    valor_unitario = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        if self.variacao: 
            self.valor_unitario = self.variacao.preco
        elif hasattr(self.produto, 'preco'):
            self.valor_unitario = self.produto.preco

        self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)
        self.pedido.calcular_total()