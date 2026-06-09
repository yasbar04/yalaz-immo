import re
from django import template

register = template.Library()


@register.filter
def fr_num(value):
    """Format a pure decimal number with French space thousands separator.
    600000 → 600 000 | 600000.00 → 600 000 | 2.5 → 2.5 | text → text"""
    s = str(value).strip()
    if not re.match(r'^\d+(\.\d+)?$', s):
        return value
    try:
        f = float(s)
        if f == int(f):
            return f"{int(f):,}".replace(',', ' ')
        return f"{f:,.2f}".replace(',', ' ')
    except (ValueError, TypeError):
        return value
