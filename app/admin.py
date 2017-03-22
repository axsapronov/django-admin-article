# -*- coding: utf-8 -*-

from django.contrib import admin

from app.admin_opt import OptAdmin
from app.models import ModelA, ModelB, ModelC, ModelD, ModelE


@admin.register(ModelA)
class ModelAAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = [
        'value',
    ]
    show_full_result_count = False

    search_fields = ['value']

    def get_queryset(self, request):
        if len(request.GET) == 0:
            return ModelA.objects.none()
        else:
            return super().get_queryset(request)


@admin.register(ModelB)
class ModelBAdmin(OptAdmin):
    list_per_page = 25
    list_display = [
        'name',
        'data',
    ]

    raw_id_fields = ['data', ]  # practice 1
    ordering = []



    # list_select_related = ['data', ]  # practice 2
    #
    # def get_queryset(self, request):  # practice 2
    #     qs = super(ModelBAdmin, self).get_queryset(request)
    #     return qs.prefetch_related('data')


@admin.register(ModelC)
class ModelCAdmin(OptAdmin):
    pass


@admin.register(ModelD)
class ModelDAdmin(OptAdmin):
    pass


@admin.register(ModelE)
class ModelEAdmin(OptAdmin):
    pass
