# This file is part of Indico.
# Copyright (C) 2002 - 2018 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from marshmallow import Schema, ValidationError, fields, post_dump, validate, validates_schema
from marshmallow.fields import Nested, String, Method

from indico.core.marshmallow import mm
from indico.modules.events.models.events import Event
from indico.modules.events.contributions.models.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.events.notes.models.notes import EventNote, EventNoteRevision
from indico.modules.attachments.models.attachments import Attachment, AttachmentFile
from indico.modules.attachments.models.folders import AttachmentFolder


class EventSchema(mm.ModelSchema):
    _access = String(default='access emails and indico groups')
    category_path = String(default='category path chain titlees')
    url = String(default='https://indico.domain.gov/event/id')
    speaker_chairs = List(String())

    class Meta:
        model = Event
        fields = ('_access', 'id', 'category_path', 'event_type', 'url', 'creation_date', 'start_date',
                  'end_date', 'location', 'title', 'description', 'speaker_chairs')


class ContributionSchema(mm.Schema):
    _access = String(default='access emails and indico groups')
    category_path = String(default='category path chain titlees')
    url = String(default='https://indico.domain.gov/contribution/id')
    list_of_persons = List(String())

    class Meta:
        model = Contribution
        fields = ('_access', 'id', 'category_path', 'event_id', 'url', 'creation_date', 'start_date',
                  'end_date', 'location', 'title', 'description', 'list_of_persons')


class SubcontributionsSchema(mm.Schema):
    _access = String(default='access emails and indico groups')
    category_path = String(default='category path chain titlees')
    url = String(default='https://indico.domain.gov/subcontribution/id')
    list_of_persons = List(String())

    class Meta:
        model = Subcontribution
        fields = ('_access', 'id', 'category_path', 'event_id', 'contribution_id', 'url', 'creation_date', 'start_date',
                  'end_date', 'location', 'title', 'description', 'list_of_persons')


class AttachmentFolderSchema(mm.Schema):

    class Meta:
        model = AttachmentFolder
        fields = ('id', 'title', 'description', 'is_deleted', 'is_default', 'is_always_visible',
                  'is_hidden', 'session_id', 'event_id', 'linked_event_id', 'contribution_id',
                  'subcontribution_id', 'category_id', 'link_type', 'protection_mode')


class AttachmentFileSchema(mm.Schema):
    filename = String(attribute=AttachmentFile.filename)
    content = Method('get_attachment_content', dump_only=True)

    def get_attachment_content(self, AttachmentFile):
        parsedFile = 'File content using tika function: parser.from_file(AttachmentFile.filename)'
        return parsedFile

    class Meta:
        model = AttachmentFile
        fields = ('id', 'filename', 'content')


class AttachmentSchema(mm.Schema):
    _access = String(default='access emails and indico groups')
    category_path = String(default='category path chain titlees')
    url = String(default='https://indico.domain.gov/attachement/id')    
    filename = Nested(AttachmentFileSchema, only=('filename'))
    content = Nested(AttachmentFileSchema, only=('content'))
    event_id = Nested(AttachmentFolderSchema, only=('event_id'))
    contribution_id = Nested(AttachmentFolderSchema, only=('contribution_id'))
    subcontribution_id = Nested(AttachmentFolderSchema, only=('subcontribution_id'))

    class Meta:
        model = Attachment
        fields = ('_access', 'id', 'category_path', 'event_id', 'contribution_id', 'subcontribution_id', 'url',
                  'creation_date', 'filename', 'content')


class NoteSchema(mm.Schema):
    _access = String(default='access emails and indico groups')
    category_path = String(default='category path chain titlees')
    url = String(default='https://indico.domain.gov/attachement/id')
    content = String('Notes text content')

    class Meta:
        model = EventNoteRevision
        fields = ('_access', 'id', 'category_path', 'event_id', 'contribution_id', 'subcontribution_id', 'url',
                  'creation_date', 'content')


class ElasticItemSchema(Schema):
    _index = String(default='indico')
    _type = String(default='events')
    _id = Integer()

    class Meta:
        fields = ('_index', '_type', '_id')


class ElasticActionSchema(Schema):
    index = Nested(ElasticItemSchema(), default=None)
    delete = Nested(ElasticItemSchema(), default=None)

    class Meta:
        fields = ('index', 'delete')
    
    @post_dump
    def clean_missing(self, data):
        for key in filter(lambda key: data[key] is None, data):
            data.pop(key)
        return data    


elastic_schema = ElasticActionSchema()
event_schema = EventSchema()
contribution_schema = ContributionSchema()
subcontribution_schema = SubcontributionSchema()
attachment_schema = AttachmentSchema()
note_schema = NotesSchema()
