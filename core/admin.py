from django.contrib import admin
from .models import Conta, Categoria, Lancamento

admin.site.register(Conta)
admin.site.register(Categoria)
admin.site.register(Lancamento)