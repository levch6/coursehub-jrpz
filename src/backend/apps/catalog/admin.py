from django.contrib import admin

from .models import Category, Course, Platform

admin.site.register(Platform)
admin.site.register(Category)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "platform", "price", "rating", "is_available", "is_hidden")
    list_filter = ("platform", "is_available", "is_hidden")
    search_fields = ("title",)
