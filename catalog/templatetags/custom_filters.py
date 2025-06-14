from django import template

register = template.Library()

@register.filter
def dictsum(items, key):
    """Суммирует значения по ключу в списке словарей"""
    return sum(float(item[key]) for item in items)