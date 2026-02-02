export function setupPartnerInfoModal() {
    const partnerInfoModal = document.getElementById('partnerStatsModal');

    const firstLetterBlock = document.getElementById('partnerInitials');
    const partnerName = document.getElementById('partnerName');

    // Общая статистика
    const totalIncome = document.getElementById('totalAmount');
    const conversionsCount = document.getElementById('totalConversions');
    const conversionsAvg = document.getElementById('AverageConversion');

    const totalProjects = document.getElementById('totalProjects');
    const activeProjects = document.getElementById('activeProjects');
    const pausedProjects = document.getElementById('pausedProjects');

    // Проекты
    const projectsList = document.getElementById('projectsList');

    const fetchBtns = document.querySelectorAll('.partner-stats');
    fetchBtns.forEach(btn => {
        btn.addEventListener('click', async function () {
            const partnerId = this.dataset.partnerId;
            const response = await fetch(`/advertiser/partners/json/${partnerId}`);
            if (response.ok) { 
                const json = await response.json();

                firstLetterBlock.innerHTML = json.partner.username.slice(0,1);
                partnerName.innerHTML = json.partner.username;

                totalIncome.innerHTML = `${json.partner.total_income}₽`;
                conversionsCount.innerHTML = json.partner.conversions_count;
                conversionsAvg.innerHTML = json.partner.average_conversion_rate;

                totalProjects.innerHTML = json.partner.projects.count;
                pausedProjects.innerHTML  = json.partner.projects.on_pause;
                activeProjects.innerHTML  = json.partner.projects.active;

                const partnerships = json.partnerships;
                projectsList.innerHTML = '';
                for(let i in partnerships){
                    const project = createProjectCard(partnerships[i]);
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML=project;
                    projectsList.appendChild(tempDiv);
                }

            } else {
                alert("Ошибка HTTP: " + response.status);
            }

            partnerInfoModal.show();
        })
    })
}

function createProjectCard(project) {
  const badgeClass = {
    'Активен': 'badge-success',
    'На паузе': 'badge-warning',
    'Удалено': 'badge-error',
  };
  
  const status = project.project_status !== 'Удалено' ? project.partnership_status || 'active' : 'Удалено';
  
  return `
    <div class="project-card bg-white rounded-xl border border-gray-200 p-4 sm:p-5 hover:border-primary/30 hover:shadow-lg transition-all duration-300">
      <!-- Верхняя часть: Информация о проекте -->
      <div class="mb-4 sm:mb-5">
        <!-- Статус и название -->
        <div class="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
          <span class="badge ${badgeClass[status]} badge-sm self-start sm:self-center">
            ${status}
          </span>
          <h4 class="text-lg sm:text-xl font-bold text-gray-800">${project.project_name}</h4>
        </div>
        
        <!-- Описание -->
        <p class="text-gray-600 text-sm sm:text-base mb-3 sm:mb-4 break-all">
          ${project.project_description}
        </p>
        
        <!-- Мета-информация -->
        <div class="flex flex-wrap gap-3 text-xs sm:text-sm text-gray-500">
          <span class="flex items-center gap-1 bg-gray-50 px-3 py-1.5 rounded-lg">
            <svg class="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            Подключен: ${new Date(project.joined_at).toDateString()}
          </span>
          <span class="flex items-center gap-1 bg-gray-50 px-3 py-1.5 rounded-lg">
            <svg class="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            CPA: ${project.cpa} ₽
          </span>
        </div>
      </div>
      
      <!-- Нижняя часть: Статистика -->
      <div class="pt-4 sm:pt-5 border-t border-gray-100">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
          <!-- Доход -->
          <div class="text-center p-3 sm:p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200">
            <div class="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Общий доход</div>
            <div class="font-bold text-green-700 text-lg sm:text-2xl">${project.income} ₽</div>
          </div>
          
          <!-- Конверсии -->
          <div class="text-center p-3 sm:p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200">
            <div class="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Конверсий</div>
            <div class="font-bold text-blue-700 text-lg sm:text-2xl">${project.conversions_count}</div>
          </div>
          
          <!-- CR -->
          <div class="text-center p-3 sm:p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200">
            <div class="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Конверсия (CR)</div>
            <div class="font-bold text-purple-700 text-lg sm:text-2xl">${project.conversion_rate}%</div>
          </div>
        </div>
      </div>
    </div>
  `;
}