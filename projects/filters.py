import django_filters
from .models import Project

class ProjectFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    tech_stack = django_filters.CharFilter(field_name="tech_stack__name", lookup_expr="icontains")
    
    class Meta:
        model = Project
        fields = ["title", "tech_stack", "author__username"]