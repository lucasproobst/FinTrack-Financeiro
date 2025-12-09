from django.db import models
from django.contrib.auth.models import User


# ----------------------------------------
#   CONTA
# ----------------------------------------
class Conta(models.Model):
    nome = models.CharField(max_length=100)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

    @property
    def saldo_total(self):
        receitas = (
            self.lancamento_set.filter(tipo="Receita").aggregate(
                total=models.Sum("valor")
            )["total"]
            or 0
        )

        despesas = (
            self.lancamento_set.filter(tipo="Despesa").aggregate(
                total=models.Sum("valor")
            )["total"]
            or 0
        )

        return self.saldo_inicial + receitas - despesas


# ----------------------------------------
#   CATEGORIA
# ----------------------------------------
class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=10, choices=[("Receita", "Receita"), ("Despesa", "Despesa")]
    )
    cor = models.CharField(max_length=7, default="#0d6efd")
    icone = models.CharField(max_length=50, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        nome_lower = self.nome.lower()

        icones_por_palavra = {
            # Despesas - Contas e Serviços
            "luz": "bi bi-lightbulb-fill",
            "energia": "bi bi-lightning-charge-fill",
            "internet": "bi bi-wifi",
            "telefone": "bi bi-phone",
            "água": "bi bi-droplet-half",
            "netflix": "bi bi-tv-fill",
            "spotify": "bi bi-music-note-beamed",
            "amazon": "bi bi-box-seam-fill",
            "prime": "bi bi-box-seam-fill",
            # Despesas - Casa
            "mercado": "bi bi-basket-fill",
            "supermercado": "bi bi-cart4",
            "aluguel": "bi bi-house-door-fill",
            "condomínio": "bi bi-building",
            "limpeza": "bi bi-bucket-fill",
            "móveis": "bi bi-couch",
            "eletrodoméstico": "bi bi-plug-fill",
            # Transporte
            "transporte": "bi bi-truck-front",
            "carro": "bi bi-car-front-fill",
            "uber": "bi bi-taxi-front-fill",
            "gasolina": "bi bi-fuel-pump-fill",
            "combustível": "bi bi-fuel-pump-fill",
            "passagem": "bi bi-ticket-detailed",
            "ônibus": "bi bi-bus-front-fill",
            "viagem": "bi bi-airplane-fill",
            # Alimentação
            "comida": "bi bi-cup-straw",
            "lanches": "bi bi-cup-hot-fill",
            "restaurante": "bi bi-egg-fried",
            "pizza": "bi bi-pie-chart-fill",
            "hamburguer": "bi bi-cup-hot-fill",
            "delivery": "bi bi-truck",
            # Saúde
            "remédio": "bi bi-capsule-pill",
            "farmácia": "bi bi-capsule",
            "médico": "bi bi-heart-pulse-fill",
            "plano": "bi bi-card-checklist",
            "hospital": "bi bi-hospital-fill",
            # Renda / Receita
            "salário": "bi bi-cash-stack",
            "freela": "bi bi-briefcase-fill",
            "pix": "bi bi-qr-code-scan",
            "renda": "bi bi-graph-up",
            "venda": "bi bi-cart-check-fill",
            "bônus": "bi bi-award-fill",
            # Bancos e Pagamentos
            "banco": "bi bi-bank",
            "transferência": "bi bi-arrow-left-right",
            "cartao": "bi bi-credit-card-2-back-fill",
            "cartão": "bi bi-credit-card-2-back-fill",
            "boleto": "bi bi-receipt",
            "nubank": "bi bi-credit-card",
            "inter": "bi bi-bank",
            "santander": "bi bi-building-fill",
            "bradesco": "bi bi-piggy-bank-fill",
            "itau": "bi bi-wallet2",
            # Poupança e Finanças
            "carteira": "bi bi-wallet-fill",
            "poupança": "bi bi-piggy-bank-fill",
            "investimento": "bi bi-bar-chart-fill",
            "cripto": "bi bi-currency-bitcoin",
            "ações": "bi bi-graph-up-arrow",
            # Diversos
            "outro": "bi bi-tag-fill",
            "roupas": "bi bi-shop-window",
            "presentes": "bi bi-gift-fill",
            "academia": "bi bi-dumbbell",
            "pets": "bi bi-paw-fill",
            "filmes": "bi bi-film",
            "estudos": "bi bi-book-half",
            "educação": "bi bi-mortarboard-fill",
            "curso": "bi bi-easel-fill",
            "eventos": "bi bi-calendar-event-fill",
        }

        if not self.icone:
            for palavra, icone in icones_por_palavra.items():
                if palavra in nome_lower:
                    self.icone = icone
                    break

            if not self.icone:
                self.icone = "bi bi-cash-coin"  # Padrão

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


# ----------------------------------------
#   LANCAMENTO
# ----------------------------------------
class Lancamento(models.Model):
    TIPO_CHOICES = [
        ("Receita", "Receita"),
        ("Despesa", "Despesa"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255)

    valor = models.DecimalField(max_digits=10, decimal_places=2)

    data = models.DateField()

    comprovante = models.FileField(upload_to="comprovantes/", null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo}: {self.descricao} - R$ {self.valor}"
