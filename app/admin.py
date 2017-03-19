# -*- coding: utf-8 -*-

from django.contrib import admin

from app.models import ModelA, ModelB


@admin.register(ModelA)
class ModelAAdmin(admin.ModelAdmin):
    list_display = [
        'value',
    ]

    search_fields = ['value']


@admin.register(ModelB)
class ModelBAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'data',
    ]

    raw_id_fields = ['data', ]  # practice 1

    list_select_related = ['data', ]  # practice 2

    def get_queryset(self, request):  # practice 2
        qs = super(ModelBAdmin, self).get_queryset(request)
        return qs.prefetch_related('data')
