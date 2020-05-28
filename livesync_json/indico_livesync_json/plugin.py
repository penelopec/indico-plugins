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
from indico_livesync_json import _


class livesyncjson_settingsform(IndicoForm):
    searchapp_url = URLField(_('Search app URL'), [DataRequired()],
                          description=_("URL <url:port> of search app import endpoint"))
    searchapp_token = StringField(_('Search app TOKEN'), [DataRequired()],
                          description=_("TOKEN  for accessing the Search app import endpoint"))
    tika_server = URLField(_('tika server URL'), [DataRequired()],
                          description=_("URL <url:port> of tika server to parse file content. If not supplied a local tika server will be instantiated."))


class LiveSyncJsonPlugin(LiveSyncPluginBase):
    """LiveSync_JSON

    Provides the LiveSync-JSON agent for LiveSync
    """

    configurable = True
    settings_form = livesyncjson_settingsform
    default_settings = {'searchapp_url': '',
                        'searchapp_token': '', 
                        'tika_server': ''
                        }
    backend_classes = {'livesyncjson': livesyncjson_backend}

    def get_blueprints(self):
        return blueprint
