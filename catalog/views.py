from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Place, Route, UserProfile
from .forms import CustomUserCreationForm, UserProfileForm
from django.core.mail import send_mail
from django.conf import settings
import math

def catalog(request):
    places = Place.objects.all().order_by('category', 'name')
    categories = {place.get_category_display() for place in places}
    return render(request, 'catalog/catalog.html', {
        'places': places,
        'categories': categories
    })

def index(request):
    return render(request, 'catalog/index.html')


def place_list(request):
    places = Place.objects.all()
    return render(request, 'catalog/place_list.html', {'places': places})


def place_detail(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    return render(request, 'catalog/place_detail.html', {'place': place})


def route_list(request):
    routes = Route.objects.all()
    return render(request, 'catalog/route_list.html', {'routes': routes})


def route_detail(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    return render(request, 'catalog/route_detail.html', {'route': route})


@login_required
def edit_route(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    if request.method == 'POST':
        form = RouteForm(request.POST, request.FILES, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Маршрут успешно обновлен')
            return redirect('route_detail', route_id=route.id)
    else:
        form = RouteForm(instance=route)
    return render(request, 'catalog/route_form.html', {'form': form, 'route': route})


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'catalog/profile.html', {
        'user': request.user,
        'user_profile': user_profile
    })

# @login_required # Убран декоратор, чтобы добавить кастомное сообщение
def select_places(request):
    if not request.user.is_authenticated:
        messages.error(request, "Для создания маршрута необходимо войти в профиль.")
        return redirect('login')

    places = Place.objects.all().order_by('category', 'name')
    categories = {place.get_category_display() for place in places}
    return render(request, 'catalog/select_places.html', {
        'places': places,
        'categories': categories
    })


@login_required
def calculate_route(request):
    if request.method != 'POST':
        return redirect('select_places')

    try:
        place_ids = request.POST.getlist('places')
        if not place_ids:
            return JsonResponse({'status': 'error', 'message': 'Не выбрано ни одного места'}, status=400)

        selected_places = list(Place.objects.filter(id__in=place_ids))
        if len(selected_places) < 2:
            return JsonResponse({'status': 'error', 'message': 'Выберите минимум 2 места'}, status=400)

        # Алгоритм ближайшего соседа для построения маршрута
        start_place = min(selected_places, key=lambda x: x.longitude)
        remaining_places = [p for p in selected_places if p != start_place]

        route_data_for_json = []

        route_data_for_json.append({
            'place': {
                'id': start_place.id,
                'name': start_place.name,
                'latitude': float(start_place.latitude),
                'longitude': float(start_place.longitude),
            },
            'distance': 0,
            'transport': 'Старт',
            'duration': 0
        })

        current_place = start_place
        while remaining_places:
            next_place, best_route = find_nearest_place(current_place, remaining_places)

            if next_place is None:
                break

            route_data_for_json.append({
                'place': {
                    'id': next_place.id,
                    'name': next_place.name,
                    'latitude': float(next_place.latitude),
                    'longitude': float(next_place.longitude),
                },
                'distance': float(best_route['distance']),
                'transport': best_route['transport'],
                'duration': int(best_route['duration'])
            })
            current_place = next_place
            remaining_places.remove(next_place)

        # Отправка маршрута на почту
        user_email = None

        if request.user.is_authenticated and request.user.email:
            user_email = request.user.email
            try:
                # send_route_email(route_data_for_json, user_email) # Временно закомментировано для отладки
                pass # Добавлено pass, чтобы блок if не был пустым
            except Exception as e:
                print(f"Ошибка отправки письма: {str(e)}")

        request.session['last_calculated_route'] = route_data_for_json # Сохраняем в сессии для route_result
        return JsonResponse({'status': 'success', 'redirect_url': '/route-result/'})

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def find_nearest_place(current_place, places):
    """Находит ближайшее место из списка"""
    next_place = None
    min_distance = float('inf')
    best_route = {}

    for place in places:
        try:
            # Пытаемся найти маршрут в обоих направлениях
            try:
                route_data = Route.objects.get(place1=current_place, place2=place)
            except Route.DoesNotExist:
                try:
                    route_data = Route.objects.get(place1=place, place2=current_place)
                except Route.DoesNotExist:
                    route_data = None

            if route_data:
                distance = route_data.distance
                transport = route_data.get_transport_display()
                duration = route_data.duration
            else:
                # Если маршрута нет в базе, используем формулу Хаверсина
                distance = haversine_distance(current_place, place)
                transport = 'пешком'
                duration = distance * 10  # 10 мин на км пешком

            if distance < min_distance:
                min_distance = distance
                next_place = place
                best_route = {
                    'distance': distance,
                    'transport': transport,
                    'duration': duration
                }

        except Exception as e:
            print(f"Ошибка при поиске маршрута: {str(e)}")
            continue

    return next_place, best_route

def haversine_distance(place1, place2):
    """Расчёт расстояния между точками по формуле Хаверсина"""
    lat1, lon1 = math.radians(place1.latitude), math.radians(place1.longitude)
    lat2, lon2 = math.radians(place2.latitude), math.radians(place2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return 6371 * c  # Радиус Земли в км

def send_route_email(route, email):
    """Отправка маршрута на почту"""
    subject = 'Ваш туристический маршрут по Ярославлю'

    message_lines = [
        "Ваш оптимальный маршрут:",
        "----------------------------------------"
    ]

    for i, point in enumerate(route):
        if i == 0:
            message_lines.append(f"Старт: {point['place']['name']}")
        else:
            message_lines.append(
                f"{i}. {point['place']['name']} - "
                f"{point['distance']:.2f} км, "
                f"{point['transport']}, "
                f"{point['duration']} мин"
            )

    total_distance = sum(p['distance'] for p in route[1:])
    total_duration = sum(p['duration'] for p in route[1:])

    message_lines.extend([
        "----------------------------------------",
        f"Общее расстояние: {total_distance:.2f} км",
        f"Общее время: {total_duration} мин"
    ])

    send_mail(
        subject=subject,
        message="\n".join(message_lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )

def route_result(request):
    route_data = request.session.get('last_calculated_route', None)
    if route_data:
        # Очищаем данные из сессии после использования, чтобы при перезагрузке страницы не было старых данных
        del request.session['last_calculated_route']
        return render(request, 'catalog/route_result.html', {'route': route_data})
    else:
        # Если данных нет, перенаправляем пользователя на страницу выбора мест с сообщением об ошибке
        # messages.error(request, "Данные маршрута не найдены. Пожалуйста, создайте маршрут снова.") # Это может быть добавлено, если у вас есть система сообщений
        return redirect('select_places')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'catalog/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'catalog/login.html', {'error': 'Неверное имя пользователя или пароль'})
    return render(request, 'catalog/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'catalog/update_profile.html', {'form': form})


@login_required
def delete_route(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    if request.method == 'POST':
        route.delete()
        return redirect('profile')
    return render(request, 'catalog/confirm_delete.html', {'route': route})
