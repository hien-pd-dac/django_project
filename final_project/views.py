from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render

from accounts.models import User
from infos.models import District
from posts.models import Post

POSTS_PER_PAGE = 4


def home_page_view(request):
    filter = request.GET.get('filter')
    if filter == 'student':
        post_lists = Post.objects.filter(
            is_approved=True,
            author__is_tutor=False,
            author__is_superuser=False
        ).order_by('-created_at').all()
    elif filter == 'tutor':
        post_lists = Post.objects.filter(
            is_approved=True,
            author__is_tutor=True
        ).order_by('-created_at').all()
    else:
        filter = 'all'
        post_lists = Post.objects.filter(is_approved=True).order_by('-created_at').all()

    paginator = Paginator(post_lists, POSTS_PER_PAGE)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    like_dict = {}
    for post in post_list:
        is_liked = post.likes.filter(username=request.user.username).exists()
        like_dict.update({post.id: is_liked})
    query = '&'.join(
        '{}={}'.format(key, value) for key, value in request.GET.items() if key != 'page'
    )
    context = {
        'post_list': post_list,
        'paginator': paginator,
        'like_dict': like_dict,
        'query': query,
        'filter_check': filter
    }
    return render(request, 'index.html', context)


def logout_page_view(request):
    return render(request, 'thanks.html')


USERS_PER_PAGE = 6


def district_user_list_view(request, district_id):
    district = District.objects.get(id=district_id)
    num_users = district.district_users.count()
    district_name = district.name
    filter = request.GET.get('filter')
    if filter == 'all':
        user_lists = User.objects.filter(district=district).all()
    elif filter == 'student':
        user_lists = User.objects.filter(district=district, is_tutor=False)
    elif filter == 'tutor':
        user_lists = User.objects.filter(district=district, is_tutor=True)
    else:
        user_lists = User.objects.filter(district=district).all()

    paginator = Paginator(user_lists, USERS_PER_PAGE)
    page = request.GET.get('page')
    try:
        user_list = paginator.page(page)
    except PageNotAnInteger:
        user_list = paginator.page(1)
    except EmptyPage:
        user_list = paginator.page(paginator.num_pages)

    query = '&'.join(
        '{}={}'.format(key, value) for key, value in request.GET.items() if key != 'page'
    )
    context = {
        'user_list': user_list,
        'paginator': paginator,
        'query': query,
        'district': district,
        'num_users': num_users,
        'filter': filter
    }
    return render(request, 'district_user_list.html', context)
