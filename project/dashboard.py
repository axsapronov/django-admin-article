# -*- coding: utf-8 -*-


from admin_tools.dashboard import Dashboard, AppIndexDashboard, modules
from admin_tools.utils import get_admin_site_name
from django.utils.translation import ugettext_lazy as _


def accounts_models():
    children = []

    children.append(modules.Group(
        title=_('Block1'),
        display='tabs',
        children=[
            modules.ModelList(title=_('Category1'),
                              models=('app.models.*',)),
            modules.ModelList(title=_('Category2'),
                              models=('app.models.ModelA',
                                      'app.models.ModelB',)
                              ),
        ]
    ))

    children.append(modules.Group(
        title=_('Block2'),
        display='tabs',
        children=[
            modules.ModelList(
                title=_('Category3'),
                models=(
                    'app.models.ModelA',
                    'app.models.ModelD',
                ),
            ),
        ]
    ))

    return children


class AdminDashboard(Dashboard):
    """Custom index dashboard for site."""
    columns = 2

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        self.children.extend(accounts_models())


class AppDashboard(AppIndexDashboard):
    """Custom app index dashboard for site."""
    columns = 2

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        if self.app_title == 'App':
            self.children.extend(accounts_models())
        else:
            self.children.append(
                modules.ModelList(
                    self.app_title,
                    self.models))

    def init_with_context(self, context):
        """Use this method if you need to access the request context."""
        return super(AppDashboard, self).init_with_context(context)
