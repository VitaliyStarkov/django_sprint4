from django.contrib.auth import get_user_model
from django.db import models

from .constant import LENGTH, REDUCTION_NAME, REDUCTION_TITLE

User = get_user_model()


class CreatedAt(models.Model):
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('created_at',)


class IsPublishedCreatedAt(CreatedAt):
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta(CreatedAt.Meta):
        abstract = True


class Category(IsPublishedCreatedAt):
    title = models.CharField(max_length=LENGTH, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; разрешены '
                   'символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:REDUCTION_TITLE]


class Location(IsPublishedCreatedAt):
    name = models.CharField(
        max_length=LENGTH,
        verbose_name='Название места',
        default='Планета Земля'
    )

    class Meta(IsPublishedCreatedAt.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:REDUCTION_NAME]


class Post(IsPublishedCreatedAt):
    title = models.CharField('Заголовок', max_length=LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        null=False,
        help_text='Если установить дату и время '
                  'в будущем — можно делать '
                  'отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Фото',
        upload_to='images',
        blank=True
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:REDUCTION_TITLE]


class Comment(CreatedAt):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )

    class Meta(CreatedAt.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return f"Комментарий пользователя {self.author}"
