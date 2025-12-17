let currentLinkData = null;
let customParamCounter = 0;
let isInitialized = false; // Флаг инициализации

export function setupEditLink() {
    const editBtns = document.querySelectorAll('.edit_generated_link');
    
    // Удаляем старые обработчики, чтобы избежать дублирования
    editBtns.forEach(btn => {
        btn.removeEventListener('click', handleEditClick);
        btn.addEventListener('click', handleEditClick);
    });
}

// Обработчик клика по кнопке редактирования
function handleEditClick() {
    // Первоначальная настройка данных
    const dataset = this.dataset;

    const requiredParams = JSON.parse(dataset.linkParams.replace(/'/g, '"'));
    document.getElementById('currentLinkDisplay').value = dataset.linkUrl;
    document.getElementById('previewLinkDisplay').value = dataset.linkUrl;
    document.getElementById('fixedPidDisplay').value = dataset.linkId;
    const linkUrl = new URL(dataset.linkUrl);
    currentLinkData = {
        url: linkUrl.toString(),
        id: linkUrl.searchParams.get('pid'),
        base_url: linkUrl.origin
    }

    // Очищаем предыдущие параметры
    clearCustomParams();
    
    // Текущие параметры
    displayExistingParams(linkUrl.searchParams, requiredParams);

    // Добавление новых параметров (инициализируем только один раз)
    if (!isInitialized) {
        initCustomParamsSystem();
        isInitialized = true;
    }

    // Настройка формы изменения
    document.getElementById('edit_partner_link_form').action = `/partner/edit_partner_link/${dataset.linkId}`;

    document.getElementById('editPartnerLinkModal').show();
}

// Очистка кастомных параметров
function clearCustomParams() {
    const customParamsList = document.getElementById('customParamsList');
    const noCustomParamsMessage = document.getElementById('noCustomParamsMessage');
    
    customParamsList.innerHTML = '';
    customParamCounter = 0;
    noCustomParamsMessage.style.display = 'block';
}

// СУЩЕСТВУЮЩИЕ ПАРАМЕТРЫ
function displayExistingParams(params, requiredParams) {
    const container = document.getElementById('existingParamsList');
    const noParamsMsg = document.getElementById('noExistingParamsMessage');

    container.innerHTML = '';

    // Получаем все параметры кроме pid
    const paramsArray = Array.from(params.entries());

    // Получаем все параметры кроме pid
    const otherParams = paramsArray.filter(([key]) => key !== 'pid');

    if (otherParams.length === 0) {
        noParamsMsg.style.display = 'block';
        return;
    }

    noParamsMsg.style.display = 'none';

    otherParams.forEach(([key, value]) => {
        let isRequired = requiredParams.includes(key);

        console.log(isRequired, key, requiredParams)
        const paramElement = createExistingParamElement(key, value, isRequired);
        container.appendChild(paramElement);
    });
}

function createExistingParamElement(key, value, isRequiredParam = false) {
    const div = document.createElement('div');
    div.className = 'existing-param-item bg-base-100 p-3 rounded-lg border border-base-300 flex items-center justify-between mb-2';
    div.dataset.key = key;
    div.dataset.currentValue = value;

    div.innerHTML = `
        <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-sm opacity-70">Ключ</span>
                ${isRequiredParam ? '<span class="badge badge-xs badge-error">Обязательный</span>' : ''}
            </div>
            <div class="font-mono bg-base-200 px-2 py-1 rounded text-sm">${escapeHtml(key)}</div>
        </div>
        <div class="flex-1 mx-4">
            <div class="font-medium text-sm opacity-70 mb-1">Значение</div>
            <div class="flex items-center gap-2">
                <div class="value-display font-mono bg-base-200 px-2 py-1 rounded text-sm truncate flex-1 min-w-0">
                    ${escapeHtml(value)}
                </div>
                <button type="button" class="edit-value-btn btn btn-sm btn-outline btn-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                </button>
            </div>
            <div class="value-edit hidden mt-2">
                <div class="flex items-center gap-2">
                    <input type="text" 
                           class="value-edit-input input input-bordered input-sm flex-1" 
                           value="${escapeHtml(value)}"
                           placeholder="Введите новое значение">
                    <div class="flex gap-1">
                        <button type="button" class="save-value-btn btn btn-sm btn-success">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                        </button>
                        <button type="button" class="cancel-edit-btn btn btn-sm btn-ghost">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div class="flex items-center gap-2">
    `;

    // Кнопка удаления (только для необязательных параметров)
    if (!isRequiredParam) {
        div.innerHTML += `
            <button type="button" class="remove-existing-param-btn btn btn-sm btn-outline btn-error">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Удалить
            </button>
        `;
    }

    div.innerHTML += `</div>`;

    // Получаем элементы
    const editBtn = div.querySelector('.edit-value-btn');
    const removeBtn = div.querySelector('.remove-existing-param-btn');
    const valueDisplay = div.querySelector('.value-display');
    const valueEdit = div.querySelector('.value-edit');
    const valueInput = div.querySelector('.value-edit-input');
    const saveBtn = div.querySelector('.save-value-btn');
    const cancelBtn = div.querySelector('.cancel-edit-btn');

    // Функция переключения в режим редактирования
    if (editBtn) {
        editBtn.addEventListener('click', function () {
            // Скрываем отображение, показываем поле редактирования
            valueDisplay.classList.add('hidden');
            valueEdit.classList.remove('hidden');
            
            // Фокусируемся на поле ввода и выделяем текст
            valueInput.focus();
            valueInput.select();
        });
    }

    // Функция сохранения значения
    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            const newValue = valueInput.value.trim();
            
            if (newValue === '') {
                alert('Значение не может быть пустым');
                valueInput.focus();
                return;
            }
            
            // Обновляем отображение
            valueDisplay.textContent = newValue;
            div.dataset.currentValue = newValue;
            
            // Возвращаемся к режиму отображения
            valueDisplay.classList.remove('hidden');
            valueEdit.classList.add('hidden');
            
            // Обновляем предпросмотр ссылки
            updatePreview();
        });
    }

    // Функция отмены редактирования
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function () {
            // Возвращаем исходное значение
            valueInput.value = div.dataset.currentValue;
            
            // Возвращаемся к режиму отображения
            valueDisplay.classList.remove('hidden');
            valueEdit.classList.add('hidden');
        });
    }

    // Сохранение по нажатию Enter, отмена по Escape
    if (valueInput) {
        valueInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && saveBtn) {
                saveBtn.click();
            } else if (e.key === 'Escape' && cancelBtn) {
                cancelBtn.click();
            }
        });
    }

    // Функция удаления параметра (только для необязательных)
    if (removeBtn) {
        removeBtn.addEventListener('click', function () {
            if (confirm(`Удалить параметр "${key}"?`)) {
                div.remove();
                updatePreview();

                // Показываем сообщение если не осталось параметров
                const container = document.getElementById('existingParamsList');
                const noParamsMsg = document.getElementById('noExistingParamsMessage');

                if (container.children.length === 0) {
                    noParamsMsg.style.display = 'block';
                }
                
                showNotification(`Параметр "${key}" удален`, 'success');
            }
        });
    }

    return div;
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Функция для показа уведомлений
function showNotification(message, type = 'info') {
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-sm`;
    notification.innerHTML = `
        <div class="flex items-center gap-2">
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    // Удаляем через 3 секунды
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ДОБАВЛЕНИЕ НОВЫХ ПАРАМЕТРОВ 
function initCustomParamsSystem() {
    const customParamsList = document.getElementById('customParamsList');
    const noCustomParamsMessage = document.getElementById('noCustomParamsMessage');
    const addCustomParamBtn = document.getElementById('addCustomParamBtn');

    customParamCounter = 0;

    // Очищаем старый обработчик, чтобы избежать дублирования
    addCustomParamBtn.removeEventListener('click', addCustomParamHandler);
    
    // Функция-обработчик для добавления параметра
    function addCustomParamHandler() {
        addCustomParameter();
        updateCustomParamsVisibility();
    }
    
    addCustomParamBtn.addEventListener('click', addCustomParamHandler);

    // Функция добавления нового параметра
    function addCustomParameter(key = '', value = '') {
        customParamCounter++;

        // Скрываем сообщение "нет параметров"
        noCustomParamsMessage.style.display = 'none';

        const paramElement = document.createElement('div');
        paramElement.className = 'custom-param-item bg-base-100 p-3 rounded-lg border border-base-300';
        paramElement.dataset.index = customParamCounter;

        paramElement.innerHTML = `
            <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1">
                            <span class="label-text font-medium">Ключ параметра</span>
                        </label>
                        <input type="text" 
                               class="custom-param-key input input-bordered input-sm w-full" 
                               placeholder="Например: utm_source" 
                               value="${key}"
                               data-original="${key}">
                        <div class="text-xs text-warning mt-1 flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.698-.833-2.464 0L4.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                            Только латинские буквы, цифры и подчеркивания
                        </div>
                    </div>
                    <div class="form-control">
                        <label class="label py-1">
                            <span class="label-text font-medium">Значение параметра</span>
                        </label>
                        <input type="text" 
                               class="custom-param-value input input-bordered input-sm w-full" 
                               placeholder="Например: telegram" 
                               value="${value}"
                               data-original="${value}">
                    </div>
                </div>
                <div class="flex gap-2 mt-2 sm:mt-0 sm:ml-2">
                    <button type="button" class="btn btn-sm btn-square btn-outline btn-success save-param-btn" title="Сохранить параметр">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                    </button>
                    <button type="button" class="btn btn-sm btn-square btn-outline btn-error remove-param-btn" title="Удалить параметр">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>
            <div class="param-status mt-2 hidden">
                <span class="text-xs badge badge-success">✓ Готово</span>
            </div>
        `;

        customParamsList.appendChild(paramElement);

        // Обработчики событий
        const keyInput = paramElement.querySelector('.custom-param-key');
        const valueInput = paramElement.querySelector('.custom-param-value');
        const removeBtn = paramElement.querySelector('.remove-param-btn');
        const saveBtn = paramElement.querySelector('.save-param-btn');
        const statusDiv = paramElement.querySelector('.param-status');

        // Валидация ключа
        keyInput.addEventListener('input', function (e) {
            e.target.value = e.target.value.replace(/[^a-zA-Z0-9_]/g, '');
            updatePreview();
        });

        valueInput.addEventListener('input', updatePreview);

        // Удаление параметра
        removeBtn.addEventListener('click', function () {
            paramElement.remove();
            updateCustomParamsVisibility();
            updatePreview();
        });

        // Сохранение параметра (добавление в существующие)
        saveBtn.addEventListener('click', function () {
            const key = keyInput.value.trim();
            const value = valueInput.value.trim();

            if (key && value) {
                // Добавляем в существующие параметры
                addToExistingParams(key, value);

                // Удаляем из новых параметров
                paramElement.remove();
                updateCustomParamsVisibility();
            }
        });

        // Отслеживание изменений
        keyInput.addEventListener('input', function () {
            const hasChanges = keyInput.value !== keyInput.dataset.original ||
                valueInput.value !== valueInput.dataset.original;
            saveBtn.disabled = !hasChanges;
        });

        valueInput.addEventListener('input', function () {
            const hasChanges = keyInput.value !== keyInput.dataset.original ||
                valueInput.value !== valueInput.dataset.original;
            saveBtn.disabled = !hasChanges;
        });

        return paramElement;
    }

    // Функция обновления видимости
    function updateCustomParamsVisibility() {
        const hasCustomParams = customParamsList.children.length > 0;
        noCustomParamsMessage.style.display = hasCustomParams ? 'none' : 'block';
    }

    // Инициализация
    updateCustomParamsVisibility();
}

// Добавление параметра в существующие
function addToExistingParams(key, value) {
    const container = document.getElementById('existingParamsList');
    const noParamsMsg = document.getElementById('noExistingParamsMessage');

    noParamsMsg.style.display = 'none';

    const paramElement = createExistingParamElement(key, value);
    container.appendChild(paramElement);

    // Обновляем предпросмотр
    updatePreview();
}


// ПРЕДПРОСМОТР НОВОЙ ССЫЛКИ
function updatePreview() {
    if (!currentLinkData) return;

    try {
        const baseUrl = currentLinkData.base_url;
        const pid = currentLinkData.id;
        const allParams = { pid: pid.toString() };

        // Существующие параметры из data-атрибутов
        document.querySelectorAll('.existing-param-item').forEach(item => {
            const key = item.dataset.key;
            const value = item.dataset.currentValue || item.dataset.value;
            if (key && value) {
                allParams[key] = value;
            }
        });

        // Новые параметры из инпутов
        document.querySelectorAll('.custom-param-item').forEach(item => {
            const keyInput = item.querySelector('.custom-param-key');
            const valueInput = item.querySelector('.custom-param-value');

            const key = keyInput?.value?.trim();
            const value = valueInput?.value?.trim();

            if (key && value) {
                allParams[key] = value;
            }
        });

        // Формируем URL
        const url = new URL(baseUrl);
        Object.entries(allParams).forEach(([key, value]) => {
            if (value) {
                url.searchParams.set(key, value);
            }
        });

        document.getElementById('previewLinkDisplay').value = url.toString();

    } catch (error) {
        console.error('Ошибка обновления предпросмотра:', error);
    }
}

// Удаляем глобальный обработчик, чтобы избежать дублирования
document.removeEventListener('click', previewUpdateHandler);
document.removeEventListener('input', previewInputHandler);

// Создаем именованные функции для обработчиков
function previewUpdateHandler(e) {
    if (e.target.closest('.remove-existing-param-btn')) {
        setTimeout(updatePreview, 50);
    }
}

function previewInputHandler(e) {
    if (e.target.closest('.custom-param-key') || e.target.closest('.custom-param-value')) {
        // Дебаунс для производительности
        clearTimeout(window.previewUpdateTimeout);
        window.previewUpdateTimeout = setTimeout(updatePreview, 100);
    }
}

// Настройка обновления предпросмотра
function setupPreviewUpdates() {
    document.addEventListener('click', previewUpdateHandler);
    document.addEventListener('input', previewInputHandler);
}

// Инициализируем обновление предпросмотра один раз
setupPreviewUpdates();