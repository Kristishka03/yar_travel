document.addEventListener('DOMContentLoaded', function() {
    // Получаем все кнопки фильтров и карточки мест
    const filterButtons = document.querySelectorAll('.category-filter');
    const placeCards = document.querySelectorAll('.place-card');
    const selectPlacesForm = document.getElementById('select-places-form');

    // Добавляем обработчик клика для каждой кнопки фильтра
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Удаляем класс active у всех кнопок
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Добавляем класс active к нажатой кнопке
            this.classList.add('active');

            // Получаем выбранную категорию
            const selectedCategory = this.getAttribute('data-category');

            // Фильтруем карточки мест
            placeCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');
                
                if (selectedCategory === 'all' || cardCategory === selectedCategory) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Handle form submission via AJAX
    if (selectPlacesForm) {
        selectPlacesForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission

            const selectedPlaceIds = [];
            selectPlacesForm.querySelectorAll('input[name="places"]:checked').forEach(checkbox => {
                selectedPlaceIds.push(checkbox.value);
            });

            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            const formData = new FormData();
            selectedPlaceIds.forEach(id => {
                formData.append('places', id);
            });
            formData.append('csrfmiddlewaretoken', csrfToken);

            fetch(selectPlacesForm.action, {
                method: 'POST',
                body: formData,
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.message || 'Неизвестная ошибка сервера');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    } else {
                        alert('Ошибка: URL для перенаправления не получен.');
                    }
                } else {
                    alert('Ошибка: ' + (data.message || 'Неизвестная ошибка'));
                }
            })
            .catch(error => {
                console.error('Ошибка при отправке данных:', error);
                alert('Произошла ошибка при построении маршрута: ' + error.message);
            });
        });
    }
}); 