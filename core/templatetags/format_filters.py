from django import template

register = template.Library()

@register.filter
def abreviar_numero(valor):
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return valor

    if valor >= 1_000_000_000:
        return f"{valor/1_000_000_000:.2f} bilhões"
    elif valor >= 1_000_000:
        return f"{valor/1_000_000:.2f} milhões"
    elif valor >= 1_000:
        return f"{valor/1_000:.2f} mil"
    else:
        return f"{valor:.2f}"
