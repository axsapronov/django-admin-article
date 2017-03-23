# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ChangeList
from django.core.cache import cache
from django.core.paginator import Paginator, InvalidPage
from django.db import connection, connections

__all__ = [
    'CachingPaginator',
    'LargeTableChangeList',
    'LargeTablePaginator',
    'OptAdmin',
]


class CachingPaginator(Paginator):
    """A custom paginator that helps to cut down on the number of SELECT
    COUNT(*) form table_name queries.

    These are really slow, therefore once we execute the query, we will
    cache the result which means the page numbers are not going to be
    very accurate but we don't care

    """

    def _get_count(self):
        """Returns the total number of objects, across all pages."""

        if self._count is None:
            try:
                key = 'adm:{0}:count'.format(
                    hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    if not self.object_list.query.where:
                        # This query that avoids a count(*) alltogether is
                        # stolen from https://djangosnippets.org/snippets/2593/
                        cursor = connection.cursor()
                        cursor.execute(
                            'SELECT reltuples FROM pg_class WHERE relname = %s',
                            [self.object_list.query.model._meta.db_table])
                        self._count = int(cursor.fetchone()[0])
                    else:
                        self._count = self.object_list.count()
                    cache.set(key, self._count, 3600)

            except:
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class LargeTableChangeList(ChangeList):
    """Overrides the count method to get an estimate instead of actual count
    when not filtered.

    The only change is the try/catch block calculating
    'full_result_count'

    """

    def get_results(self, request):
        paginator = self.model_admin.get_paginator(request, self.queryset,
                                                   self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count

        # Get the total number of objects, with no admin filters applied.
        # Perform a slight optimization: Check to see whether any filters were
        # given. If not, use paginator.hits to calculate the number of objects,
        # because we've already done paginator.hits and the value is cached.
        if not self.queryset.query.where:
            full_result_count = result_count
        else:
            try:

                if 'mysql' in connections[
                    self.queryset.db].client.executable_name.lower():
                    cursor = connections[self.queryset.db].cursor()
                    cursor.execute('SHOW TABLE STATUS LIKE %s',
                                   (self.model._meta.db_table,))
                    return cursor.fetchall()[0][4]
                    # For Postgres, by Woody Anderson
                    # http://stackoverflow.com/a/23118765/366908
                elif hasattr(connections[self.queryset.db].client.connection,
                             'pg_version'):
                    parts = [p.strip('"')
                             for p in
                             self.root_queryset.query.model._meta.db_table.split(
                                 '.')]
                    cursor = connections[self.queryset.db].cursor()
                    if len(parts) == 1:
                        cursor.execute(
                            'SELECT reltuples::bigint FROM pg_class WHERE relname = %s',
                            parts)
                    else:
                        cursor.execute(
                            'SELECT reltuples::bigint FROM pg_class c JOIN pg_namespace n ON (c.relnamespace = n.oid) WHERE n.nspname = %s AND c.relname = %s',
                            parts)
                else:
                    raise NotImplementedError
                full_result_count = int(cursor.fetchone()[0])
            except:
                full_result_count = self.root_queryset.count()

        can_show_all = result_count <= self.list_max_show_all
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.queryset._clone()
        else:
            try:
                result_list = paginator.page(self.page_num + 1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator

        # Admin actions are shown if there is at least one entry
        # or if entries are not counted because show_full_result_count is disabled
        self.show_admin_actions = bool(full_result_count)


class LargeTablePaginator(Paginator):
    """Overrides the count method to get an estimate instead of actual count
    when not filtered."""

    def _get_count(self):
        """Changed to use an estimate if the estimate is greater than 10,000
        Returns the total number of objects, across all pages."""
        if self._count is None:
            try:
                estimate = 0
                if not self.object_list.query.where:
                    try:
                        cursor = connection.cursor()
                        cursor.execute(
                            'SELECT reltuples FROM pg_class WHERE relname = %s',
                            [self.object_list.query.model._meta.db_table])
                        estimate = int(cursor.fetchone()[0])
                    except:
                        pass
                if estimate < 1000:
                    self._count = self.object_list.count()
                else:
                    self._count = estimate
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class OptAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        return LargeTableChangeList

    paginator = LargeTablePaginator

    def user_email(self, instance):
        return instance.user.email