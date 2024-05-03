"""
TODO:
    - add a descriptive docstring to this module
    - ensure descriptive docstrings for all classes
"""
import django_tables2 as tables
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django_filters import FilterSet

from .models import Assignments, User, StudentSubmissions


TABLE_TEMPLATE = "django_tables2/bootstrap5-responsive.html"

class UserTable(tables.Table):
    """A table to list users in the system."""
    action = tables.TemplateColumn(orderable = False, template_name = 'edit_usr.html')
    teacher_actions = tables.TemplateColumn(orderable = False, template_name='teacher_stud.html')
    class Meta:
        """Meta class for the UserTable."""
        model = User
        template_name = TABLE_TEMPLATE
        fields = ('username', 'email', 'type', 'is_active')
        attrs = {'ref':'UserTable'}

class AssTable(tables.Table):
    """A table to list assignments in the system."""
    details = tables.TemplateColumn(orderable = False, template_name='assignment_details.html')
    edit = tables.TemplateColumn(orderable = False, template_name='edit_assig_button.html')
    class Meta:
        """Meta class for the AssTable."""
        model = Assignments
        template_name = TABLE_TEMPLATE
        fields = ('status', 'title', 'start', 'end' )
        attrs = {'ref':'AssTable'}

class SubmissionTable(tables.Table):
    """A table to list submissions in the system."""
    details = tables.TemplateColumn(orderable = False, template_name='sub_detail_button.html')
    delete = tables.TemplateColumn(orderable = False, template_name='subdel.html')
    teacher_actions = tables.TemplateColumn(orderable = False, template_name='teacher_sub.html')
    class Meta:
        """Meta class for the SubmissionTable."""
        model = StudentSubmissions
        template_name = TABLE_TEMPLATE
        fields = ( 'result', 'assignment', 'uploadtime', 'File', 'log'  )
        attrs = {'ref':'SubmissionTable'}

class UserFilter(FilterSet):
    """A filter for the UserTable."""
    class Meta:
        """Meta class for the UserFilter."""
        model = User
        fields = {'username':["contains"],
                  'email':["contains"],
                  'type':["exact"]}

class AssFilter(FilterSet):
    """A filter for the AssTable."""
    class Meta:
        """ Meta class for the AssFilter."""
        model = Assignments
        fields = {'status':["contains"],
                  'title':["contains"],
                  'start':["contains"],
                  'end':["contains"]}

class SubmissionFilter(FilterSet):
    """A filter for the SubmissionTable."""
    class Meta:
        """Meta class for the SubmissionFilter."""
        model = StudentSubmissions
        fields = {'result':["contains"],
                  'uploadtime':["contains"]}


class FilteredUserList(SingleTableMixin, FilterView):
    """filters the UserTable."""
    table_class = UserTable
    model = User
    template_name = TABLE_TEMPLATE
    filterset_class = UserFilter

class FilteredAssTable(SingleTableMixin, FilterView):
    """filters the AssTable."""
    table_class = AssTable
    model = Assignments
    template_name = TABLE_TEMPLATE
    filterset_class = AssFilter

class FilteredSubmissionTable(SingleTableMixin, FilterView):
    """filters the SubmissionTable."""
    table_class = SubmissionTable
    model = StudentSubmissions
    template_name = TABLE_TEMPLATE
    filterset_class = SubmissionFilter
