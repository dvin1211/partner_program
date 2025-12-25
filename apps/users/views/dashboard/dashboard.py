from django.shortcuts import render, redirect

def dashboard(request):
    """Главный обработчик личного кабинета"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')   
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    if user.user_type == "advertiser": return redirect('advertiser_dashboard')
    elif user.user_type == "partner": return redirect('partner_dashboard')
    elif user.user_type == "manager": return redirect('manager_dashboard')