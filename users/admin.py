from django.utils import timezone
from datetime import timedelta
from django.contrib import admin
from .models import CustomUser
# Register your models here.
class RecentJoinFilter(admin.SimpleListFilter):
    title = 'New User'
    parameter_name = 'date_joined'

    def lookups(self, request, model_admin):
        return [
            ('today', 'امروز'),
            ('this_week', 'این هفته'),
            ('this_month', 'این ماه'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(date_joined__date=timezone.now().date())
        if self.value() == 'this_week':
            return queryset.filter(date_joined__gte=timezone.now() - timedelta(days=7))
        if self.value() == 'this_month':
            return queryset.filter(date_joined__gte=timezone.now() - timedelta(days=30))
        return queryset
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'wallet_balance', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active',RecentJoinFilter)
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'wallet_balance')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )


