from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from city import settings
from .models import Problem, ProblemType
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProblemForm
from .models import Problem, ProblemImage
from django.views.decorators.http import require_GET
import requests
import json

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import ProblemSerializer, ProblemImageSerializer

# Константы для Санкт-Петербурга
SPB_CENTER = [59.9386, 30.3141]  # Координаты Дворцовой площади
SPB_BOUNDS = '29.8,59.8~30.7,60.2'  # Границы СПб и области (min_lon,min_lat~max_lon,max_lat)


def home(request):
    latest_problems = Problem.objects.all().order_by('-created_at')[:5]
    return render(request, 'home.html', {
        'latest_problems': latest_problems,
        'default_map_center': SPB_CENTER  # Передаем центр СПб в шаблон
    })


@login_required
def create_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.user = request.user

            # Безопасное получение координат с проверкой
            try:
                lat = float(request.POST.get('latitude', SPB_CENTER[0]))
                lon = float(request.POST.get('longitude', SPB_CENTER[1]))
            except (TypeError, ValueError):
                lat, lon = SPB_CENTER  # Используем центр СПб при ошибке

            # Проверка границ СПб
            if not (59.8 <= lat <= 60.2 and 29.8 <= lon <= 30.7):
                lat, lon = SPB_CENTER

            problem.latitude = lat
            problem.longitude = lon
            problem.save()

            # Ограничение на 3 изображения
            images = request.FILES.getlist('images')[:3]
            for img in images:
                ProblemImage.objects.create(problem=problem, image=img)

            return redirect('problem_detail', pk=problem.pk)
    else:
        form = ProblemForm()

    return render(request, 'reports/create_problem.html', {
        'form': form,
        'YANDEX_MAPS_API_KEY': settings.YANDEX_MAPS_API_KEY,
        'default_map_center': SPB_CENTER
    })

@require_GET
def geocode(request):
    address = request.GET.get('address', '')
    if not address:
        return JsonResponse({'error': 'Address parameter is required'}, status=400)

    try:
        response = requests.get(
            "https://geocode-maps.yandex.ru/1.x/",
            params={
                'geocode': address,
                'format': 'json',
                'apikey': settings.YANDEX_MAPS_API_KEY,
                'results': 5,
                'lang': 'ru_RU',
                'bbox': SPB_BOUNDS  # Используем константу для границ СПб
            },
            headers={'User-Agent': settings.USER_AGENT},
            timeout=5
        )
        response.raise_for_status()

        data = response.json()
        features = []
        for member in data['response']['GeoObjectCollection']['featureMember']:
            obj = member['GeoObject']
            pos = obj['Point']['pos'].split()  # Долгота, Широта

            # Проверяем, что координаты в пределах СПб
            lon, lat = float(pos[0]), float(pos[1])
            if 29.8 <= lon <= 30.7 and 59.8 <= lat <= 60.2:
                features.append({
                    'name': obj['name'],
                    'description': obj.get('description', ''),
                    'coordinates': [lat, lon]  # Широта, Долгота
                })

        return JsonResponse({
            'features': features,
            'bounds': SPB_BOUNDS  # Добавляем границы в ответ
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'default_coordinates': SPB_CENTER  # Возвращаем центр СПб при ошибке
        }, status=500)


# Остальные функции остаются без изменений
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        return render(request, 'registration/login.html', {'error': 'Неверные данные'})
    return render(request, 'registration/login.html')


@login_required
def profile(request):
    user_problems = Problem.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reports/profile.html', {'problems': user_problems})


@require_GET
def get_problems(request):
    problems = Problem.objects.all()

    # Фильтрация по параметрам
    problem_type = request.GET.get('type')
    status = request.GET.get('status')
    date_filter = request.GET.get('date')

    if problem_type and problem_type != 'all':
        problems = problems.filter(problem_type_id=problem_type)
    if status and status != 'all':
        problems = problems.filter(status=status)
    if date_filter:
        today = datetime.now().date()
        if date_filter == 'today':
            problems = problems.filter(created_at__date=today)
        elif date_filter == 'week':
            problems = problems.filter(created_at__date__gte=today - timedelta(days=7))
        elif date_filter == 'month':
            problems = problems.filter(created_at__date__gte=today - timedelta(days=30))

    serializer = ProblemSerializer(problems, many=True)
    return JsonResponse(serializer.data, safe=False)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def problem_detail(request, pk):
    problem = get_object_or_404(Problem.objects.prefetch_related('images'), pk=pk)
    return render(request, 'reports/problem_detail.html', {'problem': problem})


class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all().prefetch_related('images')
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProblemsAPIView(APIView):
    def get(self, request):
        problems = Problem.objects.all().prefetch_related('images')
        serializer = ProblemSerializer(problems, many=True)
        return Response(serializer.data)