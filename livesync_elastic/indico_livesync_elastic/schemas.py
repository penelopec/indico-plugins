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
from marshmallow.fields import Boolean, Function, Nested, Integer, String, Method
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import column2field, property2field

from tika import parser

from indico.core.marshmallow import mm
from indico.modules.categories.models.categories import Category
from indico.modules.events.models.events import Event
from indico.modules.events.contributions.models.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.events.notes.models.notes import EventNote, EventNoteRevision
from indico.modules.attachments.models.attachments import Attachment, AttachmentFile
from indico.modules.attachments.models.folders import AttachmentFolder

from indico.modules.groups.models.groups import LocalGroup
from indico.modules.users.schemas import UserSchema


class CategorySchema(mm.ModelSchema):
    category_path = List(String(), attribute='Category.chain_titles')

    class Meta:
        model = Category
        fields = ('id', 'category_path')


class EventPersonLinkSchema(mm.ModelSchema):
    class Meta:
        model = EventPersonLink
        fields = ('id', 'event_id', 'person_id', 'last_name', 'first_name', 'title', 'affiliation', 'address', 'phone')


class ContributionPersonLinkSchema(mm.ModelSchema):
    role = String(attribute='contribution.person_links.author_type.value')

    class Meta:
        model = ContributionPersonLink
        fields = ('id', 'contribution_id', 'person_id', 'last_name', 'first_name', 'title', 'affiliation', 'address', 'phone',
                  'is_speaker', 'author_type', 'diplay_order', 'role')


class SubcontributionPersonLinkSchema(mm.ModelSchema):
    role = String(default='Speaker')

    class Meta:
        model = SubcontributionPersonLink
        fields = ('id', 'subcontribution_id', 'person_id', 'last_name', 'first_name', 'title', 'affiliation', 'address', 'phone', 'role')


class EventSchema(mm.ModelSchema):
    _access = Nested('self', attribute='Event.acl_entries', many=True)
    category_path = Nested(CategorySchema, only=['category_path'], many=True)
    event_type = String(attribute='event.type.capitalize()')
    url = event.__mapper__.get_property('url')
    property2field(url)
    speaker_chairs = List(Nested(EventPersonLinkSchema(attribute='person_links', many=True)))

    class Meta:
        model = Event
        fields = ('_access', 'id', 'category_path', 'event_type', 'url', 'creation_date', 'start_date',
                  'end_date', 'location', 'title', 'description', 'speaker_chairs')


class ContributionSchema(mm.Schema):
    _access = Nested('self', attribute='Contribution.acl_entries', many=True)
    category_path = Nested(CategorySchema, only=['category_path'], many=True)
    list_of_persons = List(Nested(ContributionPersonLinkSchema(attribute='person_links', many=True)))

    class Meta:
        model = Contribution
        fields = ('_access', 'id', 'category_path', 'event_id', 'url', 'creation_date', 'start_date',
                  'end_date', 'location', 'title', 'description', 'list_of_persons')


class SubcontributionsSchema(mm.Schema):
    _access = Nested('self', attribute='Subcontribution.acl_entries', many=True)
    category_path = Nested(CategorySchema, only=['category_path'], many=True)
    list_of_persons = List(Nested(SubcontributionPersonLinkSchema(attribute='person_links', many=True)))

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
        parsedFile = parser.from_file(AttachmentFile.filename)
        return parsedFile

    class Meta:
        model = AttachmentFile
        fields = ('id', 'filename', 'content')


class AttachmentSchema(mm.Schema):
    _access = Nested('self', attribute='Attachment.acl_entries', many=True)
    category_path = Nested(CategorySchema, only=['category_path'], many=True)
    filename = String(Nested(AttachmentFileSchema, only=['filename']) )
    content = String(Nested(AttachmentFileSchema, only=['content']) )
    event_id = Integer(Nested(AttachmentFolderSchema, only=['event_id']))
    contribution_id = Integer(Nested(AttachmentFolderSchema, only=['contribution_id']))
    subcontribution_id = Integer(Nested(AttachmentFolderSchema, only=['subcontribution_id']))

    url = String(attribute='Attachment.absolute_download_url')

    class Meta:
        model = Attachment
        fields = ('_access', 'id', 'category_path', 'event_id', 'contribution_id', 'subcontribution_id', 'url',
                  'creation_date', 'filename', 'content')


class NotesSchema(mm.Schema):
    _access = Nested('self', attribute='Notes.acl_entries', many=True)
    category_path = Nested(CategorySchema, only=['category_path'], many=True)
    content = String(attribute='EventNoteRevision.source')

    class Meta:
        model = EventNoteRevision
        fields = ('_access', 'id', 'category_path', 'event_id', 'contribution_id', 'subcontribution_id', 'url',
                  'creation_date', 'content')


event_schema = EventSchema()
contribution_schema = ContributionSchema()
subcontribution_schema = SubcontributionSchema()
attachment_schema = AttachmentSchema()
notes_schema = NotesSchema()
