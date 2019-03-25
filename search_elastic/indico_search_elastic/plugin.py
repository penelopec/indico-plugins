# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from wtforms.fields.core import SelectField
from wtforms.fields.html5 import URLField
from wtforms.validators import URL

from indico.core.plugins import IndicoPluginBlueprint
from indico.web.forms.base import IndicoForm

from indico_search import SearchPluginBase
from indico_search_elastic import _
from indico_search_elastic.engine import ElasticSearchEngine


class SettingsForm(IndicoForm):
    search_url = URLField(_('Elasticsearch URL'), [URL()])
    display_mode = SelectField(_('Display mode'), choices=[('iframe', _('Embedded (IFrame)')),
                                                           ('redirect', _('External (Redirect)'))])


class ElasticSearchPlugin(SearchPluginBase):
    """Elastic Search

    Uses Elasticsearch as Indico's search engine
    """
    configurable = True
    settings_form = SettingsForm
    default_settings = {
        'search_url': 'https://search.elastic.ch/Pages/IndicoFrame.aspx',
        'display_mode': 'iframe'
    }
    engine_class = ElasticSearchEngine

    def get_blueprints(self):
        return IndicoPluginBlueprint('search_elastic', 'indico_search_elastic')
