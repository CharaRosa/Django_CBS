from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sub(value, arg):
    """
    Soustrait l'argument 'arg' de la 'value'.
    Gère les types Decimal (nécessaire pour les nombres d'heures).
    """
    try:
        # Convertir en Decimal si ce n'est pas déjà le cas
        dec_value = Decimal(str(value))
        dec_arg = Decimal(str(arg))
        return dec_value - dec_arg
    except:
        return 0 # Retourne 0 en cas d'erreur de conversion