from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)

from .function import post_all_query, post_published_query, get_post_data
from .models import Category, Comment, Post, User
from .forms import CommentForm, PostForm, UserForm
from .mixins import CommentMixin, PostMixin

POSTS_ON_PAGE = 10


class PostListView(ListView):
    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/index.html'
    queryset = post_published_query()


class ProfileListView(PostListView):
    template_name = "blog/profile.html"
    author = None

    def get_queryset(self):
        username = self.kwargs["username"]
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            return post_all_query().filter(author=self.author)
        return super().get_queryset().filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    post_data = None

    def get_queryset(self):
        self.post_data = get_object_or_404(Post, pk=self.kwargs["pk"])
        if self.post_data.author == self.request.user:
            return post_all_query().filter(pk=self.kwargs["pk"])
        return post_published_query().filter(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.all().select_related('author')
        context['form'] = CommentForm()
        return context

    def check_post_data(self):
        return all((self.post_data.is_published,
                    self.post_data.pub_date <= now(),
                    self.post_data.category.is_published))


class PostCreateView(CreateView, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])


class PostDeleteView(PostMixin, DeleteView):

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/commnet.html'
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        self.post_data = get_post_data(self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        if self.post_data.author != self.request.user:
            self.send_author_email()
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("blog:post_detail", kwargs={"pk": pk})

    def send_author_email(self):
        post_url = self.request.build_absolute_uri(self.get_success_url())
        recipient_email = self.post_data.author.email
        subject = "New comment"
        message = (
            f"Пользователь {self.request.user} добавил "
            f"комментарий к посту {self.post_data.title}.\n"
            f"Читать комментарий {post_url}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email="from@example.com",
            recipient_list=[recipient_email],
            fail_silently=True,
        )


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    ...


class PostCategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(Category,
                                          slug=self.kwargs['category_slug'],
                                          is_published=True)
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cotegory"] = self.category
        return context
