import '@fortawesome/fontawesome-free/js/all'
import '/apps/advertisers/assets/css/advertiser.css'

document.addEventListener('DOMContentLoaded', () => {
    // DOM элементы
    const refreshButton = document.getElementById('refresh-notifications');
    const notificationsList = document.getElementById('notifications-list');
    const loadingIndicator = document.getElementById('loading-indicator');
    const lastUpdated = document.getElementById('last-updated');
    const unreadCountElement = document.getElementById('unread-count');
    const totalCountElement = document.getElementById('total-count');
    const formMarkAllAsRead = document.getElementById('mark-all-as-read');

    initNotifications();

    function initNotifications() {
        setupPagination();
        setupEventListeners();
    }

    function setupPagination() {
        const prev = document.getElementById('previous_page_number');
        const curr = document.getElementById('current_page_number');
        const next = document.getElementById('next_page_number');
        const max = parseInt(curr.getAttribute('data-max'), 10);
        const searchParams = new URLSearchParams(window.location.search);
        let page = parseInt(searchParams.get('page')) || 1;

        if (page > max) page = 1;
        updateHistory(page);
        updatePaginationUI(page, max, prev, curr, next);

        prev.addEventListener('click', () => changePage(-1, page, max, prev, curr, next));
        next.addEventListener('click', () => changePage(1, page, max, prev, curr, next));
    }

    function changePage(step, page, max, prev, curr, next) {
        page = parseInt(curr.innerHTML) + step;
        if (page < 1 || page > max) return;

        updateHistory(page);
        refreshNotifications(page);
        updatePaginationUI(page, max, prev, curr, next);
    }

    function updatePaginationUI(page, max, prev, curr, next) {
        curr.innerHTML = page;
        prev.innerHTML = page > 1 ? page - 1 : '';
        prev.style.display = page > 1 ? 'block' : 'none';
        next.innerHTML = page < max ? page + 1 : '';
        next.style.display = page < max ? 'block' : 'none';
    }

    function updateHistory(page) {
        const state = { url: `/advertiser/notifications?page=${page}`, title: "Уведомления" };
        window.history.pushState(state, state.title, state.url);
    }

    function setupEventListeners() {
        refreshButton.addEventListener('click', () => {
            refreshNotifications().then(() => showToast('Уведомления обновлены', 'success'))
                .catch(() => showToast('Ошибка при обновлении', 'error'));
        });

        formMarkAllAsRead.addEventListener("submit", markAllAsRead);
        document.querySelectorAll("form.mark-as-read").forEach(form =>
            form.addEventListener("submit", handleMarkAsRead)
        );
    }

    async function refreshNotifications(page = null) {
        toggleLoading(true);
        try {
            const newNotifications = await fetchNotifications(page);
            renderNotifications(newNotifications);
            lastUpdated.textContent = `Обновлено: ${new Date().toLocaleTimeString()}`;
        } catch (error) {
            console.error('Ошибка при обновлении уведомлений:', error);
        } finally {
            toggleLoading(false);
        }
    }

    async function fetchNotifications(page = null) {
        const searchParams = new URLSearchParams(window.location.search);
        page = page || parseInt(searchParams.get('page')) || 1;
        const response = await fetch(`/advertiser/notifications/json?page=${page}`, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!response.ok) throw new Error("Ошибка сети");
        return await response.json();
    }

    function renderNotifications(data) {
        notificationsList.innerHTML = '';
        data.notifications.forEach(notification => {
            notificationsList.appendChild(createNotificationElement(notification));
        });
        updateCounts(data.notifications_count);
        animateNotifications();
    }

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

    function createNotificationElement(notification) {
        const element = document.createElement('div');
        element.className = `notification-item group transition-all duration-200 hover:bg-blue-50 ${notification.is_read ? 'read' : 'unread'} animate-notification-item`;
        element.dataset.type = notification.activity_type;
        element.dataset.id = notification.id;

        const icons = {
            sale: ['fas fa-shopping-cart text-sm', 'bg-blue-100'],
            clicks: ['fas fa-eye text-sm', 'bg-blue-100'],
            payout: ['fas fa-money-bill-wave text-blue-600 text-sm', 'bg-blue-100'],
            system: ['fa fa-suitcase text-sm', 'bg-blue-100'],
            approve: ['fa fa-check text-sm', 'bg-blue-100'],
            reject: ['fa fa-ban text-sm', 'bg-error text-white']
        };
        const [icon, bg] = icons[notification.activity_type] || ['', 'bg-gray-100'];
        element.innerHTML = `
        <div class="p-4 flex items-start">
            <div class="flex-shrink-0">
                <div class="w-10 h-10 ${bg} rounded-full flex items-center justify-center">
                    <i class="${icon}"></i>
                </div>
            </div>
            <div class="ml-3 flex-1">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-sm font-medium text-gray-900">${notification.title}</h3>
                        <p class="mt-1 text-sm text-gray-500">${notification.details || ''}</p>
                    </div>
                    <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                        ${notification.activity_type_display}
                    </span>
                </div>
                <div class="mt-2 flex items-center text-xs text-gray-400">
                    <i class="fas fa-clock mr-1"></i><span>${notification.created_at}</span>
                </div>
            </div>
            ${!notification.is_read ? `
            <form class="mark-as-read opacity-0 group-hover:opacity-100 transition-opacity ml-2 flex-shrink-0" method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('XSRF-TOKEN')}">
                <input value="${notification.id}" name="notification_id" type="hidden">
                <button type="submit" class="btn btn-ghost btn-xs mark-read"><i class="fas fa-check"></i></button>
            </form>` : ''}
        </div>`;
        element.querySelector("form.mark-as-read")?.addEventListener("submit", handleMarkAsRead);
        return element;
    }

    async function updateCounts(total_count) {
        const unreadCount = document.querySelectorAll('.notification-item.unread').length;
        let headerCount = document.getElementById('notifications-count');
        if (unreadCount && !headerCount) {
            const dashboardLink = document.getElementById('dashboard-link');
            headerCount = document.createElement('span');
            headerCount.className = "indicator-item badge badge-sm badge-soft";
            headerCount.id = 'notifications-count';
            dashboardLink.appendChild(headerCount);
        }
        if (headerCount) headerCount.textContent = unreadCount;

        unreadCountElement.textContent = unreadCount;
        totalCountElement.textContent = total_count;
    }

    async function handleMarkAsRead(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const id = e.target.querySelector("input[name=notification_id]").value;

        try {
            const response = await fetch(`/advertiser/notifications/mark/${id}`, {
                method: "POST",
                body: formData,
                credentials: "same-origin"
            });
            if (!response.ok) throw new Error("Ошибка сети");

            e.target.closest(".notification-item").classList.replace("unread", "read");
            e.target.remove();
            const newNotifications = await fetchNotifications();
            updateCounts(newNotifications.notifications_count);
            showToast('Уведомление отмечено как прочитанное', 'success');
        } catch (err) {
            console.error("Ошибка при отметке уведомления:", err);
        }
    }

    async function markAllAsRead(e) {
        e.preventDefault();
        const formData = new FormData(formMarkAllAsRead);

        try {
            const response = await fetch(`/advertiser/notifications/mark-all`, {
                method: "POST",
                body: formData,
                credentials: "same-origin"
            });
            if (!response.ok) throw new Error("Ошибка сети");

            document.querySelectorAll('.notification-item.unread').forEach(n => {
                n.classList.replace('unread', 'read');
                n.querySelector('.mark-read')?.remove();
            });
            const newNotifications = await fetchNotifications();
            updateCounts(newNotifications.notifications_count);
            showToast('Уведомления отмечены как прочитанные', 'success');
        } catch (err) {
            console.error("Ошибка при отметке уведомления:", err);
            showToast('Ошибка при отметке уведомления', 'error');
        }
    }

    function toggleLoading(isLoading) {
        refreshButton.classList.toggle('animate-spin', isLoading);
        loadingIndicator.classList.toggle('hidden', !isLoading);
        notificationsList.classList.toggle('opacity-50', isLoading);
    }

    function animateNotifications() {
        document.querySelectorAll('.animate-notification-item').forEach((n, i) => {
            n.style.animationDelay = `${i * 0.1}s`;
        });
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert-message alert alert-${type} text-white p-4 mr-6 mb-6 shadow-lg animate-fade-in`;
        toast.innerHTML = `
            <div>
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>`;
        document.getElementById('toast-container').appendChild(toast);
        setTimeout(() => {
            toast.classList.add('animate-slide-out-left');
            setTimeout(() => toast.remove(), 800);
        }, 5000);
    }
});