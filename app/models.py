# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class ModelA(models.Model):
    value = models.PositiveSmallIntegerField(_("Value"))

    def __str__(self):
        return "Model {}".format(self.value)


class ModelB(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    data = models.ForeignKey(ModelA)

    def __str__(self):
        return "Data {} = {}".format(self.name, self.data.value)


class ModelC(models.Model):
    name = models.CharField(_("Name"), max_length=255)


class ModelD(models.Model):
    name = models.CharField(_("Name"), max_length=255)


class ModelE(models.Model):
    name = models.CharField(_("Name"), max_length=255)

