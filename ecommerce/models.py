from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal
from .services.google_calendar import (
    criar_evento_google,
    atualizar_evento_google,
    cancelar_evento_google,
)

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
    qtd_doces = models.PositiveBigIntegerField(default=0)
    qtd_salgados = models.PositiveBigIntegerField(default=0)
    
    def __str__(self):
        return f'{self.produto.nome} - {self.nome} - {self.preco}'

class Pedido(models.Model):

    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.PROTECT,
        related_name='pedidos'
    )

    data_pedido = models.DateTimeField(default=timezone.now)
    data_entrega = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='rascunho'
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    evento_calendar_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # -------------------------
    # REGRAS DE NEGÓCIO
    # -------------------------
    def clean(self):
        # domingo (6) e segunda (0)
        if self.data_entrega and self.data_entrega.weekday() in [6, 0]:
            raise ValidationError(
                {'data_entrega': 'Não é permitido agendamento para domingo ou segunda-feira.'}
            )

        # mínimo 2 dias de antecedência
        if self.data_entrega:
            dias = (self.data_entrega - timezone.now().date()).days
            if dias < 2:
                raise ValidationError(
                    {'data_entrega': 'Pedidos devem ser feitos com no mínimo 2 dias de antecedência.'}
                )

    # -------------------------
    # CÁLCULO DO TOTAL
    # -------------------------
    def calcular_total(self):
        total = sum(item.valor_total for item in self.itens.all())
        Pedido.objects.filter(pk=self.pk).update(total=total)

    # -------------------------
    # SAVE COM GOOGLE AGENDA
    # -------------------------
    def save(self, *args, **kwargs):
        pedido_antigo = None

        if self.pk:
            pedido_antigo = Pedido.objects.get(pk=self.pk)

        self.full_clean()
        super().save(*args, **kwargs)

        # FINALIZADO → criar evento
        if self.status == 'finalizado' and not self.evento_calendar_id:
            evento_id = criar_evento_google(self)
            Pedido.objects.filter(pk=self.pk).update(
                evento_calendar_id=evento_id
            )

        # FINALIZADO → data alterada → atualizar evento
        if (
            pedido_antigo and
            self.status == 'finalizado' and
            self.evento_calendar_id and
            pedido_antigo.data_entrega != self.data_entrega
        ):
            atualizar_evento_google(self.evento_calendar_id, self)

        # CANCELADO → remover evento
        if (
            pedido_antigo and
            pedido_antigo.status == 'finalizado' and
            self.status == 'cancelado' and
            self.evento_calendar_id
        ):
            cancelar_evento_google(self.evento_calendar_id)
            Pedido.objects.filter(pk=self.pk).update(
                evento_calendar_id=None
            )

    def __str__(self):
        return f'Pedido #{self.pk} - {self.cliente}'

from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class ItemPedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    produto = models.ForeignKey(
        'Produto',
        on_delete=models.PROTECT
    )

    variacao = models.ForeignKey(
        'VariacaoProduto',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    quantidade = models.PositiveIntegerField(default=1)

    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    observacao = models.TextField(blank=True)

    # Personalizações
    massa = models.ForeignKey(
        Sabor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_massa',
        limit_choices_to={'tipo': 'massa'}
    )

    recheio = models.ForeignKey(
        Sabor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_recheio',
        limit_choices_to={'tipo': 'recheio'}
    )

    tema = models.CharField(max_length=100, blank=True)

    imagem_referencia = models.ImageField(
        upload_to='referencias/',
        blank=True,
        null=True
    )

    # -------------------------
    # VALIDAÇÕES
    # -------------------------
    def clean(self):
        super().clean()

        if self.produto.tipo == 'KIT' and self.variacao:
            total_doces = sum(
                d.quantidade for d in self.doces_escolhidos.all()
            )
            total_salgados = sum(
                s.quantidade for s in self.salgados_escolhidos.all()
            )

            if total_doces > self.variacao.qtd_doces:
                raise ValidationError({
                    'doces_escolhidos': 'Quantidade de doces excede o limite do kit.'
                })

            if total_salgados > self.variacao.qtd_salgados:
                raise ValidationError({
                    'salgados_escolhidos': 'Quantidade de salgados excede o limite do kit.'
                })

    # -------------------------
    # SAVE
    # -------------------------
    def save(self, *args, **kwargs):

        if self.variacao:
            self.valor_unitario = self.variacao.preco

        self.valor_total = self.quantidade * self.valor_unitario

        self.full_clean()
        super().save(*args, **kwargs)

        # atualiza total do pedido
        self.pedido.calcular_total()

    def __str__(self):
        return f'{self.produto} ({self.quantidade}x)'

class ItemPedidoDoce(models.Model):
    item_pedido = models.ForeignKey(
        ItemPedido,
        on_delete=models.CASCADE,
        related_name='doces_escolhidos'
    )
    sabor = models.ForeignKey(
        Sabor,
        on_delete=models.PROTECT,
        limit_choices_to={'tipo': 'doce'}
    )
    quantidade = models.PositiveIntegerField()

class ItemPedidoSalgado(models.Model):
    item_pedido = models.ForeignKey(
        ItemPedido,
        on_delete=models.CASCADE,
        related_name='salgados_escolhidos'
    )
    sabor = models.ForeignKey(
        Sabor,
        on_delete=models.PROTECT,
        limit_choices_to={'tipo': 'salgado'}
    )
    quantidade = models.PositiveIntegerField()
