from django.contrib import admin

from .models import Category, Location, Post, Comment

admin.site.empty_value_display = 'Не задано'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'category',
        'location',
        'author',
    )
    list_editable = (
        'is_published',
        'category',
        'location',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title', 'author',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published'
    )
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = ('title',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published'
    )
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('name', 'created_at',)
    list_display_links = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post',)
    list_editable = ('author', 'post', )
    search_fields = ('author',)
    list_display_links = ('text',)
