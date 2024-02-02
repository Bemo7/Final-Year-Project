from django import template

register = template.Library()

def split(value):
    return value.split(',')
def minus(value, num=1):
    return value -num

register.filter("split", split)
register.filter("minus", minus)