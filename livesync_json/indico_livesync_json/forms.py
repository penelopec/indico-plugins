# NOT USED
# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from wtforms.fields import StringField
from wtforms.validators import DataRequired

from indico.web.forms.base import IndicoForm
from indico.web.forms.fields import IndicoPasswordField

from indico_livesync_json import _


class SettingsForm(IndicoForm):
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
    es_subcontributions = StringField(_('Elasticsearch SubContributions JSON Schema'), [DataRequired()],,
                          description=_("<subcontributions_vn.n.n.json>: the JSON Schema for the subcontributions ES index"))
    es_attachments = StringField(_('Elasticsearch Attachments JSON Schema'), [DataRequired()],
                          description=_("<attachments_vn.n.n.json>: the JSON Schema for the attachments ES index"))
    es_notes = StringField(_('Elasticsearch Notes JSON Schema'), [DataRequired()],
                          description=_("<notes_vn.n.n.json>: the JSON Schema for the notes ES index"))
