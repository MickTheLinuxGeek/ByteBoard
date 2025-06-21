from django.contrib import admin
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Tag

class PostCountFilter(admin.SimpleListFilter):
    """Filter tags by post count."""
    title = _('post count')
    parameter_name = 'post_count'

    def lookups(self, request, model_admin):
        return (
            ('0', _('No posts')),
            ('1-5', _('1-5 posts')),
            ('6-10', _('6-10 posts')),
            ('11+', _('11+ posts')),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(post_count=Count('posts'))
        if self.value() == '0':
            return queryset.filter(post_count=0)
        elif self.value() == '1-5':
            return queryset.filter(post_count__gte=1, post_count__lte=5)
        elif self.value() == '6-10':
            return queryset.filter(post_count__gte=6, post_count__lte=10)
        elif self.value() == '11+':
            return queryset.filter(post_count__gte=11)
        return queryset

class CreatedDateFilter(admin.SimpleListFilter):
    """Filter tags by creation date."""
    title = _('creation date')
    parameter_name = 'created_at'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('past_7_days', _('Past 7 days')),
            ('past_30_days', _('Past 30 days')),
            ('older', _('Older')),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        import datetime
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        elif self.value() == 'past_7_days':
            return queryset.filter(created_at__gte=now - datetime.timedelta(days=7))
        elif self.value() == 'past_30_days':
            return queryset.filter(created_at__gte=now - datetime.timedelta(days=30))
        elif self.value() == 'older':
            return queryset.filter(created_at__lt=now - datetime.timedelta(days=30))
        return queryset

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'post_count', 'view_posts_link')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = (PostCountFilter, CreatedDateFilter, 'created_at')
    actions = ['merge_tags']

    def post_count(self, obj):
        """Return the number of posts associated with this tag."""
        return obj.posts.count()

    post_count.short_description = 'Post Count'

    def view_posts_link(self, obj):
        """Return a link to view all posts associated with this tag."""
        count = obj.posts.count()
        if count == 0:
            return "No posts"

        url = reverse('admin:forum_post_changelist') + f'?tags__id__exact={obj.id}'
        return format_html('<a href="{}">{} post{}</a>', url, count, 's' if count != 1 else '')

    view_posts_link.short_description = 'View Posts'

    def merge_tags(self, request, queryset):
        """Merge selected tags into a target tag."""
        if queryset.count() < 2:
            self.message_user(request, "You need to select at least two tags to merge.", level=messages.ERROR)
            return

        # Use the first selected tag as the target tag
        target_tag = queryset.first()
        other_tags = queryset.exclude(id=target_tag.id)

        post_count = 0
        for tag in other_tags:
            # Get all posts associated with this tag
            posts = tag.posts.all()
            post_count += posts.count()

            # Add the target tag to these posts
            for post in posts:
                post.tags.add(target_tag)

            # Delete the tag
            tag.delete()

        self.message_user(
            request, 
            f"Successfully merged {other_tags.count()} tags into '{target_tag.name}'. {post_count} posts were updated.",
            level=messages.SUCCESS
        )

    merge_tags.short_description = "Merge selected tags (first selected tag is the target)"

# Register the Tag model with the custom admin class
admin.site.register(Tag, TagAdmin)
