from django import template
from news.censoredwords import *

register = template.Library()


@register.filter(name='censor')
def censor(value):
    if isinstance(value, str):
        for _ in cens_words_list:
            if _.lower() in value.lower():
                value = value.replace(_.lower(), '*' * len(_))
            else:
                continue
    else:
        raise ValueError
    return value


@register.filter(name='multiply')
def multiply(value, arg):
    if isinstance(value, str) and isinstance(arg, int):
        return str(value) * arg
    else:
        raise ValueError(f'Нельзя умножить {type(value)} на {type(arg)}')
