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
import json

from indico.modules.events import Event
from indico.modules.events.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.attachments import Attachment
from indico.modules.events.notes.models.notes import EventNote

from indico_livesync_json.models.search_id_map import EntryType, Livesync_json_search_id_map_entry
from indico_livesync_json.schemas import EventSchema, ContributionSchema, SubContributionSchema, AttachmentSchema, EventNoteSchema
from indico_livesync import AgentForm, LiveSyncBackendBase, SimpleChange
from indico_livesync import Uploader
from indico_livesync_json import _


class LivesyncJsonAgentForm(AgentForm):
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
                          description=_("URL <url:port> of tika server to parse file content"))


class json_uploaderError(Exception):
    pass


class json_uploader(Uploader):

    def __init__(self, *args, **kwargs): 
        _search_app = self.backend.agent.settings.get('search_app_url').rstrip('/')
        endpoint = '/indico/records/'
        self.search_url = '{0}{1}'.format(_search_app, endpoint)
        self.headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': 'Bearer {}'.format(self.backend.agent.settings.get('search_app_token'))
                }
        
        # for the $schema: http://cernsearchdocs.web.cern.ch/cernsearchdocs/usage/schemas/
        # and http://cernsearchdocs.web.cern.ch/cernsearchdocs/usage/operations/
        endpoint = '/schemas/indico/'
        self.es_events = '$schema:{0}{1}{2}'.format(_search_app, endpoint, self.backend.agent.settings.get('es_events'))
        self.es_contributions = '$schema:{0}{1}{2}'.format(_search_app, endpoint, self.backend.agent.settings.get('es_contributions'))
        self.es_subcontributions = '$schema:{0}{1}{2}'.format(_search_app, endpoint, self.backend.agent.settings.get('es_subcontributions'))
        self.es_attachments = '$schema:{0}{1}{2}'.format(_search_app, endpoint, self.backend.agent.settings.get('es_attachments'))
        self.es_notes = '$schema:{0}{1}{2}'.format(_search_app, endpoint, self.backend.agent.settings.get('es_notes'))
        
        self.tika_server = self.backend.agent.settings.get('tika_server')

    def upload_records(self, records, from_queue):
        if from_queue:
            for entry, change in records.iteritems():
                jsondata, entry_type = get_jsondata(entry)
                if jsondata is not None:
                    self.upload_jsondata(jsondata, change, entry.id, entry_type)
        else:
            for entry in records:
                jsondata, entry_type = get_jsondata(entry)
                if jsondata is not None:
                    self.upload_jsondata(jsondata, SimpleChange.created, entry.id, entry_type)

    def get_jsondata(self, obj):
        if isinstance(obj, Event):
            return self.add_schema(EventSchema().jsonify(obj), self.es_events), EntryType.event
        elif isinstance(obj, Contribution):
            return  self.add_schema(ContributionSchema().jsonify(obj), self.es_contributions), EntryType.contribution
        elif isinstance(obj, SubContribution):
            return  self.add_schema(SubContributionSchema().jsonify(obj), self.es_subcontributions), EntryType.subcontribution
        elif isinstance(obj, Attachment):
            return  self.add_schema(AttachmentSchema().jsonify(obj), self.es_attachments), EntryType.attachment
        elif isinstance(obj, EventNote):
            return  self.add_schema(EventNoteSchema().jsonify(obj), self.es_notes), EntryType.note
        elif isinstance(obj, Category):
            return None
        else:
            raise ValueError('unknown object ref: {}'.format(obj))

    def add_schema(self, response, schema):
        data = response.get_json()
        data['$schema'] = schema
        response.data = json.dumps(data)
        return response

    def upload_jsondata(self, jsondata, change_type, obj_id, entry_type):
        # http://cernsearchdocs.web.cern.ch/cernsearchdocs/example/
        if change_type == SimpleChange.created:
            response = requests.post(self.search_url, headers=self.headers, json=jsondata)
        else:
            search_id = Livesync_json_search_id_map_entry.get_search_id(obj_id, entry_type)
            if search_id:
                if change_type == SimpleChange.updated:
                    response = requests.put('{}/{}'.format(self.search_url, search_id), headers=self.headers, 
                                            json=jsondata)
                elif change_type == SimpleChange.deleted:
                    response = requests.delete('{}/{}'.format(self.search_url, search_id), headers=self.headers, 
                                               json=jsondata)
                else:
                    pass
            else:
                pass

        if response.status_code != 200:
            raise json_uploaderError('{} - {}'.format(response.status_code, response.text))
        elif change_type == SimpleChange.created:
            if response.id:
                Livesync_json_search_id_map_entry.create(response.id, obj_id, entry_type)
            else:
                raise json_uploaderError('Cannot create the search id mapping: {} - {}'.format(response.status_code, response.text))


class LivesyncJsonBackend(LiveSyncBackendBase):
    """JSON-search

    This backend uploads data to JSON-search.
    """

    uploader = json_uploader
    form = LivesyncJsonAgentForm
