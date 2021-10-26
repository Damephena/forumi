from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView
from accounts import views

router = SimpleRouter()

urlpatterns = [
    path("register/", views.RegisterView.as_view()),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh-token/", TokenRefreshView.as_view(), name="token_refresh"),
    path('password-reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]

router.register("dashboard", views.DashboardViewset)

urlpatterns += router.urls
