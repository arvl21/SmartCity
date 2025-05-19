from django.db import models
from django.core.cache import cache
import requests
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class ProblemType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Тип проблемы")

    def __str__(self):
        return self.name

    @classmethod
    def create_default_types(cls):
        default_types = [
            "Яма на дороге",
            "Мусор",
            "Неработающее освещение",
            "Другое"
        ]
        for type_name in default_types:
            cls.objects.get_or_create(name=type_name)


class Problem(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('resolved', 'Решена'),
    ]

    STATUS_COLORS = {
        'new': 'red',
        'in_progress': 'orange',
        'resolved': 'green'
    }

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    problem_type = models.ForeignKey(
        ProblemType,
        on_delete=models.CASCADE,
        verbose_name="Тип проблемы"
    )
    short_description = models.CharField(
        max_length=200,
        verbose_name="Краткое описание"
    )
    full_description = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Подробное описание"
    )
    address = models.TextField(verbose_name="Адрес")
    latitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Широта"
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Долгота"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    expected_solve_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ожидаемая дата решения"
    )

    class Meta:
        verbose_name = 'Проблема'
        verbose_name_plural = 'Проблемы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.problem_type}: {self.short_description}"

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, 'gray')

    def get_location(self):
        return {
            'lat': self.latitude,
            'lng': self.longitude
        } if self.latitude and self.longitude else None

    def geocode_address(self):
        if not self.address:
            return False

        try:
            response = requests.get(
                'https://geocode-maps.yandex.ru/1.x/',
                params={
                    'geocode': self.address,
                    'apikey': settings.YANDEX_MAPS_API_KEY,
                    'format': 'json',
                    'results': 1
                },
                timeout=5
            )
            data = response.json()

            pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            self.longitude, self.latitude = map(float, pos.split(' '))
            return True

        except Exception as e:
            logger.error(f"Yandex geocoding failed: {str(e)}")
            # Резервный вариант
            self.latitude = 55.751244
            self.longitude = 37.618423
            return False

    def save(self, *args, **kwargs):
        if not self.pk or 'address' in kwargs.get('update_fields', []):
            if not self.geocode_address():
                # Координаты по умолчанию для Москвы
                self.latitude = 55.751244
                self.longitude = 37.618423

        super().save(*args, **kwargs)

class ProblemImage(models.Model):
    problem = models.ForeignKey(Problem, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='problems/')

    def __str__(self):
        return f"Image for {self.problem.id}"

    class Meta:
        verbose_name = 'Изображение проблемы'
        verbose_name_plural = 'Изображения проблем'