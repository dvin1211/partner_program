import json

from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.db.utils import IntegrityError
from django.contrib import messages

from apps.advertisers.forms import ProjectForm
from apps.advertisers.models import ProjectParam
from apps.core.decorators import role_required


@role_required('advertiser')
@require_POST
def add_project(request):
    form = ProjectForm(request.POST)
    
    if not form.is_valid():
        # Собираем все ошибки в чистый текст
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                # Убираем HTML теги и лишние символы
                clean_error = str(error).replace('<strong>', '').replace('</strong>', '').strip()
                error_messages.append(clean_error)
        
        # Объединяем все ошибки в одну строку
        full_error_message = ". ".join(error_messages)
        messages.error(request, f"Ошибка: {full_error_message}", extra_tags="project_add_error")
        
        return redirect("advertiser_projects")
    
    try:
        project = form.save(commit=False)
        project.advertiser = request.user
        project.first_price = project.cost_per_action
        
        # Обработка шаблона ссылки (только если он был предоставлен)
        if project.link_template:
            # Добавляем параметры в правильном порядке
            params = ["pid=partner_id"]  # Начинаем с partner_id
            
            params_data = json.loads(request.POST.get('params_json', '[]'))
            for param in params_data:
                param_name = param.get('name', '')
                param_value = param.get('example', '')
                if param_name:  # Только если имя параметра не пустое
                    params.append(f"{param_name}={param_value}")
            
            # Собираем итоговую ссылку
            separator = '?' if '?' not in project.link_template else '&'
            project.link_template += separator + '&'.join(params)
        
        project.save()  # Сохраняем проект
        
        # Главный параметр ID партнёра
        ProjectParam.objects.create(
            project=project,
            name='pid',
            description='ID партнёра. Укажите ID вашего партнёрского аккаунта',
            param_type='required',
            example_value='111'
        )
        # Создаем параметры (после сохранения проекта, чтобы была связь)
        for param in params_data:
            ProjectParam.objects.create(
                project=project,
                name=param['name'],
                description=param.get('description', ''),
                param_type=param.get('type', 'optional'),
                example_value=param.get('example', '')
            )
        
        messages.success(request, message="Проект успешно добавлен", extra_tags="project_add_success")
    
    except IntegrityError as e:
        messages.error(request, message="Уже существует проект с таким URL или названием", extra_tags="project_add_error")
    
    except json.JSONDecodeError as e:
        messages.error(request, message="Ошибка в формате параметров", extra_tags="project_add_error")
    
    except Exception as e:
        for error in e.messages:
            messages.error(request, message=f"Произошла непредвиденная ошибка: {str(error)}", extra_tags="project_add_error")
        
    return redirect("advertiser_projects")

