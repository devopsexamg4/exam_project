"""
TODO:
    - add a descriptive docstring to this module
    - create table to list assignments
    - create table to list submissions
    - ensure descriptive docstrings for all classes
"""
import django_tables2 as tables
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django_filters import FilterSet
from .models import User


TABLE_TEMPLATE = "django_tables2/bootstrap5-responsive.html"

class UserTable(tables.Table):
    action = tables.TemplateColumn(orderable = False, template_name = 'edit_usr.html')
    class Meta:
        model = User
        template_name = TABLE_TEMPLATE
        fields = ('username', 'email', 'type')
        attrs = {'ref':'UserTable'}

class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = {'username':["contains"], 'email':["contains"], 'type':["exact"]}

class FilteredUserList(SingleTableMixin, FilterView):
    table_class = UserTable
    model = User
    template_name = TABLE_TEMPLATE
    filterset_class = UserFilter
