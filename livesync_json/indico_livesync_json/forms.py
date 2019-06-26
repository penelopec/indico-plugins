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
    events = IndicoPasswordField(_('Elasticsearch Events JSON Schema'), [DataRequired()], toggle=True,
                          description=_("<events_vn.n.n.json>: the JSON Schema for the events Elasticsearch index"))
    contributions = IndicoPasswordField(_('Elasticsearch Contributions JSON Schema'), [DataRequired()], toggle=True,
                          description=_("<contributions_vn.n.n.json>: the JSON Schema for the contributions Elasticsearch index"))
    subcontributions = IndicoPasswordField(_('Elasticsearch SubContributions JSON Schema'), [DataRequired()], toggle=True,
                          description=_("<subcontributions_vn.n.n.json>: the JSON Schema for the subcontributions Elasticsearch index"))
    attachments = IndicoPasswordField(_('Elasticsearch Attachments JSON Schema'), [DataRequired()], toggle=True,
                          description=_("<attachments_vn.n.n.json>: the JSON Schema for the attachments Elasticsearch index"))
    notes = IndicoPasswordField(_('Elasticsearch Notes JSON Schema'), [DataRequired()], toggle=True,
                          description=_("<notes_vn.n.n.json>: the JSON Schema for the notes Elasticsearch index"))
