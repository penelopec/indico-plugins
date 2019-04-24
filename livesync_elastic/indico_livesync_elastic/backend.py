# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

import requests
from lxml import etree
from wtforms.fields.core import StringField
from wtforms.fields.html5 import URLField
from wtforms.validators import URL, DataRequired

from indico.web.forms.fields import IndicoPasswordField

from indico_livesync import AgentForm, LiveSyncBackendBase, JSONUploader
from indico_livesync_elastic import _


class ElasticAgentForm(AgentForm):
    server_url = URLField(_('URL'), [DataRequired(), URL(require_tld=False)],
                          description=_("The URL of Elasticsearch's import endpoint"))
    esIndex_name = StringField(_('Repository'), [DataRequired()])
    username = StringField(_('Username'), [DataRequired()])
    password = IndicoPasswordField(_('Password'), [DataRequired()], toggle=True)


class ElasticUploaderError(Exception):
    pass


class ElasticUploader(JSONUploader):
    def __init__(self, *args, **kwargs):
        super(ElasticUploader, self).__init__(*args, **kwargs)
        self.url = self.backend.agent.settings.get('server_url')
        self.repository = self.backend.agent.settings.get('esIndex_name')
        self.username = self.backend.agent.settings.get('username')
        self.password = self.backend.agent.settings.get('password')

    def upload_json(self, jsonData):
        response = requests.post(self.url, auth=(self.username, self.password), data={'json': jsonData})
        result_text = self._get_result_text(response.content)

        if response.status_code != 200 or result_text != 'true':
            raise ElasticUploaderError('{} - {}'.format(response.status_code, result_text))

    def _get_result_text(self, result):
        try:
            return etree.tostring(etree.fromstring(result), method="text")
        except etree.XMLSyntaxError:
            raise ElasticUploaderError('Invalid XML response: {}'.format(result))


class ElasticLiveSyncBackend(LiveSyncBackendBase):
    """Elasticsearch

    This backend uploads data to Elasticsearch.
    """

    uploader = ElasticUploader
    form = ElasticAgentForm
