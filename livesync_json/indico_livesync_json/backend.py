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
import base64
import json

from indico.web.forms.fields import IndicoPasswordField
from indico.modules.events import Event
from indico.modules.events.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.attachments import Attachment
from indico.modules.events.notes.models.notes import EventNote

from indico_livesync_json.schemas import EventSchema, ContributionSchema, SubContributionSchema, AttachmentSchema, EventNoteSchema
from indico_livesync import AgentForm, LiveSyncBackendBase, SimpleChange
from indico_livesync import Uploader
from indico_livesync_json import _


class JsonAgentForm(AgentForm):
    search_app = URLField(_('Search app URL'), [DataRequired(), URL(require_tld=False)],
                          description=_("URL <url:port> of search app import endpoint"))
    username = StringField(_('Search app Username'), [DataRequired()],
                          description=_("User name for accessing the Search app import endpoint"))
    password = IndicoPasswordField(_('Search app Password'), [DataRequired()], toggle=True,
                          description=_("Password for accessing the Search app import endpoint"))
    tika_server = URLField(_('tika server URL'), [DataRequired(), URL(require_tld=False)],
                          description=_("URL <url:port> of tika server to parse file content"))
    es_server = URLField(_('Elasticsearch URL'), [DataRequired(), URL(require_tld=False)],
                          description=_("URL <http://<host:port>/schemas/instance/> of Elasticsearch endpoint"))
    es_events = StringField(_('Elasticsearch Events JSON Schema'), [DataRequired()],
                          description=_("<events_vn.n.n.json>: the JSON Schema for the events ES index"))
    es_contributions = StringField(_('Elasticsearch Contributions JSON Schema'), [DataRequired()],
                          description=_("<contributions_vn.n.n.json>: the JSON Schema for the contributions ES index"))
    es_subcontributions = StringField(_('Elasticsearch SubContributions JSON Schema'), [DataRequired()],
                          description=_("<subcontributions_vn.n.n.json>: the JSON Schema for the subcontributions ES index"))
    es_attachments = StringField(_('Elasticsearch Attachments JSON Schema'), [DataRequired()],
                          description=_("<attachments_vn.n.n.json>: the JSON Schema for the attachments ES index"))
    es_notes = StringField(_('Elasticsearch Notes JSON Schema'), [DataRequired()],
                          description=_("<notes_vn.n.n.json>: the JSON Schema for the notes ES index"))


class json_uploaderError(Exception):
    pass


class json_uploader(Uploader):
    def __init__(self, *args, **kwargs): 
        instance = self.backend.agent.settings.get('search_app')
        endpoint = '/api/records/'
        self.search_url = '{0}{1}'.format(instance, endpoint)
        self.username = self.backend.agent.settings.get('username')
        self.password = self.backend.agent.settings.get('password')
        self.headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
        
        """ Alternate code for the headers
        if self.backend.agent.settings.get('token'):
            authorization = 'Bearer {}'.format(self.backend.agent.settings.get('token'))
        else:
            authorization = 'Basic {}'.format(base64.b64encode("self.username:self.password"))
        self.headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': authorization
                }
        """
        
        self.tika_server = self.backend.agent.settings.get('tika_server')
        es_server = self.backend.agent.settings.get('es_server').rstrip('/')
        self.es_events = '$schema:{}/{}'.format(es_server, self.backend.agent.settings.get('es_events'))
        self.es_contributions = '$schema:{}/{}'.format(es_server, self.backend.agent.settings.get('es_contributions'))
        self.es_subcontributions = '$schema:{}/{}'.format(es_server, self.backend.agent.settings.get('es_subcontributions'))
        self.es_attachments = '$schema:{}/{}'.format(es_server, self.backend.agent.settings.get('es_attachments'))
        self.es_notes = '$schema:{}/{}'.format(es_server, self.backend.agent.settings.get('es_notes'))


    def upload_records(self, records, from_queue):
        if from_queue:
            for entry, change in records.iteritems():
                jsondata = get_jsondata(entry)
                if jsondata is not None:
                    self.upload_jsondata(jsondata, change, entry.id)
        else:
            for entry in records:
                jsondata = get_jsondata(entry)
                if jsondata is not None:
                    self.upload_jsondata(jsondata, SimpleChange.created, entry.id)

    def get_jsondata(self, obj):
        if isinstance(obj, Event):
            return self.add_schema(EventSchema().jsonify(obj), self.es_events)
        elif isinstance(obj, Contribution):
            return  self.add_schema(ContributionSchema().jsonify(obj), self.es_contributions)
        elif isinstance(obj, SubContribution):
            return  self.add_schema(SubContributionSchema().jsonify(obj), self.es_subcontributions)
        elif isinstance(obj, Attachment):
            return  self.add_schema(AttachmentSchema().jsonify(obj), self.es_attachments)
        elif isinstance(obj, EventNote):
            return  self.add_schema(EventNoteSchema().jsonify(obj), self.es_notes)
        elif isinstance(obj, Category):
            return None
        else:
            raise ValueError('unknown object ref: {}'.format(obj))

    def add_schema(self, response, schema):
        data = response.get_json()
        data['$schema'] = schema
        response.data = json.dumps(data)
        return response

    def upload_jsondata(self, jsondata, change_type, id):
        TEST = True
        if TEST:
            f = open('/opt/indico/log/livesync.log', 'w') 
            f.write('Type = {} - object ID = {} - json = \n{}\n\n'.format(change_type, id, jsondata))
            f.close()
        else:
            if change_type == SimpleChange.created:
                response = requests.post(self.search_url, auth=(self.username, self.password), 
                                         json=jsondata, headers=self.headers)
            elif change_type == SimpleChange.updated:
                response = requests.put('{}{}'.format(self.search_url, id), auth=(self.username, self.password), 
                                        json=jsondata, headers=self.headers)
            elif change_type == SimpleChange.deleted:
                response = requests.delete('{}{}'.format(self.search_url, id), auth=(self.username, self.password), 
                                           json=jsondata, headers=self.headers)
            else:
                pass

            if response.status_code != 200:
                raise json_uploaderError('{} - {}'.format(response.status_code, response.text))


class JsonLiveSyncBackend(LiveSyncBackendBase):
    """JSON-search

    This backend uploads data to JSON-search.
    """

    uploader = json_uploader
    form = JsonAgentForm