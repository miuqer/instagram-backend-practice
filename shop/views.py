from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render 
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .models import MyUser,Post


def index(request):
  posts = Post.objects.all()
  return render(request, 'shop/index.html', {'posts': posts})
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
def custom_password_reset_view(request):
  if request.method == 'POST':
    email_input = request.POST.get('email', '').strip()

    if not email_input:
      messages.error(request, 'لطفاً آدرس ایمیل خود را وارد کنید.')
      return render(request, 'shop/password_reset.html')

    user = MyUser.objects.filter(email=email_input).first()

    if user:
      uid = urlsafe_base64_encode(force_bytes(user.pk))
      token = default_token_generator.make_token(user)

      reset_link = request.build_absolute_uri(
          reverse(
              'shop:password_reset_confirm',
              kwargs={'uidb64': uid, 'token': token},
          )
      )

      subject = 'درخواست بازنشانی رمز عبور'
      message = (
          f'سلام {user.username} عزیز،\n\n'
          f'برای تأیید و تنظیم رمز عبور جدید، روی لینک زیر کلیک کنید:\n\n'
          f'{reset_link}\n\n'
          f'اگر شما این درخواست را ثبت نکرده‌اید، این پیام را نادیده بگیرید.'
      )

      send_mail(
          subject=subject,
          message=message,
          from_email=None,
          recipient_list=[user.email],
          fail_silently=False,
      )

    return redirect('shop:password_reset_done')

  return render(request, 'shop/password_reset.html')
def password_reset_done_view(request):
  return render(request, 'shop/password_reset_done.html')
def password_reset_confirm_view(request, uidb64, token):
  try:
    uid = urlsafe_base64_decode(uidb64).decode()
    user = MyUser.objects.get(pk=uid)
  except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
    user = None

  if user is not None and default_token_generator.check_token(user, token):
    validlink = True

    if request.method == 'POST':
      new_password1 = request.POST.get('new_password1', '')
      new_password2 = request.POST.get('new_password2', '')

      if not new_password1 or not new_password2:
        messages.error(request, 'لطفاً هر دو فیلد رمز عبور را وارد کنید.')
      elif new_password1 != new_password2:
        messages.error(request, 'رمزهای عبور وارد شده همخوانی ندارند.')
      elif len(new_password1) < 8:
        messages.error(request, 'رمز عبور باید حداقل ۸ کاراکتر باشد.')
      else:
        user.set_password(new_password1)
        user.save()
        messages.success(
            request, 'رمز عبور تغییر یافت. اکنون می‌توانید وارد شوید.'
        )
        return redirect('shop:login')
  else:
    validlink = False

  return render(
      request, 'shop/password_reset_confirm.html', {'validlink': validlink}
  )
def create_post(request):
  if not request.user.is_authenticated:
    messages.error(request, 'برای ایجاد پست ابتدا باید وارد شوید.')
    return redirect('shop:login')

  if request.method == 'POST':
    image_file = request.FILES.get('image')
    caption_input = request.POST.get('caption', '').strip()

    if not image_file:
      messages.error(request, 'لطفاً یک تصویر برای پست انتخاب کنید.')
      return render(request, 'shop/create_post.html')

    Post.objects.create(
        author=request.user, image=image_file, caption=caption_input
    )
    messages.success(request, 'پست جدید با موفقیت منتشر شد!')
    return redirect('shop:index')

  return render(request, 'shop/create_post.html')

