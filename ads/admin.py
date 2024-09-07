from django.contrib.admin import SimpleListFilter
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Car,Ad

@admin.action(description='Mark selected ads as premium')
def make_premium(modeladmin, request, queryset):
    queryset.update(type='premium')

class PriceRangeFilter(SimpleListFilter):
    title = 'Price Range'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return [
            ('under_500_million', 'Under 500 Million'),
            ('500_1000_million', '500-1000 Million'),
            ('over_1000_million', 'Over 1000 Million'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'under_500_million':
            return queryset.filter(price__lt=500000000)
        if self.value() == '500_1000_million':
            return queryset.filter(price__range=(500000000, 1000000000))
        if self.value() == 'over_1000_million':
            return queryset.filter(price__gt=1000000000)
        return queryset
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General Info', {
            'fields': ('title', 'year', 'mileage', 'body_color', 'inside_color')
        }),
        ('Specifications', {
            'fields': ('body_type','transmission', 'fuel', 'image')
        }),
    )
    list_display = ['title', 'year', 'mileage','body_color','inside_color', 'body_type', 'transmission','fuel','image_preview']
    ordering = ['-year']
    list_filter = ['transmission', 'fuel','body_type','body_color', 'year']
    search_fields = ['title']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image}" width="100" height="100" />')
        return "No Image"

    image_preview.short_description = 'Image Preview'
@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['code','car','location','price','payment_method','type','seller_contact']
    readonly_fields = ['created_date', 'modified_date']
    ordering = ['-price']
    list_filter = ['payment_method','type',PriceRangeFilter]
    search_fields = ['location']
    actions = [make_premium]




