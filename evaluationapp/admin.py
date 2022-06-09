from django.contrib import admin
from .models import JobDescription, GradedOrganization

# Register your models here.


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'grade',
                    'academic_qualifications', 'experience_in_years')
    list_filter = ('company_name', 'grade', 'academic_qualifications')
    search_fields = ['job_title', 'academic_qualifications', 'purpose']


admin.site.register(GradedOrganization)
