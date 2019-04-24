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

from flask_pluginengine import current_plugin

from indico.modules.categories.models.categories import Category
from indico.modules.attachments.models.attachments import Attachment
from indico.modules.events.contributions.models.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.events.notes.models.notes import EventNote
from indico.modules.events.models.events import Event

from indico_livesync import SimpleChange
from indico_livesync.util import compound_id, obj_ref
from indico_livesync_elastic import event_schema, contribution_schema, subcontribution_schema, attachment_schema, note_schema, elastic_schema


class JSONGenerator:
    """Generate JSON for Elasticsearch based on Indico objects."""

    @classmethod
    def records_to_json(cls, records):
        jg = JSONGenerator()
        for entry, change in records.iteritems():
            jg.safe_add_object(entry, bool(change & SimpleChange.deleted))
        return jg.get_json()

    @classmethod
    def objects_to_json(cls, objs, change_type=SimpleChange.created):
        jg = JSONGenerator()
        for obj in objs:
            jg.safe_add_object(obj_ref(obj), bool(change_type & SimpleChange.deleted))
        return jg.get_json()

    def __init__(self):
        from indico_livesync_elastic.plugin import ElasticLiveSyncPlugin
        self.closed = False
        self.esIndex = ElasticLiveSyncPlugin.settings.get('esIndex_name')
        self.jsonData = ''

    def get_json():
        return self.jsonData

    def safe_add_object(self, obj, deleted=False):
        try:
            self.add_object(obj, deleted)
        except Exception:
            current_plugin.logger.exception('Could not process %s', obj)

    def add_object(self, obj, deleted=False):
        if self.closed:
            raise RuntimeError('Cannot add object to closed json generator')
        if isinstance(obj, Event):
            self.jsonData += self._event_to_json(obj, deleted)
        elif isinstance(obj, Contribution):
            self.jsonData += self._contrib_to_json(obj, deleted)
        elif isinstance(obj, SubContribution):
            self.jsonData += self._subcontrib_to_json(obj, deleted)
        elif isinstance(obj, Attachment):
            self.jsonData += self._attachment_to_json(obj, deleted)
        elif isinstance(obj, EventNote):
            self.jsonData += self._note_to_json(obj, deleted)
        elif isinstance(obj, Category):
            pass  # we don't send category updates
        else:
            raise ValueError('unknown object ref: {}'.format(obj))
        return self.jsonData

    def _event_to_json(self, obj, deleted):
        js = '\n'
        esMapping = dict(_index=self.esIndex, _type='events', _id=obj.id)
        if (deleted):
            esAction = dict(delete=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
        else:
            esAction = dict(index=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
            js += '\n'
            rsObj = event_schema.dumps(obj)
            js += rsObj.data
        return js

    def _contrib_to_json(self, obj, deleted):
        js = '\n'
        esMapping = dict(_index=self.esIndex, _type='contributions', _id=obj.id)
        if (deleted):
            esAction = dict(delete=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
        else:
            esAction = dict(index=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
            js += '\n'
            rsObj = contribution_schema.dumps(obj)
            js += rsObj.data
        return js

    def _subcontrib_to_json(self, obj, deleted):
        js = '\n'
        esMapping = dict(_index=self.esIndex, _type='subcontributions', _id=obj.id)
        if (deleted):
            esAction = dict(delete=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
        else:
            esAction = dict(index=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
            js += '\n'
            rsObj = subcontribution_schema.dumps(obj)
            js += rsObj.data
        return js

    def _attachment_to_json(self, obj, deleted):
        js = '\n'
        esMapping = dict(_index=self.esIndex, _type='attachments', _id=obj.id)
        if (deleted):
            esAction = dict(delete=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
        else:
            esAction = dict(index=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
            js += '\n'
            rsObj = attachment_schema.dumps(obj)
            js += rsObj.data
        return js

    def _note_to_json(self, obj, deleted):
        js = '\n'
        esMapping = dict(_index=self.esIndex, _type='notes', _id=obj.id)
        if (deleted):
            esAction = dict(delete=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
        else:
            esAction = dict(index=esMapping)
            rs = elastic_schema.dumps(esAction)
            js += rs.data
            js += '\n'
            rsObj = note_schema.dumps(obj)
            js += rsObj.data
        return js
