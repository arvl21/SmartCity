from django.contrib import admin
from .models import ProblemType, Problem, ProblemImage

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('short_description', 'problem_type', 'status', 'user')
    list_editable = ('status',)
    search_fields = ('address', 'short_description')

admin.site.register(ProblemType)
admin.site.register(ProblemImage)