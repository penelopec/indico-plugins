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

from indico.core.plugins import IndicoPluginBlueprint

from indico_vc_zoom.controllers import RHZoomRoomOwner


blueprint = IndicoPluginBlueprint('vc_zoom', 'indico_vc_zoom')

# Room management
# using any(zoom) instead of defaults since the event vc room locator
# includes the service and normalization skips values provided in 'defaults'
blueprint.add_url_rule('/event/<confId>/manage/videoconference/<any(zoom):service>/<int:event_vc_room_id>/room-owner',
                       'set_room_owner', RHZoomRoomOwner, methods=('POST',))
