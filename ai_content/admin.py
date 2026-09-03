from django.contrib import admin

from .models import ContentJob


@admin.register(ContentJob)
class ContentJobAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'organization', 'kind', 'status', 'created_by', 'created_at', 'completed_at')
    list_filter = ('status', 'kind', 'organization')
    search_fields = ('prompt', 'result_text')
    readonly_fields = ('result_text', 'error', 'created_at', 'completed_at')
