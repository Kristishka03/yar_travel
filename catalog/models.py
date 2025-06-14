from django.db import models
from django.contrib.auth.models import User

class Place(models.Model):
    CATEGORY_CHOICES = [
        ('museum', 'Музей'),
        ('park', 'Парк'),
        ('church', 'Церковь'),
        ('historic', 'Историческое место'),
    ]
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='places/', null=True, blank=True)

    def __str__(self):
        return self.name

class Route(models.Model):
    TRANSPORT_CHOICES = [
        ('walk', 'Пешком'),
        ('bus', 'Автобус'),
        ('trolley', 'Троллейбус'),
        ('taxi', 'Такси')
    ]

    title = models.CharField('Название', max_length=200, blank=True, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    place1 = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='start_routes')
    place2 = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='end_routes')
    distance = models.FloatField('Расстояние (км)')
    transport = models.CharField(
        'Транспорт',
        max_length=100,
        choices=TRANSPORT_CHOICES,
        default='walk'
    )
    duration = models.PositiveIntegerField('Длительность (мин)', default=0)

    def __str__(self):
        return self.title or f"Маршрут {self.id}"  # Обновите этот метод

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"Маршрут {self.place1} → {self.place2}"
        super().save(*args, **kwargs)

    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='routes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

def __str__(self):
    return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Профиль {self.user.username}"