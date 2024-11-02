# urls.py
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def redirect_to_home(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_home),  # Redirect to login or home based on authentication
    path('accounts/', include('accounts.urls')),
    path('profile/', include('profiles.urls')),
    path('batch/', include('batch_allocation.urls')),
    path('test/', include('test_.urls')),
    path('visualization/', include('visual.urls')),
    path('feedback/', include('feedback.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
