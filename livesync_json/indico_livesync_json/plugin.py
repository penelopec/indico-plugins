# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from wtforms.fields.core import StringField
from wtforms.fields.html5 import URLField
from wtforms.validators import URL, DataRequired

from indico.web.forms.base import IndicoForm
from indico_livesync import LiveSyncPluginBase
from indico_livesync_json.backend import livesyncjson_backend
from indico_livesync_json.blueprint import blueprint


class livesyncjson_settingsform(IndicoForm):
    search_app_url = URLField(_('Search app URL'), [DataRequired(), URL(require_tld=False)],
                          description=_("URL <url:port> of search app import endpoint"))
    search_app_token = StringField(_('Search app TOKEN'), [DataRequired()],
                          description=_("TOKEN  for accessing the Search app import endpoint"))
    es_events = StringField(_('Elasticsearch Events JSON Schema'), [DataRequired()],
                          description=_("<events_vn.n.n.json>: the JSON Schema for the events Elasticsearch index"))
    es_contributions = StringField(_('Elasticsearch Contributions JSON Schema'), [DataRequired()],
                          description=_("<contributions_vn.n.n.json>: the JSON Schema for the contributions Elasticsearch index"))
    es_subcontributions = StringField(_('Elasticsearch SubContributions JSON Schema'), [DataRequired()],
                          description=_("<subcontributions_vn.n.n.json>: the JSON Schema for the subcontributions Elasticsearch index"))
    es_attachments = StringField(_('Elasticsearch Attachments JSON Schema'), [DataRequired()],
                          description=_("<attachments_vn.n.n.json>: the JSON Schema for the attachments Elasticsearch index"))
    es_notes = StringField(_('Elasticsearch Notes JSON Schema'), [DataRequired()],
                          description=_("<notes_vn.n.n.json>: the JSON Schema for the notes Elasticsearch index"))
    tika_server = URLField(_('tika server URL'), [DataRequired(), URL(require_tld=False)],
                          description=_("URL <url:port> of tika server to parse file content. If not supplied a local tika server will be instantiated."))


class LiveSyncJsonPlugin(LiveSyncPluginBase):
    """LiveSync JSON

    Provides the JSON-search backend for LiveSync
    """

    configurable = True
    settings_form = livesyncjson_settingsform
    default_settings = {'search_app_url': '',
                        'search_app_token': '', 
                        'es_events': 'events_v1.1.0.json',
                        'es_contributions': 'contributions_v1.1.0.json',
                        'es_subcontributions': 'subcontributions_v1.1.0.json',
                        'es_attachments': 'attachments_v1.1.0.json',
                        'es_notes': 'notes_v1.1.0.json',
                        'tika_server': ''
                        }
    backend_classes = {'livesyncjson': livesyncjson_backend}

    def get_blueprints(self):
        return blueprint
