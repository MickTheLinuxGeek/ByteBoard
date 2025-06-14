from django.contrib import admin
from django.http import HttpResponse
from django.utils.text import slugify
import csv
from .models import Category

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'created_at', 'updated_at', 'topic_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['export_as_csv', 'regenerate_slugs', 'display_topic_count']

    def topic_count(self, obj):
        """Return the number of topics in this category."""
        return obj.topics.count()
    topic_count.short_description = 'Topics'

    def export_as_csv(self, request, queryset):
        """Export selected categories as CSV."""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}-export.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "Export selected categories to CSV"

    def regenerate_slugs(self, request, queryset):
        """Regenerate slugs for selected categories based on their names."""
        for category in queryset:
            category.slug = slugify(category.name)
            category.save()
    regenerate_slugs.short_description = "Regenerate slugs for selected categories"

    def display_topic_count(self, request, queryset):
        """Display the number of topics for each selected category."""
        message_parts = []
        for category in queryset:
            count = category.topics.count()
            message_parts.append(f'"{category.name}": {count} topics')

        message = ', '.join(message_parts)
        self.message_user(request, message)
    display_topic_count.short_description = "Show topic count for selected categories"

admin.site.register(Category, CategoryAdmin)
