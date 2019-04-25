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

from indico_livesync_elastic import _


class SettingsForm(IndicoForm):
    repository = StringField(_("Repository"), validators=[DataRequired()],
                           description=_("The Elasticsearch top index name"))
    username = StringField(_("Username"), validators=[DataRequired()],
                           description=_("The username to access the Elasticsearch index mappings"))
    password = IndicoPasswordField(_('Password'), [DataRequired()], toggle=True,
                                   description=_("The password to access the Elasticsearch index mappings"))
