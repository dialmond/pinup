from django.shortcuts import redirect
from django.urls import reverse, resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = reverse('accounts:login')
        self.allowed_views = ['login', 'password_reset', 'password_change', 'password_reset_done', 'password_reset_confirm', 'password_reset_complete']

    def __call__(self, request):
        view = resolve(request.path_info).url_name
        #if not request.user.is_authenticated and request.path != self.login_url:
        if not request.user.is_authenticated and not view in self.allowed_views:
            return redirect(self.login_url+'?next='+request.path)
        return self.get_response(request)
