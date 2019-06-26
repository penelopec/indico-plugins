# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from indico.core.plugins import IndicoPluginBlueprint

from indico_livesync_json.controllers import RHCategoriesJSON


blueprint = IndicoPluginBlueprint('livesync_json', __name__)

blueprint.add_url_rule('/livesync/jsonsearch/categories.json', 'categories_json', RHCategoriesJSON)
