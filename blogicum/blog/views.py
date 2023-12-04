from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView
)

from .function import annotation_post, filter_date_and_publication
from .models import Category, Post, User
from .forms import PostForm, UserForm, CommentForm
from .mixins import PostMixin, CommentMixin, AuthorCheckMixin
from .constant import PAGE_POST_COUNT


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGE_POST_COUNT
    queryset = annotation_post(filter_date_and_publication(Post.objects))


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = PAGE_POST_COUNT

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        profile = self.get_object()
        posts = annotation_post(profile.posts)
        if self.request.user != profile:
            posts = filter_date_and_publication(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'profile': self.get_object()})
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:index')


class PostDetailView(ListView):
    model = Post
    pk_field = 'post_id'
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'
    paginate_by = PAGE_POST_COUNT

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author and (
            post.pub_date > timezone.now() or not post.is_published
        ):
            raise Http404
        return post

    def get_queryset(self):
        return self.get_object().comments.select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={self.pk_url_kwarg: self.get_object().pk}
        )


class PostDeleteView(PostMixin, DeleteView):

    pass


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, AuthorCheckMixin, UpdateView):

    pass


class CommentDeleteView(CommentMixin, AuthorCheckMixin, DeleteView):

    pass


class CategoryListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = PAGE_POST_COUNT

    def get_object(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return annotation_post(
            filter_date_and_publication(self.get_object().posts)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['category'] = category
        return context
