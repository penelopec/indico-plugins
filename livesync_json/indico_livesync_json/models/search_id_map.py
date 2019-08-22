# This file is part of the Indico plugins.
# Copyright (C) 2002 - 2019 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

from __future__ import unicode_literals

from flask import g
from werkzeug.datastructures import ImmutableDict

from indico.core.db.sqlalchemy import PyIntEnum, UTCDateTime, db
from indico.modules.categories.models.categories import Category
from indico.modules.events.models.events import Event
from indico.modules.events.contributions.models.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.attachments import Attachment
from indico.modules.events.notes.models.notes import EventNote
from indico.util.date_time import now_utc
from indico.util.string import format_repr, return_ascii
from indico.util.struct.enum import IndicoEnum

from indico_livesync.models.agents import LiveSyncAgent
from indico_livesync.util import obj_deref


class EntryType(int, IndicoEnum):
    event = 1
    contribution = 2
    subcontribution = 3
    attachment = 4
    note = 5


_column_for_types = {
    EntryType.event: 'event_id',
    EntryType.contribution: 'contribution_id',
    EntryType.subcontribution: 'subcontribution_id',
    EntryType.attachment: 'attachment_id',
    EntryType.note: 'note_id'
}


def _make_checks():
    available_columns = set(_column_for_types.viewvalues())
    for link_type in EntryType:
        required_col = _column_for_types[link_type]
        forbidden_cols = available_columns - {required_col}
        criteria = ['{} IS NULL'.format(col) for col in sorted(forbidden_cols)]
        criteria += ['{} IS NOT NULL'.format(required_col)]
        condition = 'type != {} OR ({})'.format(link_type, ' AND '.join(criteria))
        yield db.CheckConstraint(condition, 'valid_{}_entry'.format(link_type.name))


class Livesync_json_cern_search_id_map_entry(db.Model):
    __tablename__ = 'cern_search_id_map'
    __table_args__ = tuple(_make_checks()) + ({'schema': 'plugin_livesync'},)

    #: Entry ID
    id = db.Column(
        db.Integer,
        autoincrement=True,
        primary_key=True
    )

    #: ID of the cernsearch this entry belongs to
    search_id = db.Column(
        'elasticsearch_id',
        db.Integer,
        nullable=False,
        index=True
    )

    #: Timestamp of the record entry
    timestamp = db.Column(
        UTCDateTime,
        nullable=False,
        default=now_utc
    )

    #: The type of the search entry object
    entry_type = db.Column(
        PyIntEnum(EntryType),
        nullable=False
    )

    #: ID of the search entry event
    event_id = db.Column(
        db.Integer,
        db.ForeignKey('events.events.id'),
        index=True,
        nullable=True
    )

    #: ID of the search entry contribution
    contrib_id = db.Column(
        'contribution_id',
        db.Integer,
        db.ForeignKey('events.contributions.id'),
        index=True,
        nullable=True
    )

    #: ID of the search entry subcontribution
    subcontrib_id = db.Column(
        'subcontribution_id',
        db.Integer,
        db.ForeignKey('events.subcontributions.id'),
        index=True,
        nullable=True
    )

    #: The ID of the search entry attachment
    attachment_id = db.Column(
        'attachment_id',
        db.Integer,
        db.ForeignKey('attachments.attachments.id'),
        index=True,
        nullable=True
    )

    #: ID of the search entry note
    note_id = db.Column(
        'note_id',
        db.Integer,
        db.ForeignKey('events.notes.id'),
        index=True,
        nullable=True
    )

    event = db.relationship(
        'Event',
        lazy=True,
        backref=db.backref(
            'livesync_json_es_entries',
            cascade='all, delete-orphan',
            lazy=True
        )
    )

    contribution = db.relationship(
        'Contribution',
        lazy=False,
        backref=db.backref(
            'livesync_json_es_entries',
            cascade='all, delete-orphan',
            lazy='dynamic'
        )
    )

    subcontribution = db.relationship(
        'SubContribution',
        lazy=False,
        backref=db.backref(
            'livesync_json_es_entries',
            cascade='all, delete-orphan',
            lazy='dynamic'
        )
    )

    attachment = db.relationship(
        'Attachment',
        lazy=False,
        backref=db.backref(
            'livesync_json_es_entries',
            cascade='all, delete-orphan',
            lazy='dynamic'
        )
    )

    note = db.relationship(
        'Note',
        lazy=False,
        backref=db.backref(
            'livesync_json_es_entries',
            cascade='all, delete-orphan',
            lazy='dynamic'
        )
    )
    
    @classmethod
    def get_search_id(cls, oid, obj_type):
        """Get the search_id for a given object type and id.

        :param oid: The id of the object
        :param obj_type: the EntryType of the object
        """
        
        obj = cls.query.get(oid).filter_by(entry_type=obj_type).first()
        if obj is None:
            return None
        return obj.search_id

    @classmethod
    def create(cls, eid, oid, obj_type):
        """Create a new mapping.

        :param eid: The search_id to map the oid to
        :param oid: The id of the object
        :param obj_type: the EntryType of the object
        """
        if obj_type == EntryType.event:
            entry = cls(search_id=eid, entry_type=obj_type, event_id=oid)
        elif obj_type == EntryType.contribution:
            entry = cls(search_id=eid, entry_type=obj_type, contrib_id=oid)
        elif obj_type == EntryType.subcontribution:
            entry = cls(search_id=eid, entry_type=obj_type, subcontrib_id=oid)
        elif obj_type == EntryType.attachment:
            entry = cls(search_id=eid, entry_type=obj_type, attachment_id=oid)
        elif obj_type == EntryType.note:
            entry = cls(search_id=eid, entry_type=obj_type, note_id=oid)
        else:
            return

        db.session.add(entry)
        db.session.flush()