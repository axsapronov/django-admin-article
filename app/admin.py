# -*- coding: utf-8 -*-

from django.contrib import admin

from app.models import ModelA, ModelB


@admin.register(ModelA)
class ModelAAdmin(admin.ModelAdmin):
    list_display = [
        'value',
    ]


@admin.register(ModelB)
class ModelBAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'data',
    ]
