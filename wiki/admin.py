from django.contrib import admin

from .models import Page, Revision

class RevisionAdmin(admin.ModelAdmin):
    model = Revision
    readonly_fields = ('edit_number', )
    list_display = ('page', 'edit_number', 'created_date')

admin.site.register(Page)
admin.site.register(Revision, RevisionAdmin)
