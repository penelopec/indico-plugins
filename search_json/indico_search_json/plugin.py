# This file is part of the CERN Indico plugins.
# Copyright (C) 2014 - 2019 CERN
#
# The CERN Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from wtforms.fields.core import SelectField
from wtforms.fields.html5 import URLField, IntegerField
from wtforms.fields import core
from wtforms.validators import URL

from indico.core.plugins import IndicoPluginBlueprint
from indico.web.forms.base import IndicoForm

from indico_search import SearchPluginBase
from indico_search_json import _
from indico_search_json.engine import JSONSearchEngine


class SettingsForm(IndicoForm):
    search_url = URLField(_('CERN Search URL'),
                          [URL()],
                          description=_("URL for the CERN Search API"))
    results_per_page = IntegerField(_('Number of results per page'),
                                    [NumberRange(min=5)],
                                    description=_("Number of results to display on each page"))
    token = core.StringField('CERN Search token',
                             [DataRequired()],
                             description=_("CERN Search security token"))



class JSONSearchPlugin(SearchPluginBase):
    """JSON Search

    Uses JSONSearch as Indico's search engine
    """
    configurable = True
    settings_form = SettingsForm
    default_settings = {
        'search_url': 'https://search.cern.ch/Pages/IndicoFrame.aspx',
        'results_per_page': 10,
        'token': ''
    }
    engine_class = JSONSearchEngine

    def get_blueprints(self):
        return IndicoPluginBlueprint('search_json', 'indico_search_json')

