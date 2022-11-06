from django.contrib import admin
from .models import SparePartModel, StockModel, Relationship


class RelationshipInline(admin.TabularInline):
    model = Relationship
    extra = 0
    #formset = RelationshipInlineFormset


@admin.register(SparePartModel)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ['item_number', 'name', 'min_value']


@admin.register(StockModel)
class StockModelAdmin(admin.ModelAdmin):
    inlines = [RelationshipInline]
