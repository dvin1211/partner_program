import '@fortawesome/fontawesome-free/js/all'
import '/apps/partners/assets/css/partner.css'

import { setupDeletePartnerLinkModal } from "./delete_link.js";
import { setupEditLink } from "./edit_link.js";

document.addEventListener('DOMContentLoaded', function () {
    setupDeletePartnerLinkModal();
    setupEditLink();
})