from django.shortcuts import render
from django.shortcuts import redirect
# Create your views here.
from .models import User,ConfirmString
from . import  forms
import hashlib
import datetime
from  django.conf import settings

def hash_code(s,salt='chensd'):
    h = hashlib.sha256()
    s+=salt
    h.update(s.encode())
    return h.hexdigest()


def index(request):
    if not request.session.get('is_login',None):
        return redirect('/login/')
    return render(request,'login/index.html')


def login(request):
    register_form = forms.RegisterForm()
    if request.session.get('is_login',None):
        return redirect('/index/')
    if request.method=='POST':
        login_form = forms.UserForm(request.POST)
        message='请检查输入内容'
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name=username)
            except:
                message = '用户不存在'
                return render(request,'login/login.html',locals())
            if user.password==hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = '密码不正确'
                return render(request, 'login/login.html',locals())
        else:
            return render(request,'login/login.html',locals()   )
    login_form = forms.UserForm()
    return render(request,'login/login.html',locals())

def register(request):
    if request.session.get('is_login',None):
        return redirect('/index/')
    if request.method=='POST':
        register_form = forms.RegisterForm(request.POST)
        message='请检查输入内容'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 !=password2:
                message = '两次输入的密码不同！'
                return render(request,'login/register.html',locals())
            else:
                same_name_user = User.objects.filter(name = username)
                if same_name_user:
                    message = '用户已经存在'
                    return render(request,'login/register.html',locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message='该邮箱已经被注册'
                    return render(request, 'login/register.html',locals())
                new_user = User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                sent_email(email,code)
                return redirect('/login/')
        else:
            return  render(request,'login/register.html',locals())
    register_form = forms.RegisterForm()
    return render(request,'login/register.html',locals())



def logout(request):
    if not request.session.get('is_login',None):
        #如果本来就没有登录，就不会有登出

        return redirect(request,'/login/')
    request.session.flush()
    print('session is cleaned')

    return redirect('/login/')




def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    ConfirmString.objects.create(code=code, user=user, )
    return code


def sent_email(email,code):
    from django.core.mail import  EmailMultiAlternatives

    subject = '来自chensd注册系统的注册邮件确认'

    text_content = '''感谢注册www.liujiangblog.com，这里是刘江的博客和教程站点，专注于Python、Django和机器学习技术的分享！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''
    html_content = '''
                       <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                       这里是刘江的博客和教程站点，专注于Python、Django和机器学习技术的分享！</p>
                       <p>请点击站点链接完成注册确认！</p>
                       <p>此链接有效期为{}天！</p>
                       '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def user_confirm(request):
    code = request.GET.get('code',None)
    message=''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认信息'
        return render(request,'login/confirm.html',locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now >c_time +datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message ='您的邮件已经过期！请重新注册'
        return render(request,'login/confirm.html',locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请您使用账号登录'
        return render(request, 'login/confirm.html',locals())