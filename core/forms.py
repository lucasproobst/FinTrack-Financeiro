from django import forms
from .models import Conta, Lancamento, Categoria
from django.contrib.auth.forms import PasswordChangeForm

from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


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
            field.widget.attrs.update({"class": "form-control"})


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):

        subject = render_to_string(subject_template_name, context).strip()
        body_text = render_to_string(email_template_name, context)
        body_html = render_to_string(html_email_template_name, context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[to_email]
        )
        email.attach_alternative(body_html, "text/html")
        email.send()
