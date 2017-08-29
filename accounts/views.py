from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import DetailView, UpdateView

from infos.models import Rating, Notify
from posts.models import Post
from . import forms
from .models import User

token_generator = PasswordResetTokenGenerator()


def send_email(subject, message, to_email):
    email = EmailMessage(subject, message, to=[to_email])
    email.send()


def signup(request):
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            is_email_exist = User.objects.filter(email=user.email).exists()
            if is_email_exist:
                form.add_error('email', 'Email is already exist!')
                return render(request, 'accounts/signup.html', {'form': form})

            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('accounts/email_active_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generator.make_token(user),
            })
            mail_subject = 'Activate your Account !'
            to_email = form.cleaned_data.get('email')
            send_email(mail_subject, message, to_email)
            return redirect('accounts:wait_verify_email')
    else:
        form = forms.SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def waiting_verify_email(request):
    return render(request, 'accounts/wating_verify_email.html')


def success_verify_email(request):
    return render(request, 'accounts/verify_success.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('accounts:success_verify_email')
    else:
        return HttpResponse('Activation link is invalid!')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        name = request.POST['username']
        if not User.objects.filter(username=name).exists():  # check username
            form.add_error('username', 'username is not exists!')
            return render(request, 'accounts/login.html', {'form': form, 'username': name})
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:  # if None -> password false
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                form.add_error('password', "incorrect password!")
                return render(request, 'accounts/login.html', {'form': form, 'username': name})
        else:
            return render(request, 'accounts/login.html', {'form': form, 'username': name})
    else:
        form = forms.LoginForm()
        return render(request, 'accounts/login.html', {'form': form})


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_object_or_404(User, id=self.kwargs['pk'])
        post_lists = Post.objects.filter(author_id=self.kwargs['pk'], is_approved=True).order_by('-created_at')
        paginator = Paginator(post_lists, 2)
        page = self.request.GET.get('page')
        try:
            post_list = paginator.page(page)
        except PageNotAnInteger:
            post_list = paginator.page(1)
        except EmptyPage:
            post_list = paginator.page(paginator.num_pages)

        like_dict = {}
        for post in post_list:
            is_liked = post.likes.filter(username=self.request.user.username).exists()
            like_dict.update({post.id: is_liked})
        context['post_list'] = post_list
        context['paginator'] = paginator
        context['rating'] = self.request.user.get_rating_other(self.kwargs['pk'])
        context['like_dict'] = like_dict
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    fields = (
        'first_name',
        'last_name',
        'school',
        'classname',
        'telephone',
        'email',
        'dateofbirth',
        'gender',
        'district',
        'intro_yourself',
        'picture'
    )
    template_name = "accounts/user_edit.html"

    def form_valid(self, form):
        if form.instance.id != self.request.user.id:
            return HttpResponse("you dont have permission")
        return super().form_valid(form)


def vote_user_view(request, user_id, rating):
    if int(rating) > 5 or int(rating) < 0:
        return HttpResponse("Error rating! olny rate from 0 -> 5 stars !")
    user = get_object_or_404(User, id=user_id)
    if user.is_tutor and not request.user.is_tutor and not request.user.is_superuser:
        is_rated = Rating.objects.filter(
            from_user=request.user,
            to_user=user
        ).exists()
        if is_rated:
            rate = Rating.objects.get(
                from_user=request.user,
                to_user=user
            )
            rate.rating = rating
            rate.save()
            Notify.objects.filter(
                from_user=request.user,
                to_user=user,
                noti_type=Notify.RATING,
            ).update(rating=rating)

        else:
            rate = Rating.objects.create(
                from_user=request.user,
                to_user=user,
                rating=rating
            )
            rate.save()
            Notify.objects.create(
                from_user=request.user,
                to_user=user,
                noti_type=Notify.RATING,
                rating=rating,
                seen=False
            )
        raters = user.count_raters()
        rating_avg = user.str_avg_rating()
        data = {
            "raters": raters,
            "rating_avg": rating_avg,
            "your_rated": rating
        }
        return JsonResponse(data=data)
    else:
        return HttpResponse("Sorry! only student can vote Tutor!")


def set_seen_noties(request):
    Notify.objects.filter(to_user=request.user).update(seen=True)
