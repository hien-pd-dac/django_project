from operator import attrgetter

from django import template

from accounts.models import User
from infos.models import District, Notify
from posts.forms import PostSearchForm

register = template.Library()


@register.inclusion_tag('posts/post_search2.html')
def get_search_form():
    return {
        'form': PostSearchForm()
    }


@register.inclusion_tag('accounts/rating_user_list.html')
def show_rating_list(number_result):
    user_list = User.objects.filter(is_tutor=True).all()
    rank_list = []
    for user in user_list:
        user.rank = user.calculate_avg_rating()
        rank_list.append(user)
    rank_list.sort(key=attrgetter('rank'), reverse=True)
    result_list = rank_list[:number_result]
    return {
        'rating_user_list': result_list
    }


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.inclusion_tag('district_user_index.html')
def show_district_user_list():
    district_list = District.objects.all()
    return {
        'district_list': district_list
    }


@register.assignment_tag
def get_user_noties(user):
    noti_list = Notify.objects.filter(to_user=user).all().order_by('-noti_date')
    return noti_list

