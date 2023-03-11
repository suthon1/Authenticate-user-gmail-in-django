from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_byte
from .tokens import generate_token
from django.core.mail import EmailMessage

from dj_auth import settings



def home(request):
    name = 'Hello World'
    return HttpResponse(f"{name} is Working...")

def index(request):
    return render(request, 'authenticate/index.html')


def signup(request):
    if request.method == 'POST':
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        passw1 = request.POST['password']
        passw2 = request.POST['cpassword']

        if User.objects.filter(username=username):
            messages.error(request, 'Username already exist..')
            return redirect('home')
        if User.objects.filter(email=email):
            messages.error(request, 'Email already exist')

        if len(username) > 20:
            messages.error(request, 'Username must be under 20 charackter')
        if passw1 != passw2:
            messages.error(request, 'Password did not math')

        if not username.isalnum():
            messages.error(request, 'Username must be Alpha-Numeric')
            return redirect('home')

        myuser = User.objects.create_user(username, email, passw1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request, 'Your account has been succsessfully created, We have send yoy confirmation to your email please verify your account')

        # Wellcome email
        subject = 'Wellcome To GFG - Django-Login!!'
        message = 'Hello' + myuser.first_name + "!!\n" + 'Wellcome to DFG!!\n Thank you for visiting our website, We have also sent you confirmation email, please confirm your email..'
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)


        # Email Address Confirmation
        current_site = get_current_site(request)
        email_subject = "Confirm Your Email @ GFG - Django Login"
        message2 = render_to_string('email_confirmation.html'), {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_byte(myuser.pk)),
            'token': generate_token.make_token(myuser)
        }
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.send()


        return redirect('signin')


    return render(request, 'authenticate/signup.html')



def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['password']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'authenticate/index.html', {'fname': fname})
        else:
            messages.error(request, 'Bad Credential')
            return redirect('home')
    return render(request, 'authenticate/signin.html')


def signout(request):
    logout(request)
    messages.success(request, 'Logged out Succes')
    return redirect('home')


# def activate(request, uidb64, token):
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))