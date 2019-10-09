# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from indico_livesync import LiveSyncPluginBase
from indico_livesync_json.backend import LivesyncJsonBackend, LivesyncJsonForm
from indico_livesync_json.blueprint import blueprint


class LivesyncJsonPlugin(LiveSyncPluginBase):
    """LiveSync JSON

    Provides the JSON-search backend for LiveSync
    """

    configurable = True
    settings_form = LivesyncJsonForm
    default_settings = {'search_app_url': '',
                        'search_app_token': '', 
                        'es_events': 'events_v1.1.0.json',
                        'es_contributions': 'contributions_v1.1.0.json',
                        'es_subcontributions': 'subcontributions_v1.1.0.json',
                        'es_attachments': 'attachments_v1.1.0.json',
                        'es_notes': 'notes_v1.1.0.json',
                        'tika_server': ''
                        }
    backend_classes = {'livesyncjson': LivesyncJsonBackend}

    def get_blueprints(self):
        return blueprint
