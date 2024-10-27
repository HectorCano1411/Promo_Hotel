from django.urls import path
from .views import EmailAPIView, HomeView, RegisterView, SetPasswordView, VerifyEmailView, AdminLoginView, AdminDashboardView, GenerateWinnerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Vista para manejar la raíz
    path('email/', EmailAPIView.as_view(), name='email'),  # Vista para manejar la raíz
    path('register/', RegisterView.as_view(), name='api-register'),  
    path('api/users/verify/<uuid:token>/', VerifyEmailView.as_view(), name='verify_email'),  # Asegúrate de que el nombre coincida
    path('admin/login/', AdminLoginView.as_view(), name='api-admin-login'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='api-admin-dashboard'),
    path('generate-winner/', GenerateWinnerView.as_view(), name='generate-winner'),
    path('set-password/<uidb64>/<token>/', SetPasswordView.as_view(), name='set-password'),
    # JWT Authentication URLs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

    # path("api/gmail/labels/", GmailLabelsView.as_view(), name="gmail_labels"),
#  GmailLabelsView,