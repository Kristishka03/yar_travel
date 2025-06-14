from django.urls import path
from . import views
from django.contrib.auth.views import LoginView  # Удалите если не используете

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),  # Оставляем только этот вариант
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('route/', views.select_places, name='select_places'),
    path('select-places/', views.select_places, name='select_places'),
    path('calculate-route/', views.calculate_route, name='calculate_route'),
    path('route-result/', views.route_result, name='route_result'),
]