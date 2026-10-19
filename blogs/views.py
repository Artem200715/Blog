from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BlogPostForm
from .models import BlogPost

def index(request):
    posts = BlogPost.objects.order_by('-date_added', '-id')
    return render(request, 'blogs/index.html', {'posts': posts})

@login_required
def post_new(request):
    form = BlogPostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.owner = request.user
        post.save()
        return redirect('blogs:index')
    return render(request, 'blogs/post_form.html', {'form': form, 'heading': 'Новая публикация'})

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id, owner=request.user)
    form = BlogPostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blogs:index')
    return render(request, 'blogs/post_form.html', {'form': form, 'heading': 'Редактирование публикации'})
