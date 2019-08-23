# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from indico_livesync import LiveSyncPluginBase
from indico_livesync_json.backend import LivesyncJsonBackend, LivesyncJsonAgentForm
from indico_livesync_json.blueprint import blueprint


class LivesyncJsonPlugin(LiveSyncPluginBase):
    """LiveSync JSON

    Provides the JSON-search backend for LiveSync
    """

    configurable = True
    settings_form = LivesyncJsonAgentForm
    default_settings = {'search_app_url': '',
                        'search_app_token': '', 
                        'es_events': '',
                        'es_contributions': '',
                        'es_subcontributions': '',
                        'es_attachments': '',
                        'es_notes': '',
                        'tika_server': ''
                        }
    backend_classes = {'jsonsearch': LivesyncJsonBackend}

    def get_blueprints(self):
        return blueprint
