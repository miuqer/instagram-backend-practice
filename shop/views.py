from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from django.shortcuts import redirect, render
from .models import MyUser
def index(request):
    return render(request, 'shop/index.html')
def register_view(request):
    if request.user.is_authenticated:
       return redirect('shop:index')
    if request.method == 'POST':
       username = request.POST.get('username', '').strip()
       email = request.POST.get('email', '').strip()
       phone_number = request.POST.get('phone_number', '').strip()
       password = request.POST.get('password', '')
       confirm_password = request.POST.get('confirm_password', '')
       context = {
            'username': username,
            'email': email,
            'phone_number': phone_number,
        }
       if not username or not email or not phone_number or not password or not confirm_password:
           messages.error(request, 'لطفاً تمام فیلدها را پر کنید.')
           return render(request, 'shop/register.html', context)
       if phone_number and not phone_number.isdigit():
           messages.error(request, 'شماره تلفن باید فقط شامل ارقام باشد.')
           return render(request, 'shop/register.html', context)
       if phone_number and len(phone_number) != 11:
           messages.error(request, 'شماره تلفن باید شامل 11 رقم باشد.')
           return render(request, 'shop/register.html', context)
       if phone_number and not phone_number.startswith('09'):
           messages.error(request, 'شماره تلفن باید با 09 شروع شود.')
           return render(request, 'shop/register.html', context)
       if password != confirm_password:
           messages.error(request, 'گذرواژه‌ها مطابقت ندارند.')
           return render(request, 'shop/register.html', context)
       if MyUser.objects.filter(username=username).exists():
           messages.error(request, 'نام کاربری قبلاً استفاده شده است.')
           return render(request, 'shop/register.html', context)
       if MyUser.objects.filter(email=email).exists():
           messages.error(request, 'ایمیل قبلاً استفاده شده است.')
           return render(request, 'shop/register.html', context)
       if MyUser.objects.filter(phone_number=phone_number).exists():
           messages.error(request, 'شماره تلفن قبلاً استفاده شده است.')
           return render(request, 'shop/register.html', context)
       user = MyUser.objects.create_user(username=username, email=email, phone_number=phone_number, password=password)
       messages.success(request, 'ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.')
       return redirect('shop:login')
    return render(request, 'shop/register.html')
def login_view(request):
  if request.user.is_authenticated:
    return redirect('shop:index')

  if request.method == 'POST':
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    if not username or not password:
      messages.error(request, 'لطفاً هم نام کاربری و هم گذرواژه را وارد کنید.')
      return render(request, 'shop/login.html')

    user = authenticate(request, username=username, password=password)

    if user is not None:
      if user.is_active:
        login(request, user)
        messages.success(request, f'خوش آمدید {user.username}!')
        return redirect('shop:index')
      else:
        messages.error(request, 'حساب کاربری شما غیرفعال است.')
        return render(request, 'shop/login.html')
    else:
      messages.error(request, 'نام کاربری یا گذرواژه اشتباه است.')
      return render(request, 'shop/login.html')

  return render(request, 'shop/login.html')
def logout_view(request):
    logout(request)
    messages.success(request, 'شما با موفقیت خارج شدید.')
    return redirect('shop:login')