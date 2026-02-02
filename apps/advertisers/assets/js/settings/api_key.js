function generateApiKey() {
  const prefix = 'sk-';
  const length = 25;
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';

  const crypto = window.crypto || window.msCrypto;
  const values = new Uint32Array(length);
  crypto.getRandomValues(values);

  let key = prefix;
  for (let i = 0; i < length; i++) {
    key += chars[values[i] % chars.length];
  }

  return key;
}

export function setupApiKeySettings() {
  const btnGenerate = document.getElementById('generate_api_key');
  const btnCopy = document.getElementById('copy_api_key');

  const apiKeyInput = document.getElementById('api_key');
  const apiKeyShowBtn = document.getElementById('show_api_key');

  apiKeyShowBtn.addEventListener('click', () => {
    if (apiKeyInput.type === 'password') {
      apiKeyInput.type = 'text';
    } else {
      apiKeyInput.type = 'password';
    }
  })


  if (btnGenerate) {
    btnGenerate.addEventListener('click', () => {
      document.getElementById('api_key').value = generateApiKey();
    });
  }

  if (btnCopy) {
    btnCopy.addEventListener('click', async () => {
      addAlertStyles();
      const apiKeyElement = document.getElementById('api_key');

      if (!apiKeyElement) {
        showAlert('Ошибка: поле с ключом не найдено', 'error');
        return;
      }

      const apiKey = apiKeyElement.value;

      if (!apiKey) {
        showAlert('Нет ключа для копирования', 'warning');
        return;
      }

      if (!navigator.clipboard) {
        fallbackCopy(apiKey);
        return;
      }

      try {
        await navigator.clipboard.writeText(apiKey);
        showAlert('API ключ скопирован!', 'success');
        updateButtonState(btnCopy, true);
      } catch (err) {
        fallbackCopy(apiKey);
      }
    });
  }

  function fallbackCopy(text) {
    try {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed'; 
      document.body.appendChild(textarea);
      textarea.select();

      const successful = document.execCommand('copy');
      document.body.removeChild(textarea);

      if (successful) {
        showAlert('API ключ скопирован', 'success');
      } else {
        throw new Error('Резервное копирование не удалось');
      }
    } catch (err) {
      showAlert('Не удалось скопировать ключ. Скопируйте вручную.', 'error');
    }
  }

  // Обновление состояния кнопки
  function updateButtonState(button, success) {
    if (success) {
      button.innerHTML = '<i class="fas fa-check"></i>';
      button.classList.add('btn-success');
      setTimeout(() => {
        button.innerHTML = '<i class="fas fa-copy"></i>';
        button.classList.remove('btn-success');
      }, 2000);
    } else {
      button.innerHTML = '<i class="fas fa-times"></i> Ошибка';
      button.classList.add('btn-error');
      setTimeout(() => {
        button.innerHTML = '<i class="fas fa-copy"></i> Копировать';
        button.classList.remove('btn-error');
      }, 2000);
    }
  }
  function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    const alertClass = `alert-${type}`;
    const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';

    alert.className = `alert-message alert ${alertClass} text-white p-4 mr-6 mb-6 transition-all duration-300 ease-out shadow-lg animate-fade-in`;
    alert.innerHTML = `<i class="fas ${iconClass} mr-2"></i>${message}`;
    document.getElementById('settings_messages__container').appendChild(alert);

    setTimeout(() => {
      alert.classList.add('animate-slide-out-left','transform-gpu','transition-all','duration-800','ease-in-out');
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  }
}

const addAlertStyles = () => {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slide-out-left {
            0% {
                opacity: 1;
                transform: translateX(0);
            }
            70% {
                opacity: 0;
                transform: translateX(+100%);
            }
            100% {
                opacity: 0;
                transform: translateX(+100%);
                max-height: 0;
                margin-bottom: 0;
                padding: 0;
                border: none;
            }
        }
        
        .animate-slide-out-left {
            animation: slide-out-left 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            pointer-events: none;
        }
    `;
    document.head.appendChild(style);
};