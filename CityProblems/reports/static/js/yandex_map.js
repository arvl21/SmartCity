// static/js/yandex_map.js
document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('map')) return;

    ymaps.ready(function() {
        // Устанавливаем центр карты на СПб (Дворцовая площадь)
        const map = new ymaps.Map('map', {
            center: [59.9386, 30.3141],  // Координаты Дворцовой площади
            zoom: 12,
            controls: ['zoomControl', 'typeSelector']
        });

        // Остальной код остается без изменений
        fetch('/get_problems/')
            .then(response => response.json())
            .then(problems => {
                problems.forEach(problem => {
                    new ymaps.Placemark(
                        problem.coordinates,
                        {
                            hintContent: problem.short_description,
                            balloonContent: `
                                <h5>${problem.problem_type}</h5>
                                <p>${problem.full_description || 'Нет описания'}</p>
                                <small>${problem.address}</small>
                            `
                        },
                        {
                            preset: problem.status === 'new' ? 'islands#redIcon' :
                                   (problem.status === 'in_progress' ? 'islands#yellowIcon' : 'islands#greenIcon')
                        }
                    ).addTo(map);
                });
            });
    });
});
// Функция для цветов маркеров по статусам
function getMarkerPreset(status) {
    switch(status) {
        case 'new': return 'islands#redIcon';
        case 'in_progress': return 'islands#yellowIcon';
        case 'resolved': return 'islands#greenIcon';
        default: return 'islands#blueIcon';
    }
}

// Инициализация карты для СПб
function initMap() {
    const map = new ymaps.Map('map', {
        center: [59.9386, 30.3141],  // СПб
        zoom: 12,
        controls: ['zoomControl', 'typeSelector', 'fullscreenControl']
    });

    // Загрузка проблем
    fetch('/get_problems/')
        .then(response => response.json())
        .then(problems => {
            problems.forEach(problem => {
                new ymaps.Placemark(
                    problem.coordinates,
                    {
                        hintContent: problem.short_description,
                        balloonContent: `
                            <h5>${problem.problem_type}</h5>
                            <p>${problem.full_description || 'Нет описания'}</p>
                            <small>Статус: ${problem.status}</small>
                        `,
                        iconCaption: problem.short_description.substring(0, 30)
                    },
                    {
                        preset: getMarkerPreset(problem.status),
                        draggable: false
                    }
                ).addTo(map);
            });
        });
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    ymaps.ready(initMap);
});