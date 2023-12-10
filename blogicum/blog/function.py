from django.db.models import Count

from django.utils import timezone


def filter_date_and_publication(queryset):
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
        )


def annotation_post(queryset):
    return queryset.select_related(
        "category", "location", "author"
    ).annotate(
        comment_count=Count("comments")
    ).order_by("-pub_date")
