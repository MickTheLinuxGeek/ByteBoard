from django.db.models import Q
from django.http import JsonResponse

from .models import Tag

# Create your views here.

def tag_suggestions(request):
    """
    View to provide tag suggestions for autocomplete.

    Accepts a 'query' parameter and returns matching tags as JSON.
    Tags are matched if they start with or contain the query string.
    """
    query = request.GET.get("query", "").strip().lower()

    if not query:
        return JsonResponse({"tags": []})

    # Find tags that start with the query (higher priority) or contain the query
    # Order by name to provide consistent results
    tags = Tag.objects.filter(
        Q(name__startswith=query) | Q(name__contains=query),
    ).order_by("name").distinct().values_list("name", flat=True)[:10]  # Limit to 10 suggestions

    return JsonResponse({"tags": list(tags)})
