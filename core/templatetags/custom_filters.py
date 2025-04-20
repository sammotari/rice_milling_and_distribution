from django import template

register = template.Library()

# Filter to retrieve the value of a field dynamically by its name
@register.filter
def get_field_value(instance, field_name):
    return getattr(instance, field_name, None)

# Filter to add a CSS class to a form field widget
@register.filter
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

# Filter to return the correct dashboard URL based on user role
@register.filter
def get_dashboard_url(role):
    """Returns the dashboard URL for a given user role."""
    if role == 'admin':
        return 'admin_dashboard'
    elif role == 'farmer':
        return 'farmer_dashboard'
    elif role == 'customer':
        return 'customer_dashboard'
    elif role == 'delivery':
        return 'delivery_dashboard'
    elif role == 'mill_operator':
        return 'mill_operator_dashboard'
    return 'home'  # Default fallback if no role matches
