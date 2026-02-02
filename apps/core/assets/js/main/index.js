import '@fortawesome/fontawesome-free/js/all'
import '../../css/main/index.css'

import { setupFeedback } from './feedback';

// ==================== КОНФИГУРАЦИЯ И КОНСТАНТЫ ====================
const MODAL_CONFIG = {
    partner: {
        icon: "fas fa-user-plus text-4xl text-blue-600 mb-4",
        title: "Регистрация партнёра",
        subtitle: "Начните зарабатывать с нами"
    },
    advertiser: {
        icon: "fas fa-bullhorn text-4xl text-green-500 mb-4",
        title: "Регистрация рекламодателя",
        subtitle: "Привлекайте новых клиентов"
    }
};

// ==================== УТИЛИТЫ ====================
const DOMUtils = {
    get: (id) => document.getElementById(id),
    getAll: (selector) => document.querySelectorAll(selector),
    create: (tag) => document.createElement(tag)
};

const UIHelpers = {
    // Плавная прокрутка
    initSmoothScrolling: () => {
        DOMUtils.getAll('a[href^="#"]').forEach((anchor) => {
            anchor.addEventListener("click", (e) => {
                e.preventDefault();
                const targetElement = DOMUtils.get(anchor.getAttribute("href").substring(1));
                targetElement?.scrollIntoView({ behavior: "smooth" });
            });
        });
    },

    // Эффект навигационной панели при прокрутке
    initNavbarScrollEffect: () => {
        window.addEventListener("scroll", () => {
            const navbar = DOMUtils.get("navbar");
            navbar?.classList.toggle("scrolled", window.scrollY > 50);
        });
    }
};

// ==================== УПРАВЛЕНИЕ МОДАЛЬНЫМИ ОКНАМИ ====================
const ModalManager = {
    currentType: "partner",

    // Инициализация всех обработчиков модальных окон
    init: () => {
        ModalManager.setupAuthModal();
        ModalManager.setupRegistrationModals();
        ModalManager.setupTabSwitching();
        ModalManager.setupModalLinks();
    },

    // Модальное окно авторизации
    setupAuthModal: () => {
        const authBtn = DOMUtils.get("authModal");
        authBtn?.addEventListener("click", () => ModalManager.openModal("auth"));
    },

    // Модальные окна регистрации
    setupRegistrationModals: () => {
        const buttons = {
            reg_partner: DOMUtils.get("reg_partner-btn"),
            reg_advertiser: DOMUtils.get("reg_advertiser-btn"),
            become_partner: DOMUtils.get("become_partner"),
            become_advertiser: DOMUtils.get("become_advertiser")
        };

        buttons.reg_partner?.addEventListener("click", () => ModalManager.openModal('register', 'partner'));
        buttons.reg_advertiser?.addEventListener("click", () => ModalManager.openModal('register', 'advertiser'));
        buttons.become_partner?.addEventListener("click", () => ModalManager.openModal('register', 'partner'));
        buttons.become_advertiser?.addEventListener("click", () => ModalManager.openModal('register', 'advertiser'));
    },

    // Переключение вкладок
    setupTabSwitching: () => {
        const tabs = {
            partner: DOMUtils.get("tab-partner"),
            advertiser: DOMUtils.get("tab-advertiser"),
            partner_tab: DOMUtils.get("partner-tab"),
            advertiser_tab: DOMUtils.get("advertiser-tab")
        };

        tabs.partner?.addEventListener("click", () => ModalManager.openModal('register', 'partner'));
        tabs.advertiser?.addEventListener("click", () => ModalManager.openModal('register', 'advertiser'));
        tabs.partner_tab?.addEventListener("click", () => TabManager.switchTab("partner"));
        tabs.advertiser_tab?.addEventListener("click", () => TabManager.switchTab("advertiser"));
    },

    // Ссылки между модальными окнами
    setupModalLinks: () => {
        const registrationLink = DOMUtils.get("registration-link");
        const authorizationLink = DOMUtils.get("authorization-Link");

        registrationLink?.addEventListener("click", () => {
            ModalManager.closeModal('auth');
            ModalManager.openModal('register', 'partner');
        });

        authorizationLink?.addEventListener("click", () => {
            ModalManager.closeModal('register');
            ModalManager.openModal('auth');
        });
    },

    // Открытие модального окна
    openModal: (type, userType = "partner") => {
        if (type === "register") {
            ModalManager.currentType = userType;
            ModalManager.switchModalTab(userType);
        }
        DOMUtils.get(`${type}_modal`)?.showModal();
    },

    // Закрытие модального окна
    closeModal: (type) => {
        DOMUtils.get(`${type}_modal`)?.close();
    },

    // Переключение вкладок в модальном окне
    switchModalTab: (type) => {
        const tabs = {
            partner: DOMUtils.get("tab-partner"),
            advertiser: DOMUtils.get("tab-advertiser")
        };

        const forms = {
            partner: DOMUtils.get("form-partner"),
            advertiser: DOMUtils.get("form-advertiser")
        };

        // Управление классами вкладок и форм
        Object.keys(tabs).forEach((key) => {
            const isActive = key === type;
            tabs[key]?.classList.toggle("tab-active", isActive);
            forms[key]?.classList.toggle("hidden", !isActive);
            forms[key]?.classList.toggle("active_reg-form", isActive);
        });

        // Обновление UI
        ModalManager.updateModalUI(type);
    },

    // Обновление интерфейса модального окна
    updateModalUI: (type) => {
        const regHeader = DOMUtils.get("reg-header");
        const oldIcon = DOMUtils.get("reg-icon");
        const title = DOMUtils.get("reg-title");
        const subtitle = DOMUtils.get("reg-subtitle");

        if (!regHeader || !title || !subtitle) return;

        // Удаляем старую иконку
        oldIcon?.remove();

        // Создаем новую иконку
        const icon = DOMUtils.create("i");
        const config = MODAL_CONFIG[type];

        icon.className = config.icon;
        icon.id = "reg-icon";
        icon.style.margin = "0 auto";

        regHeader.prepend(icon);
        title.textContent = config.title;
        subtitle.textContent = config.subtitle;
    }
};

