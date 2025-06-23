from django import template
import json

register = template.Library()

@register.filter
def parse_json(value):
    """
    将JSON字符串解析为Python对象
    """
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return None 