from django.urls import path
from . import views

urlpatterns = [
    # Функции
    path('add_project',views.add_project,name='add_project'),
    path('del_project/<int:project_id>',views.delete_project,name='del_project'),
    path('edit_project/<int:project_id>',views.edit_project,name='edit_project'),
    path('stop_partnership_with_partner/<int:partner_id>',views.stop_partnership_with_partner,name="stop_partnership_with_partner"),
    path('top_up_balance',views.top_up_balance,name='top_up_balance'),
    path('update_api_settings',views.update_api_settings,name='update_api_settings'),
    path('update_requisites',views.update_requisites_settings,name='update_requisites_settings'),
    path('read_notifications',views.read_advertiser_notifications,name='read_advertiser_notifications'),
    
    # ЛК
    path('dashboard',views.dashboard,name='advertiser_dashboard'),
    path('partners',views.partners,name='advertiser_partners'),
    path('partners/json/<int:partner_id>',views.partners_json,name='advertiser_partners_json'),
    path('sales',views.sales,name='advertiser_sales'),
    path('projects',views.projects,name='advertiser_projects'),
    path('settings',views.settings,name='advertiser_settings'),
    path('requisites',views.requisites,name='advertiser_requisites'),
    path('notifications',views.notifications,name='advertiser_notifications'),
    path('notifications/json',views.notifications_json,name='partner_notifications_json'),
    path('notifications/mark/<int:notification_id>', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all', views.mark_all_notifications_read, name='mark_all_notifications_read')
]