// ==================== УПРАВЛЕНИЕ ВКЛАДКАМИ ====================
const TabManager = {
    // Переключение вкладок
    switchTab: (tabType) => {
        // Удаляем активные классы
        DOMUtils.getAll(".tab").forEach((tab) => tab.classList.remove("tab-active"));
        DOMUtils.getAll(".tab-content").forEach((content) => content.classList.remove("active"));

        // Добавляем активные классы
        DOMUtils.get(`${tabType}-tab`)?.classList.add("tab-active");
        DOMUtils.get(`${tabType}-content`)?.classList.add("active");
    }
};

// ==================== ОБРАБОТКА URL ПАРАМЕТРОВ ====================
const URLParamsHandler = {
    // Обработка параметров URL
    handleURLParams: () => {
        const urlParams = new URLSearchParams(window.location.search);
        const modalType = urlParams.get('show_modal');

        if (modalType === "auth") {
            URLParamsHandler.openAuthModal();
        } else if (modalType === "partner" || modalType === "advertiser") {
            URLParamsHandler.openRegistrationModal(modalType);
        }
    },

    // Открытие модального окна авторизации
    openAuthModal: () => {
        const state = { url: `/`, title: "LinkOffer - Партнёрская программа" };
        window.history.pushState(state, state.title, state.url);
        window.addEventListener("DOMContentLoaded", () => {
            setTimeout(() => DOMUtils.get("auth_modal")?.showModal(), 505);
            
        });
    },

    // Открытие модального окна регистрации
    openRegistrationModal: (type) => {
        const state = { url: `/`, title: "LinkOffer - Партнёрская программа" };
        window.history.pushState(state, state.title, state.url);
        ModalManager.switchModalTab(type);
        setTimeout(() => DOMUtils.get('register_modal')?.showModal(), 505);
    }
};



// Стили для анимации
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

// ==================== ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ====================
const App = {
    init: () => {
        UIHelpers.initSmoothScrolling();
        UIHelpers.initNavbarScrollEffect();

        ModalManager.init();

        URLParamsHandler.handleURLParams();
    }
};


// Запуск приложения после загрузки DOM
document.addEventListener("DOMContentLoaded", function () {

    App.init();

    addAlertStyles();

    // setupFeedback();
});