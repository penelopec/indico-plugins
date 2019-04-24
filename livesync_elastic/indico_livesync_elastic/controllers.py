# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from flask import current_app, jsonify, request
from sqlalchemy.orm import load_only
from werkzeug.exceptions import Unauthorized

from indico.modules.categories import Category
from indico.web.rh import RH


class RHCategoriesJSON(RH):
    """Provide category information for Elastic search"""

    """ ??? Ask CERN about this 
    def _check_access(self):
        from indico_livesync_elastic.plugin import ElasticLiveSyncPlugin
        auth = request.authorization
        username = ElasticLiveSyncPlugin.settings.get('username')
        password = ElasticLiveSyncPlugin.settings.get('password')
        if not auth or not auth.password or auth.username != username or auth.password != password:
            response = current_app.response_class('Authorization required', 401,
                                                  {'WWW-Authenticate': 'Basic realm="Indico - Elastic Search"'})
            raise Unauthorized(response=response)
    """

    def _process(self):
        query = (Category.query
                 .filter_by(is_deleted=False)
                 .options(load_only('id', 'title'))
                 .order_by(Category.id).all())
        return jsonify(categories=[{'id': c.id, 'title': c.title} for c in query])
