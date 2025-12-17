// Глобальные переменные
let customParamCounter = 0;
let currentParams = [];
let currentBaseUrl = '';
let currentPid = '';
let currentPartnershipId = '';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция инициализации
export function setupProjectGenerateLink() {
    const generateBtns = document.querySelectorAll('.generate_partner_link');
    const copyBtn = document.getElementById('copyLinkBtn');
    const generatedLinkContainer = document.getElementById('generatedLinkContainer');
    const generatedLinkInput = document.getElementById('generatedLink');
    const paramsControls = document.getElementById('paramsControls');
    const generateLinkBtn = document.getElementById('generateLinkBtn');
    const fixedPidInput = document.getElementById('fixedPidInput');
    const customParamsList = document.getElementById('customParamsList');
    const noCustomParamsMessage = document.getElementById('noCustomParamsMessage');
    const addCustomParamBtn = document.getElementById('addCustomParamBtn');
    const requiredParamsError = document.getElementById('requiredParamsError');
    const partnerLinkModal = document.getElementById('partnerLinkModal');

    // Флаг, чтобы отслеживать, был ли сгенерирован ID для текущего открытия модалки
    let isPidGeneratedForCurrentModal = false;

    // Открытие модального окна
    generateBtns.forEach(generateBtn => {
        generateBtn.addEventListener('click', async function () {
            try {
                // Сбрасываем флаг при каждом новом открытии
                isPidGeneratedForCurrentModal = false;
                
                // Сохраняем текущие данные
                currentPartnershipId = this.dataset.partnership;
                currentBaseUrl = this.dataset.projectLink;
                currentParams = JSON.parse(this.dataset.projectParams);
                
                // Очищаем предыдущий PID - он будет сгенерирован позже
                currentPid = '';
                fixedPidInput.value = 'Здесь будет ID cсылки';

                // Очищаем контейнеры
                paramsControls.innerHTML = '';
                customParamsList.innerHTML = '';
                generatedLinkInput.value = 'Здесь будет ваша ссылка';
                updateCustomParamsVisibility();

                // Сбрасываем состояние кнопки генерации
                generateLinkBtn.disabled = false;
                generateLinkBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    Сгенерировать ссылку
                `;
                requiredParamsError.classList.add('hidden');

                // Добавляем стандартные параметры (кроме pid)
                currentParams
                    .filter(param => param.name !== 'pid')
                    .forEach(param => {
                        const paramControl = document.createElement('div');
                        paramControl.className = 'flex flex-col sm:flex-row items-start sm:items-center gap-3 p-3 bg-base-100 rounded-lg';
                        paramControl.id = `param_${param.name}`;

                        const label = document.createElement('label');
                        label.className = 'flex-1';
                        label.innerHTML = `
                            <span class="font-medium">${param.name}</span>
                            ${param.description ? `<span class="text-sm opacity-70 block">${param.description}</span>` : ''}
                            ${param.example_value ? `<span class="text-sm opacity-70 block">Пример: <code>${param.example_value}</code></span>` : ''}
                            ${param.param_type === 'required' ? `<span class="text-xs badge badge-error mt-1">Обязательный</span>` : '<span class="text-xs badge badge-info mt-1">Опциональный</span>'}
                        `;

                        const inputGroup = document.createElement('div');
                        inputGroup.className = 'flex items-center gap-2 w-full sm:w-auto';

                        // Для опциональных параметров добавляем чекбокс
                        if (param.param_type !== 'required') {
                            const checkbox = document.createElement('input');
                            checkbox.type = 'checkbox';
                            checkbox.className = 'toggle toggle-sm';
                            checkbox.checked = true;
                            checkbox.dataset.param = param.name;

                            checkbox.addEventListener('change', function () {
                                input.disabled = !this.checked;
                                validateRequiredParams();
                                updateGeneratedLink();
                            });

                            inputGroup.appendChild(checkbox);
                        }

                        // Поле ввода для параметра
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.placeholder = 'Введите значение';
                        input.className = 'input input-bordered input-sm flex-1 param-input';
                        input.dataset.param = param.name;
                        input.dataset.required = param.param_type === 'required';

                        if (param.param_type === 'required') {
                            input.required = true;
                        }

                        input.addEventListener('input', function () {
                            validateRequiredParams();
                            updateGeneratedLink();
                        });

                        input.addEventListener('blur', function () {
                            validateRequiredParams();
                        });

                        inputGroup.appendChild(input);
                        paramControl.appendChild(label);
                        paramControl.appendChild(inputGroup);
                        paramsControls.appendChild(paramControl);
                    });

                generatedLinkContainer.classList.remove('hidden');
                validateRequiredParams();

            } catch (error) {
                console.error('Ошибка парсинга параметров:', error);
                alert('Ошибка при обработке параметров ссылки');
            }
        });
    });

    // Функция валидации обязательных параметров
    function validateRequiredParams() {
        let isValid = true;
        const requiredInputs = document.querySelectorAll('.param-input[data-required="true"]');

        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                const paramControl = input.closest('.flex-col, .flex-row');
                if (paramControl) {
                    paramControl.classList.add('border', 'border-error');
                    input.classList.add('input-error');
                }
            } else {
                const paramControl = input.closest('.flex-col, .flex-row');
                if (paramControl) {
                    paramControl.classList.remove('border', 'border-error');
                    input.classList.remove('input-error');
                }
            }
        });

        // Проверка пользовательских обязательных параметров
        const customRequiredInputs = document.querySelectorAll('.custom-param-value[required]');
        customRequiredInputs.forEach(input => {
            const keyInput = input.closest('.custom-param-item')?.querySelector('.custom-param-key');
            if (keyInput && keyInput.value.trim() && !input.value.trim()) {
                isValid = false;
                input.closest('.custom-param-item').classList.add('border-error');
            }
        });

        // Обновление состояния кнопки и сообщения об ошибке
        generateLinkBtn.disabled = !isValid;
        requiredParamsError.classList.toggle('hidden', isValid);

        if (!isValid) {
            generateLinkBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.698-.833-2.464 0L4.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                Заполните обязательные параметры
            `;
            generateLinkBtn.classList.add('btn-disabled');
        } else {
            generateLinkBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Сгенерировать ссылку
            `;
            generateLinkBtn.classList.remove('btn-disabled');
        }

        return isValid;
    }

    // Функция обновления сгенерированной ссылки
    function updateGeneratedLink() {
        try {
            if (!currentPid) {
                generatedLinkInput.value = '';
                return;
            }
            
            const url = new URL(currentBaseUrl);
            url.searchParams.set('pid', currentPid);

            // Обработка стандартных параметров
            document.querySelectorAll('#paramsControls .param-input').forEach(input => {
                const paramName = input.dataset.param;
                const paramConfig = currentParams.find(p => p.name === paramName);

                if (!paramConfig) return;

                const isRequired = paramConfig.param_type === 'required';
                const hasCheckbox = paramConfig.param_type !== 'required';
                const isChecked = hasCheckbox ?
                    input.previousElementSibling?.checked : true;
                const hasValue = input.value.trim();

                if (isRequired && hasValue) {
                    url.searchParams.set(paramName, input.value.trim());
                } else if (!isRequired && isChecked && hasValue) {
                    url.searchParams.set(paramName, input.value.trim());
                } else if (!isRequired && !isChecked) {
                    url.searchParams.delete(paramName);
                }
            });

            // Обработка пользовательских параметров
            document.querySelectorAll('.custom-param-item').forEach(item => {
                const keyInput = item.querySelector('.custom-param-key');
                const valueInput = item.querySelector('.custom-param-value');

                if (keyInput && valueInput && keyInput.value.trim() && valueInput.value.trim()) {
                    url.searchParams.set(keyInput.value.trim(), valueInput.value.trim());
                }
            });

            generatedLinkInput.value = url.toString();
        } catch (error) {
            console.error('Ошибка генерации ссылки:', error);
        }
    }

    // Функция для добавления пользовательского параметра
    function addCustomParameter(key = '', value = '') {
        customParamCounter++;

        // Скрываем сообщение "нет параметров"
        noCustomParamsMessage.style.display = 'none';

        const paramId = `custom_param_${customParamCounter}`;

        const paramElement = document.createElement('div');
        paramElement.className = 'custom-param-item bg-base-100 p-3 rounded-lg border border-base-300';
        paramElement.id = paramId;

        paramElement.innerHTML = `
            <div class="flex flex-col sm:flex-row items-start sm:items-center gap-2">
                <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text font-medium">Ключ параметра</span>
                        </label>
                        <input type="text" 
                               name="custom_params_key[]" 
                               class="custom-param-key input input-bordered input-sm" 
                               placeholder="Например: utm_source" 
                               value="${key}"
                               required>
                        <div class="text-xs text-warning mt-1">Только латинские буквы, цифры и подчеркивания</div>
                    </div>
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text font-medium">Значение параметра</span>
                        </label>
                        <input type="text" 
                               name="custom_params_value[]" 
                               class="custom-param-value input input-bordered input-sm" 
                               placeholder="Например: telegram" 
                               value="${value}"
                               required>
                    </div>
                </div>
                <div class="flex gap-2 mt-2 sm:mt-0">
                    <button type="button" class="btn btn-sm btn-square btn-outline btn-error remove-param-btn" title="Удалить параметр">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>
        `;

        customParamsList.appendChild(paramElement);

        // Добавляем обработчики событий
        const removeBtn = paramElement.querySelector('.remove-param-btn');
        const keyInput = paramElement.querySelector('.custom-param-key');
        const valueInput = paramElement.querySelector('.custom-param-value');

        removeBtn.addEventListener('click', function () {
            paramElement.remove();
            updateCustomParamsVisibility();
            validateRequiredParams();
            updateGeneratedLink();
        });

        keyInput.addEventListener('input', function (e) {
            e.target.value = e.target.value.replace(/[^a-zA-Z0-9_]/g, '');
            validateRequiredParams();
            updateGeneratedLink();
        });

        valueInput.addEventListener('input', function () {
            validateRequiredParams();
            updateGeneratedLink();
        });

        valueInput.addEventListener('blur', function () {
            validateRequiredParams();
        });

        return paramElement;
    }

    // Функция обновления видимости контейнера пользовательских параметров
    function updateCustomParamsVisibility() {
        const hasCustomParams = customParamsList.children.length > 0;
        noCustomParamsMessage.style.display = hasCustomParams ? 'none' : 'block';
    }

    // Добавление пользовательского параметра по кнопке
    addCustomParamBtn.addEventListener('click', function () {
        addCustomParameter();
        validateRequiredParams();
    });

    // Инициализация при открытии модального окна
    partnerLinkModal.addEventListener('show', function () {
        customParamsList.innerHTML = '';
        updateCustomParamsVisibility();
    });

    // Обработка клика по кнопке генерации
    generateLinkBtn.addEventListener('click', async function (event) {
        event.preventDefault();

        if (!validateRequiredParams()) {
            alert('Пожалуйста, заполните все обязательные параметры');
            return;
        }

        try {
            // Показываем индикатор загрузки
            generateLinkBtn.disabled = true;
            generateLinkBtn.innerHTML = `
                <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Генерация ID...
            `;

            // Генерируем новый ID только если еще не генерировали для этого открытия модалки
            if (!isPidGeneratedForCurrentModal) {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', getCookie('XSRF-TOKEN'));
                
                const response = await fetch('/partner/generate_next_link_id', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Ошибка при генерации ID');
                }
                
                const data = await response.json();
                currentPid = data.partner_link_id;
                fixedPidInput.value = currentPid;
                isPidGeneratedForCurrentModal = true;
                
                // Обновляем ссылку с новым PID
                updateGeneratedLink();
            }

            // Показываем, что ссылка готова
            generateLinkBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Ссылка готова!
            `;

            // Ждем немного и отправляем форму
            setTimeout(() => {
                const form = document.getElementById('generate_partner_link_form');
                form.action = `/partner/generate_partner_link/${currentPartnershipId}`;
                
                // Добавляем скрытое поле с PID если его еще нет в форме
                if (!document.querySelector('input[name="pid"]')) {
                    const pidInput = document.createElement('input');
                    pidInput.type = 'hidden';
                    pidInput.name = 'pid';
                    pidInput.value = currentPid;
                    form.appendChild(pidInput);
                }
                
                form.submit();
            }, 1000);

        } catch (error) {
            console.error('Ошибка при генерации ссылки:', error);
            alert('Ошибка при генерации ID ссылки. Пожалуйста, попробуйте еще раз.');
            
            // Восстанавливаем кнопку
            generateLinkBtn.disabled = false;
            generateLinkBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Сгенерировать ссылку
            `;
        }
    });

    // Копирование ссылки
    copyBtn.addEventListener('click', function (event) {
        event.preventDefault();
        const textToCopy = generatedLinkInput.value;

        if (!textToCopy) {
            alert('Сначала сгенерируйте ссылку');
            return;
        }

        navigator.clipboard.writeText(textToCopy)
            .then(() => {
                const btn = copyBtn;
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check mr-2"></i> Скопировано!';
                btn.classList.add('btn-success');

                setTimeout(() => {
                    btn.innerHTML = originalHtml;
                    btn.classList.remove('btn-success');
                }, 2000);
            })
            .catch(err => {
                console.error('Ошибка копирования:', err);
                alert('Не удалось скопировать. Разрешите доступ к буферу обмена.');
            });
    });

    // Инициализация
    updateCustomParamsVisibility();
}