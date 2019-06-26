# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from indico_livesync import LiveSyncPluginBase
from indico_livesync_json.backend import JsonLiveSyncBackend
from indico_livesync_json.blueprint import blueprint
from indico_livesync_json.forms import SettingsForm


class JsonLiveSyncPlugin(LiveSyncPluginBase):
    """LiveSync JSON

    Provides the JSON-search backend for LiveSync
    """

    configurable = True
    settings_form = SettingsForm
    default_settings = {'search_repository': 'indico',
                        'username': '', 
                        'password': ''}
    backend_classes = {'jsonsearch': JsonLiveSyncBackend}

    def get_blueprints(self):
        return blueprint
