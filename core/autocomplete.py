# In your autocomplete.py file
import autocomplete_light
from .models import CustomUser, Farmer

class FarmerAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['user__first_name', 'user__last_name']  # Search by farmer's first and last name
    
    # Filter users by role 'FARMER'
    def get_queryset(self):
        return CustomUser.objects.filter(role=CustomUser.Role.FARMER)

autocomplete_light.register(FarmerAutocomplete)
