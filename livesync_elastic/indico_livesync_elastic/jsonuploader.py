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

from indico_livesync import Uploader
from indico_livesync_elastic.jsongen import JSONGenerator


class JSONUploader(Uploader):
    def upload_records(self, records, from_queue):
        jsondata = JSONGenerator.records_to_json(records) if from_queue else JSONGenerator.objects_to_json(records)
        if jsondata is not None:
            self.upload_json(jsondata)

    def upload_json(self, jsondata):
        """Receives JSON strings to be uploaded"""
        raise NotImplementedError  # pragma: no cover
