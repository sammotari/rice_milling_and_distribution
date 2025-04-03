# core/middleware.py
from django.http import HttpResponseForbidden
from django.urls import resolve

from core.models import CustomUser

class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        url_name = resolve(request.path_info).url_name
        
        role_urls = {
            'admin_dashboard': CustomUser.Role.ADMIN,
            'farmer_dashboard': CustomUser.Role.FARMER,
            'customer_dashboard': CustomUser.Role.CUSTOMER,
            'delivery_dashboard': CustomUser.Role.DELIVERY,
            'mill_operator_dashboard': CustomUser.Role.MILL_OPERATOR,
        }

        if url_name in role_urls and request.user.role != role_urls[url_name]:
            return HttpResponseForbidden("You don't have permission to access this page.")
        
        return None