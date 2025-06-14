from .models import Place, UserProfile
from django.contrib import admin
from .models import Route

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('title', 'place1', 'place2', 'transport', 'distance', 'duration')
    search_fields = ('title', 'place1__name', 'place2__name')
    list_filter = ('transport',)

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'latitude', 'longitude')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city')
