from django.urls import path
from . import views

urlpatterns = [
    # Функции
    path('approve_platform/<int:platform_id>',views.approve_platform,name='approve_platform'),
    path('reject_platform/<int:platform_id>',views.reject_platform,name='reject_platform'),
    path('approve_project/<int:project_id>',views.approve_project,name='approve_project'),
    path('reject_project/<int:project_id>',views.reject_project,name='reject_project'),
    path('approve_transaction/<int:transaction_id>/<int:partner_id>',views.approve_transaction,name='approve_transaction'),
    path('reject_transaction/<int:transaction_id>/<int:partner_id>',views.reject_transaction,name='reject_transaction'),
    path('proccess_adv_transaction/<int:transaction_id>',views.proccess_adv_transaction,name='proccess_adv_transaction'),
    path('approve_adv_transaction/<int:transaction_id>',views.approve_adv_transaction,name='approve_adv_transaction'),
    path('reject_adv_transaction/<int:transaction_id>',views.reject_adv_transaction,name='reject_adv_transaction'),
    path("block_user/<int:user_id>",views.block_user,name='block_user'),
    path("unblock_user/<int:user_id>",views.unblock_user,name='unblock_user'),
    path("edit_review/<int:review_id>",views.edit_review,name="edit_review"),
    path("publish_review/<int:review_id>",views.publish_review,name="publish_review"),
    path("remove_review/<int:review_id>",views.remove_review,name="remove_review"),
    path("make_single_notification/<int:user_id>",views.make_single_notification,name='make_single_notification'),
    
    # ЛК
    path('dashboard',views.manager_dashboard,name='manager_dashboard'),
    path('projects',views.manager_projects,name="manager_projects"),
    path('platforms',views.manager_platforms,name="manager_platforms"),
    path('users',views.manager_users,name="manager_users"),
    path('partners',views.manager_partners,name="manager_partners"),
    path('advertisers',views.manager_advertisers,name="manager_advertisers"),
    path('reviews',views.reviews,name='manager_reviews'),
    path('settings',views.settings,name='manager_settings'),
    
    # Просмотры для менеджера
    path('advertiser_requisites/<int:advertiser_id>',views.advertiser_legal_details,name='advertiser_legal_details'),
]