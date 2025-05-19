document.addEventListener('DOMContentLoaded', function() {
    const addressInput = document.getElementById('id_address');
    if (!addressInput) return;

    // Дебаунс для уменьшения запросов
    let timeout;
    addressInput.addEventListener('input', function(e) {
        clearTimeout(timeout);
        const query = e.target.value.trim();
        if (query.length < 3) return;

        timeout = setTimeout(() => {
            fetch(`/geocode/?address=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => showSuggestions(data.features))
                .catch(console.error);
        }, 300);
    });

    function showSuggestions(features) {
        const dropdown = document.getElementById('address-suggestions') || createDropdown();
        dropdown.innerHTML = features.map(feature => `
            <li class="list-group-item list-group-item-action">
                <div class="fw-bold">${feature.name}</div>
                <small class="text-muted">${feature.description || ''}</small>
            </li>
        `).join('');

        // Обработка выбора
        dropdown.querySelectorAll('li').forEach((item, index) => {
            item.addEventListener('click', () => {
                addressInput.value = features[index].name;
                if (features[index].description) {
                    addressInput.value += ', ' + features[index].description;
                }
                dropdown.innerHTML = '';

                // Можно добавить центрирование карты на выбранном адресе
                if (window.map && features[index].coordinates) {
                    window.map.setCenter(features[index].coordinates, 15);
                }
            });
        });
    }

    function createDropdown() {
        const dropdown = document.createElement('ul');
        dropdown.id = 'address-suggestions';
        dropdown.className = 'list-group position-absolute w-100';
        dropdown.style.zIndex = '1000';
        dropdown.style.maxHeight = '200px';
        dropdown.style.overflowY = 'auto';
        addressInput.parentNode.appendChild(dropdown);
        return dropdown;
    }
});