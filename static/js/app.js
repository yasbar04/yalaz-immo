document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('js-ready');

    initNavigation();
    initNavScroll();
    initUserMenu();
    initListingFilters();
    initDistrictAutocomplete();
    initRevealAnimations();
    initImageGallery();
});

function initNavScroll() {
    const header = document.getElementById('site-header');
    if (!header) return;

    const onScroll = () => {
        header.classList.toggle('nav-condensed', window.scrollY > 40);
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
}

function initNavigation() {
    const toggle = document.querySelector('[data-nav-toggle]');
    const panel = document.querySelector('[data-nav-panel]');

    if (!toggle || !panel) {
        return;
    }

    toggle.addEventListener('click', () => {
        const isOpen = panel.classList.toggle('is-open');
        document.body.classList.toggle('nav-open', isOpen);
        toggle.setAttribute('aria-expanded', String(isOpen));
    });
}

function initUserMenu() {
    const button = document.querySelector('[data-user-menu-toggle]');
    const dropdown = document.querySelector('[data-user-menu-dropdown]');

    if (!button || !dropdown) {
        return;
    }

    const closeDropdown = () => {
        dropdown.classList.remove('is-open');
        button.setAttribute('aria-expanded', 'false');
    };

    const openDropdown = () => {
        dropdown.classList.add('is-open');
        button.setAttribute('aria-expanded', 'true');
    };

    const toggleDropdown = () => {
        dropdown.classList.toggle('is-open');
        button.setAttribute('aria-expanded', String(dropdown.classList.contains('is-open')));
    };

    button.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleDropdown();
    });

    dropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    const links = dropdown.querySelectorAll('a');
    links.forEach((link) => {
        link.addEventListener('click', closeDropdown);
    });

    document.addEventListener('click', () => {
        if (dropdown.classList.contains('is-open')) {
            closeDropdown();
        }
    });
}

function initDistrictAutocomplete() {
    const cityInput = document.getElementById('id_city');
    const districtInput = document.getElementById('id_district');

    if (!cityInput || !districtInput) {
        return;
    }

    fetch('/static/js/districts.json')
        .then((response) => response.json())
        .then((districts) => {
            let list = document.getElementById('districts');
            if (!list) {
                list = document.createElement('datalist');
                list.id = 'districts';
                document.body.appendChild(list);
            }

            cityInput.addEventListener('input', () => {
                const city = cityInput.value.trim();
                const cityDistricts = districts[city] || [];
                list.innerHTML = '';

                cityDistricts.forEach((district) => {
                    const option = document.createElement('option');
                    option.value = district;
                    list.appendChild(option);
                });
            });
        })
        .catch(() => {
            console.warn('District autocomplete unavailable.');
        });
}

function initListingFilters() {
    const toggle = document.querySelector('[data-filter-toggle]');
    const panel = document.querySelector('[data-filter-panel]');
    const toggleIcon = toggle?.querySelector('[data-toggle-icon]');
    const toggleLabel = toggle?.querySelector('[data-toggle-label]');

    if (toggle && panel) {
        const advancedInputs = panel.querySelectorAll('input, select, textarea');
        const hasActiveAdvancedFilters = Array.from(advancedInputs).some((input) => {
            if (input.type === 'checkbox') {
                return input.checked;
            }
            return Boolean(input.value);
        });

        const setPanelState = (isOpen) => {
            panel.hidden = !isOpen;
            panel.classList.toggle('is-open', isOpen);
            toggle.classList.toggle('is-open', isOpen);
            toggle.setAttribute('aria-expanded', String(isOpen));

            if (toggleIcon) {
                toggleIcon.textContent = isOpen ? '-' : '+';
            }

            if (toggleLabel) {
                toggleLabel.textContent = isOpen ? 'Masquer les filtres' : 'Plus de filtres';
            }
        };

        setPanelState(hasActiveAdvancedFilters);

        toggle.addEventListener('click', () => {
            setPanelState(panel.hidden);
        });
    }

    const citySelect = document.getElementById('city');
    const districtSelect = document.getElementById('district');

    if (!citySelect || !districtSelect) {
        return;
    }

    const requestedDistrict = districtSelect.dataset.selected || districtSelect.value;

    const renderDistrictOptions = (districts, selectedDistrict) => {
        let html = '<option value="">Tous les quartiers</option>';

        if (!districts.length) {
            districtSelect.innerHTML = html;
            return;
        }

        districts.forEach((district) => {
            const selected = district === selectedDistrict ? ' selected' : '';
            html += `<option value="${district}"${selected}>${district}</option>`;
        });

        districtSelect.innerHTML = html;
    };

    const updateDistricts = async (selectedDistrict = '') => {
        const city = citySelect.value.trim();

        if (!city) {
            districtSelect.innerHTML = '<option value="">Tous les quartiers</option>';
            return;
        }

        try {
            const response = await fetch(`/listings/api/districts/?city=${encodeURIComponent(city)}`);
            const data = await response.json();
            renderDistrictOptions(data.districts || [], selectedDistrict);
        } catch (error) {
            console.error('Unable to load districts.', error);
        }
    };

    citySelect.addEventListener('change', () => updateDistricts());

    if (citySelect.value) {
        updateDistricts(requestedDistrict);
    }
}

function initRevealAnimations() {
    const elements = document.querySelectorAll('[data-reveal]');

    if (!elements.length || !('IntersectionObserver' in window)) {
        elements.forEach((element) => element.classList.add('is-visible'));
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.18,
        }
    );

    elements.forEach((element) => observer.observe(element));
}

function initImageGallery() {
    const mainImage = document.querySelector('[data-main-image]');
    const thumbButtons = document.querySelectorAll('[data-thumb-button]');

    if (!mainImage || !thumbButtons.length) {
        return;
    }

    thumbButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const imageUrl = button.getAttribute('data-image-url');
            const imageAlt = button.getAttribute('data-image-alt') || '';

            if (!imageUrl) {
                return;
            }

            mainImage.src = imageUrl;
            mainImage.alt = imageAlt;

            thumbButtons.forEach((item) => item.classList.remove('is-active'));
            button.classList.add('is-active');
        });
    });
}
