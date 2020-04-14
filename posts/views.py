from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from posts.models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

def index(request):
    index = True
    follow = False
    post_list = Post.objects.annotate(comment_count=Count('post_comments')).all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    context = {
        'page': page,
        'paginator': paginator,
        'follow': follow,
        'index': index
    }
    return render(request, 'index.html', context)

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.annotate(comment_count=Count('post_comments')).filter(group=group).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})

@login_required
def new_post(request):

    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
    
    form = PostForm()
    return render(request, "new.html", {"form": form})

def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.annotate(comment_count=Count('post_comments')).filter(author=profile).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    followers = Follow.objects.filter(author=profile).count()
    followed = Follow.objects.filter(user=profile).count()
    context = {
        'profile': profile,
        'page': page,
        'paginator': paginator,
        'followers': followers,
        'followed': followed,
    }

    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=profile.id).exists()
        context = {
            'profile': profile,
            'page': page,
            'paginator': paginator,
            'followers': followers,
            'followed': followed,
            'following': following,
        }
        return render(request, "profile.html", context)
    return render(request, "profile.html", context)

def post_view(request, username, post_id):
    profile = User.objects.get(username=username)
    followers = Follow.objects.filter(author=profile).count()
    followed = Follow.objects.filter(user=profile).count()
    post = Post.objects.get(author=profile, id=post_id)
    comments = Comment.objects.filter(post_id=post_id).all()
    form = CommentForm()
    context = {
        "post": post,
        "profile": profile,
        'comments': comments,
        'form': form,
        'followers': followers,
        'followed': followed
    }
    return render(request, "post.html", context)

@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect("post", username=request.user.username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)
    return render(request, "post_edit.html", {"form": form, "post": post})

def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)

def server_error(request):
    return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, username, post_id):
    post_author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post_id = post_id
            comment.author = request.user
            comment.save()
            return redirect('post', username=post.author, post_id=post_id)
    return render(request, 'post.html', {'post':post, 'comments':comments})

@login_required
def follow_index(request):
    if request.user.is_authenticated:
        favourites = Follow.objects.filter(user=request.user).count()
        if favourites > 0:
            follow = True
            index = False
            following = Follow.objects.select_related('author', 'user').filter(user=request.user)
            following_authors_list = [item.author for item in following]
            post_list = Post.objects.filter(author__in=following_authors_list).annotate(comment_count=Count('post_comments')).all()
            paginator = Paginator(post_list, 10)
            page_number = request.GET.get('page')
            page = paginator.get_page(page_number)

            context = {
                'page': page,
                'paginator': paginator,
                'follow': follow,
                'index': index
            }
            return render(request, "follow.html", context)
        return redirect('index')
    return redirect('index')

    

@login_required
def profile_follow(request, username):
    user = User.objects.get(username=request.user.username)
    author = User.objects.get(username=username)
    Follow.objects.create(user=user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = User.objects.get(username=request.user.username)
    author = User.objects.get(username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect("profile", username=username)
