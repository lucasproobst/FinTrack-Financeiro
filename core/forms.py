from django import forms
from .models import Conta, Lancamento, Categoria
from django.contrib.auth.forms import PasswordChangeForm

class LancamentoForm(forms.ModelForm):
    class Meta:
        model = Lancamento
        fields = [
            "data",
            "categoria",
            "descricao",
            "valor",
            "conta",
            "comprovante",
        ]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control"}),
            "conta": forms.Select(attrs={"class": "form-select"}),
            "comprovante": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["categoria"].queryset = Categoria.objects.filter(usuario=user)
            self.fields["conta"].queryset = Conta.objects.filter(usuario=user)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "tipo", "cor"]
        widgets = {
            "cor": forms.TextInput(
                attrs={"type": "color", "class": "form-control form-control-color"}
            ),
        }


class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ["nome", "saldo_inicial"]


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
