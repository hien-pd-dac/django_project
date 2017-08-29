from enum import Enum
from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from infos.models import Notify
from .forms import CommentForm, PostSearchForm
from .models import Post, Comment


class UserCreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    fields = (
        'title',
        'subject',
        'class_level',
        'salary_hour',
        'times_week',
        'district',
        'text')
    template_name = 'posts/profile_create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class DetailPostView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'posts/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            post_id__exact=self.kwargs['pk']
        ).order_by(
            '-created_date'
        )
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        context['is_liked'] = post.likes.filter(id=self.request.user.id).exists()
        return context


class EditPostView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = (
        'title',
        'subject',
        'class_level',
        'salary_hour',
        'times_week',
        'district',
        'text')
    template_name = 'posts/post_edit.html'

    def form_valid(self, form):
        if form.instance.author != self.request.user:
            return HttpResponse("you dont have permission")
        return super().form_valid(form)


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'

    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.request.user.id})

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if not request.user.is_superuser and post.author != request.user:
            return HttpResponse("you dont have permission")
        success_url = self.get_success_url()
        super().delete(request, *args, **kwargs)
        return HttpResponseRedirect(success_url)


def comment_on_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_author = post.author
    other_comments = post.post_comments.all()
    to_users = []
    for cmt in other_comments:
        to_users.append(cmt.author)
    if not post_author in to_users:
        to_users.append(post_author)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        for to_user in to_users:
            if to_user != request.user:
                Notify.objects.create(
                    from_user=request.user,
                    to_user=to_user,
                    noti_type=Notify.COMMENT,
                    noti_post=post,
                    seen=False
                )
        return redirect(post.get_absolute_url())


def edit_comment(request, post_id, comment_id):
    old_comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != old_comment.author:
        return HttpResponse("you dont have permission")
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        old_comment.text = new_comment.text
        old_comment.save()
        return redirect(old_comment.post.get_absolute_url())


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    post = get_object_or_404(Post, pk=post_id)
    if request.user != comment.author and request.user != post.author:
        return HttpResponse("you dont have permission")
    url = comment.post.get_absolute_url()
    comment.delete()
    to_user = post.author
    Notify.objects.filter(
        from_user=request.user,
        to_user=to_user,
        noti_type=Notify.COMMENT,
        noti_post=post,
    ).delete()
    return redirect(url)


@login_required()
def like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    to_user = post.author
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(user)
        is_liked = False
        Notify.objects.filter(
            from_user=request.user,
            to_user=to_user,
            noti_type=Notify.LIKE,
            noti_post=post
        ).delete()
    else:
        post.likes.add(user)
        is_liked = True
        # add noti
        if to_user != request.user:
            Notify.objects.create(
                from_user=request.user,
                to_user=to_user,
                noti_type=Notify.LIKE,
                noti_post=post,
                seen=False
            )
    data = {
        "is_liked": is_liked,
        "num_liked": post.likes.count()
    }
    return JsonResponse(data=data)


def caculate_approve(request):
    num_approve = Post.objects.filter(is_approved=False).count()
    data = {
        "num_approve": num_approve
    }
    return JsonResponse(data=data)


def count_true_field(post_obj, district_val, subject_val, class_val):
    count = 0
    if district_val == None or post_obj.district == district_val:
        count += 1
    if subject_val == None or post_obj.subject == subject_val:
        count += 1
    if class_val == None or post_obj.class_level == class_val:
        count += 1
    return count


class FilterPost(Enum):
    ALL = 0
    STUDENT = 1
    TUTOR = 2


def find_post(form, filter_param):
    district_val = form.cleaned_data['district']
    subject_val = form.cleaned_data['subject']
    class_level_val = form.cleaned_data['class_level']
    if filter_param == FilterPost.ALL.value:
        post_result = Post.objects.filter(
            Q(district=district_val) | Q(subject=subject_val) | Q(class_level=class_level_val),
            is_approved=True
        ).order_by('-created_at')
    elif filter_param == FilterPost.STUDENT.value:
        post_result = Post.objects.filter(
            Q(district=district_val) | Q(subject=subject_val) | Q(class_level=class_level_val),
            is_approved=True,
            author__is_tutor=False
        ).order_by('-created_at')
    elif filter_param == FilterPost.TUTOR.value:
        post_result = Post.objects.filter(
            Q(district=district_val) | Q(subject=subject_val) | Q(class_level=class_level_val),
            is_approved=True,
            author__is_tutor=True
        ).order_by('-created_at')
    rank_posts = []
    matches = 0
    for post in post_result:
        post.rank = count_true_field(post, district_val, subject_val, class_level_val)
        if post.rank == 3:
            matches += 1
        rank_posts.append(post)
    num_results = len(rank_posts)
    recommend = num_results - matches
    rank_posts.sort(key=attrgetter('rank'), reverse=True)
    dic_rank = {'rank_posts': rank_posts, 'matches': matches, 'recommend': recommend}
    return dic_rank


POSTS_PER_PAGE = 4


def search_post_view(request):
    filter = request.GET.get('filter')
    form = PostSearchForm(request.GET)
    if form.is_valid():
        if filter == 'tutor':
            post_result_filter = find_post(form, FilterPost.TUTOR.value)
        elif filter == 'student':
            post_result_filter = find_post(form, FilterPost.STUDENT.value)
        else:
            filter = 'all'
            post_result_filter = find_post(form, FilterPost.ALL.value)
        paginator = Paginator(post_result_filter['rank_posts'], POSTS_PER_PAGE)
        matches = post_result_filter['matches']
        recommend = post_result_filter['recommend']
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
            'form': form,
            'post_list': post_list,
            'paginator': paginator,
            'query': query,
            'like_dict': like_dict,
            'filter_check': filter,
            'matches': matches,
            'recommend': recommend
        }
        return render(request, 'posts/post_search.html', context)
    else:
        form = PostSearchForm()
    return render(request,
                  'posts/post_search.html',
                  {'form': form}
                  )


def admin_approve_post_view(request):
    filter = request.GET.get('filter')
    if filter == 'student':
        post_lists = Post.objects.filter(
            is_approved=False,
            author__is_tutor=False,
            author__is_superuser=False
        ).order_by('-created_at').all()
    elif filter == 'tutor':
        post_lists = Post.objects.filter(
            is_approved=False,
            author__is_tutor=True
        ).order_by('-created_at').all()
    else:
        filter = 'all'
        post_lists = Post.objects.filter(is_approved=False).order_by('-created_at').all()

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
    return render(request, 'posts/admin_approve_post.html', context)


def admin_approve_post(request, pk):
    if not request.user.is_superuser:
        return HttpResponse("you don't have permisson!")
    post = Post.objects.get(id=pk)
    post.is_approved = True
    post.save()
    url = post.get_absolute_url()
    return redirect(url)
