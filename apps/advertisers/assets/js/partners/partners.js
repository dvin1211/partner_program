import '@fortawesome/fontawesome-free/js/all'
import '/apps/advertisers/assets/css/advertiser.css'

import { setupStopPartnership } from './stop_partnership_with_partner.js';
import { setupPartnerInfoModal } from './fetch_partner_info.js';
document.addEventListener('DOMContentLoaded', function () {
    setupStopPartnership();
    setupPartnerInfoModal();

    const style = document.createElement('style');
    style.textContent = `
        @keyframes slide-out-left {
            0% {
                opacity: 1;
                transform: translateX(0);
            }
            70% {
                opacity: 0;
                transform: translateX(-100%);
            }
            100% {
                opacity: 0;
                transform: translateX(-100%);
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

    const alertMessages = document.querySelectorAll('.alert-message');

    alertMessages.forEach((element, index) => {
        const delay = 5000 + (index * 200);

        setTimeout(() => {
            element.classList.add(
                'animate-slide-out-left',
                'transform-gpu', 
                'transition-all',
                'duration-800',
                'ease-in-out'
            );

            setTimeout(() => {
                if (element.parentNode) {
                    element.remove();
                }
            }, 800); // Время анимации
        }, delay);
    });
})