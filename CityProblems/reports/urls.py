from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'problems', views.ProblemViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Проблемы
    path('create/', views.create_problem, name='create_problem'),
    path('problem/<int:pk>/', views.problem_detail, name='problem_detail'),

    # API
    path('api/', include(router.urls)),
    path('api/problems/', views.ProblemsAPIView.as_view(), name='problems_api'),
    path('api/get_problems/', views.get_problems, name='get_problems'),
    path('geocode/', views.geocode, name='geocode'),

    # Профиль
    path('profile/', views.profile, name='profile'),

    # Сброс пароля
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]