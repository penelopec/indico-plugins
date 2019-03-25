# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from indico_livesync import LiveSyncPluginBase
from indico_livesync_elastic.backend import ElasticLiveSyncBackend
from indico_livesync_elastic.blueprint import blueprint
from indico_livesync_elastic.forms import SettingsForm


class ElasticLiveSyncPlugin(LiveSyncPluginBase):
    """LiveSync Elastic

    Provides the Elasticsearch backend for LiveSync
    """

    configurable = True
    settings_form = SettingsForm
    default_settings = {'username': 'elasticsearch', 'password': ''}
    backend_classes = {'elasticsearch': ElasticLiveSyncBackend}

    def get_blueprints(self):
        return blueprint
