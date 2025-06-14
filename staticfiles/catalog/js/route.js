document.addEventListener('DOMContentLoaded', function() {
    // Получаем все кнопки фильтров и карточки мест
    const filterButtons = document.querySelectorAll('.category-filter');
    const placeCards = document.querySelectorAll('.place-card');

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
}); 