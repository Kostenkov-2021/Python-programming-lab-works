/**
 * Основной JavaScript файл для Currency Tracker
 * Содержит общие функции и обработчики событий
 */

// Глобальные переменные
let currentUserId = null;
let chartInstances = {};

/**
 * Инициализация приложения при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Currency Tracker initialized');
    
    // Проверка наличия сохраненного пользователя
    const savedUserId = localStorage.getItem('currentUserId');
    if (savedUserId) {
        currentUserId = parseInt(savedUserId);
        updateUserInfo(savedUserId);
    }
    
    // Инициализация всех графиков на странице
    initAllCharts();
    
    // Настройка обработчиков событий
    setupEventListeners();
    
    // Автоматическое обновление данных (каждые 5 минут)
    startAutoRefresh();
});

/**
 * Инициализация всех графиков Chart.js на странице
 */
function initAllCharts() {
    const chartElements = document.querySelectorAll('canvas[data-chart]');
    
    chartElements.forEach((canvas, index) => {
        const chartType = canvas.getAttribute('data-chart-type') || 'line';
        const chartData = JSON.parse(canvas.getAttribute('data-chart-data') || '{}');
        const chartOptions = JSON.parse(canvas.getAttribute('data-chart-options') || '{}');
        
        if (chartData && Object.keys(chartData).length > 0) {
            const ctx = canvas.getContext('2d');
            chartInstances[`chart-${index}`] = new Chart(ctx, {
                type: chartType,
                data: chartData,
                options: chartOptions
            });
        }
    });
}

/**
 * Настройка обработчиков событий
 */
function setupEventListeners() {
    // Обработчики для модальных окон
    setupModalListeners();
    
    // Обработчики для форм
    setupFormListeners();
    
    // Обработчики для кнопок обновления
    document.querySelectorAll('.btn-refresh').forEach(button => {
        button.addEventListener('click', handleRefresh);
    });
}

/**
 * Настройка обработчиков для модальных окон
 */
function setupModalListeners() {
    // Закрытие модальных окон при клике на фон
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(event) {
            if (event.target === this) {
                this.style.display = 'none';
            }
        });
    });
    
    // Закрытие модальных окон при нажатии Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.style.display = 'none';
            });
        }
    });
}

/**
 * Настройка обработчиков для форм
 */
function setupFormListeners() {
    // Валидация форм
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Валидация формы
 */
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showInputError(input, 'Это поле обязательно для заполнения');
            isValid = false;
        } else {
            clearInputError(input);
        }
    });
    
    return isValid;
}

/**
 * Показать ошибку для поля ввода
 */
function showInputError(input, message) {
    const formGroup = input.closest('.form-group');
    if (!formGroup) return;
    
    // Удаляем старую ошибку
    const oldError = formGroup.querySelector('.error-message');
    if (oldError) oldError.remove();
    
    // Добавляем новую ошибку
    const error = document.createElement('div');
    error.className = 'error-message';
    error.style.color = '#e74c3c';
    error.style.fontSize = '0.9em';
    error.style.marginTop = '5px';
    error.textContent = message;
    
    formGroup.appendChild(error);
    input.style.borderColor = '#e74c3c';
}

/**
 * Очистить ошибку поля ввода
 */
function clearInputError(input) {
    const formGroup = input.closest('.form-group');
    if (!formGroup) return;
    
    const error = formGroup.querySelector('.error-message');
    if (error) error.remove();
    
    input.style.borderColor = '';
}

/**
 * Обработка обновления данных
 */
function handleRefresh(event) {
    event.preventDefault();
    
    const button = event.currentTarget;
    const originalText = button.innerHTML;
    
    // Показываем индикатор загрузки
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обновление...';
    button.disabled = true;
    
    // Симуляция загрузки
    setTimeout(() => {
        location.reload();
    }, 1000);
}

/**
 * Обновление информации о текущем пользователе
 */
function updateUserInfo(userId) {
    // Здесь можно добавить запрос к API для получения информации о пользователе
    console.log('Current user ID:', userId);
    
    // Обновляем интерфейс
    updateUIForUser(userId);
}

/**
 * Обновление интерфейса для пользователя
 */
function updateUIForUser(userId) {
    // Обновляем элементы, зависящие от пользователя
    document.querySelectorAll('[data-show-if-user]').forEach(element => {
        element.style.display = 'block';
    });
    
    document.querySelectorAll('[data-hide-if-user]').forEach(element => {
        element.style.display = 'none';
    });
    
    // Обновляем текст приветствия
    const greetingElement = document.getElementById('userGreeting');
    if (greetingElement) {
        greetingElement.textContent = `Вы вошли как пользователь #${userId}`;
    }
}

/**
 * Запуск автоматического обновления данных
 */
function startAutoRefresh() {
    // Обновляем каждые 5 минут (300000 мс)
    setTimeout(() => {
        if (confirm('Хотите обновить данные?')) {
            location.reload();
        } else {
            // Повторяем через 5 минут
            startAutoRefresh();
        }
    }, 300000);
}

/**
 * Показать уведомление
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Стили для уведомления
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        min-width: 300px;
        max-width: 400px;
        animation: slideIn 0.3s ease;
    `;
    
    // Анимация
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Загрузка данных с API
 */
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        showNotification('Ошибка при загрузке данных', 'error');
        throw error;
    }
}

/**
 * Форматирование даты
 */
function formatDate(date, format = 'ru-RU') {
    const d = new Date(date);
    return d.toLocaleDateString(format, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Форматирование числа (валюты)
 */
function formatCurrency(value, currency = 'RUB') {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 4
    }).format(value);
}

/**
 * Анимация загрузки
 */
function showLoading(element) {
    if (element) {
        const originalContent = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';
        element.disabled = true;
        
        // Возвращаем функцию для восстановления состояния
        return () => {
            element.innerHTML = originalContent;
            element.disabled = false;
        };
    }
    return () => {};
}

// Экспорт функций в глобальную область видимости
window.showNotification = showNotification;
window.formatDate = formatDate;
window.formatCurrency = formatCurrency;
window.fetchData = fetchData;