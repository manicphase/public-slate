from django.contrib import admin

from .models import Constituency, Candidate, Party

class CandidatesTabular(admin.TabularInline):
    model = Candidate


class ConstituencyAdmin(admin.ModelAdmin):
    fieldset = "name"
    inlines = [CandidatesTabular]


admin.site.register(Constituency, ConstituencyAdmin)
admin.site.register(Party)

# Register your models here.
