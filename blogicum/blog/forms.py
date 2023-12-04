from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import Post, User, Comment


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
        exclude = ('password',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ("author",)
        widgets = {
            "text": forms.Textarea({"rows": "5"}),
            "pub_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "format": "%m/%d/%y %H:%M"}
                ),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
