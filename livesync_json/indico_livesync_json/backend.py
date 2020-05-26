# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

import requests
from lxml import etree
import json

from indico.web.forms.base import IndicoForm
from indico.modules.events import Event
from indico.modules.events.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.attachments import Attachment
from indico.modules.events.notes.models.notes import EventNote

from indico_livesync_json.models.search_id_map import EntryType, livesyncjson_searchapp_id_map
from indico_livesync_json.schemas import EventSchema, ContributionSchema, SubContributionSchema, AttachmentSchema, EventNoteSchema
from indico_livesync import LiveSyncBackendBase, SimpleChange
from indico_livesync import Uploader
from indico_livesync_json import _


class livesyncjson_uploaderError(Exception):
    pass


class livesyncjson_uploader(Uploader):

    def __init__(self, *args, **kwargs): 
        from indico_livesync_json.plugin import LiveSyncJsonPlugin
        
        search_app = LiveSyncJsonPlugin.settings.get('searchapp_url').rstrip('/')
        endpoint = '/indico/records/'
        self.search_url = '{0}{1}'.format(search_app, endpoint)
        self.headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': 'Bearer {}'.format(LiveSyncJsonPlugin.settings.get('searchapp_token'))
                }

        endpoint = '/schemas/indico/'
        self.es_events = '$schema:{0}{1}{2}'.format(search_app, endpoint, 'events_v1.1.0.json')
        self.es_contributions = '$schema:{0}{1}{2}'.format(search_app, endpoint, 'contributions_v1.1.0.json')
        self.es_subcontributions = '$schema:{0}{1}{2}'.format(search_app, endpoint, 'subcontributions_v1.1.0.json')
        self.es_attachments = '$schema:{0}{1}{2}'.format(search_app, endpoint, 'attachments_v1.1.0.json')
        self.es_notes = '$schema:{0}{1}{2}'.format(search_app, endpoint, 'notes_v1.1.0.json')
        self.tika_server = LiveSyncJsonPlugin.settings.get('tika_server')

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
        if change_type == SimpleChange.created:
            response = requests.post(self.search_url, headers=self.headers, json=jsondata)
        else:
            search_id = livesyncjson_searchapp_id_map.get_search_id(obj_id, entry_type)
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
            raise livesyncjson_uploaderError('{} - {}'.format(response.status_code, response.text))
        elif change_type == SimpleChange.created:
            content = json.loads(response.content)
            if content["control_number"]:
                livesyncjson_searchapp_id_map.create(content["control_number"], obj_id, entry_type)
            else:
                raise livesyncjson_uploaderError('Cannot create the search id mapping: {} - {}'.format(response.status_code, response.text))


class livesyncjson_backend(LiveSyncBackendBase):
    """LiveSync-JSON

    This backend uploads data to CERN-search.
    """

    uploader = livesyncjson_uploader
