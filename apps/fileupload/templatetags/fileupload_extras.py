from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary safely"""
    return dictionary.get(key, "")

@register.filter
def has_missing_values(missing_values_dict):
    """Check if any column has missing values"""
    if not missing_values_dict:
        return False
    return any(count > 0 for count in missing_values_dict.values())

@register.filter
def missing_columns_list(missing_values_dict):
    """Get list of columns with missing values"""
    if not missing_values_dict:
        return []
    return [(col, count) for col, count in missing_values_dict.items() if count > 0]

@register.filter
def calculate_percentage(missing_count, total_rows):
    """Calculate percentage of missing values"""
    if not total_rows or total_rows == 0:
        return 0
    return round((missing_count / total_rows) * 100, 1)

@register.filter
def mul(value, arg):
    """Multiply filter"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide filter"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0
