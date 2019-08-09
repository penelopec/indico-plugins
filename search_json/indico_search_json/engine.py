# This file is part of the CERN Indico plugins.
# Copyright (C) 2014 - 2019 CERN
#
# The CERN Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

import json
import re
import requests

from marshmallow import Schema, fields, post_load

from flask import redirect
from flask_pluginengine import current_plugin
from werkzeug.urls import url_encode

from indico.core.db import db
from indico.core.plugins import get_plugin_template_module
from indico_search import SearchEngine



#FIELD_MAP = {'title': 'titlereplica',
#             'abstract': 'description',
#             'author': 'authors',
#             'affiliation': 'companies',
#             'keyword': 'keywords'}


class JSONSearchEngine(SearchEngine):
   
    @property
    def url(self):
        return current_plugin.settings.get('search_url')

    @property
    def results_per_page(self):
        return current_plugin.settings.get('results_per_page')


    def process(self):

        # search values
        self.username = self.user.name
        self.useremail = self.user.email
        self.query_phrase = self.values['phrase']
        self.query_start_date = self.values['start_date']  # datetime.date object
        self.query_end_date = self.values['end_date']  # datetime.date object
        self.query_field = self.values['field']

        query_d = self._build_query()
        out = self._query(query_d)
        return out


    def _build_query(self):
        qphrase = self._build_phrase_query()
        qdate = self._build_date_query()
        query = 'q=' + qphrase + qdate  # FIXME !! Is this needed ???
        query = query.replace(' ', '+')
        query_d = {}
        query_d['q'] = query
        return query_d


    def _build_phrase_query(self):
        phrase = self.values['phrase']
        phrase = self._escape_symbols(phrase)
        field = self.values['field']
        phrase = ' OR '.join([x.strip() for x in phrase.split()])
        if field:
            qphrase = '%s:(%s)' %(field, phrase)
        else:
            qphrase = '(%s)' %phrase
        return qphrase


    def _escape_symbols(self, phrase):
        list_symbols = {'+':'\+',
                        '-':'\-',
                        '=':'\=',
                        '&&':'\&\&',
                        '||':'\|\|',
                        '>':'\>',
                        '<':'\<',
                        '!':'\!',
                        '(':'\(',
                        ')':'\)',
                        '{':'\{',
                        '}':'\}',
                        '[':'\[',
                        ']':'\]',
                        '^':'\^',
                        '"':'\\"',
                        '~':'\~',
                        '*':'\*',
                        '?':'\?',
                        ':':'\:',
                        '/':'\/'}

        # first, escape the backslashes 
        phrase = phrase.replace('\\', '\\\\')

        # then, escape the rest of symbols
        for k,v in list_symbols.items():
            phrase = phrase.replace(k, v)

        return phrase


    def _build_date_query(self):
        start_date = self.values['start_date']
        end_date = self.values['end_date']

        if start_date:
            start_date = start_date.strftime('%Y-%m-%d')
        if end_date:
            end_date = end_date.strftime('%Y-%m-%d')

        if start_date and end_date:
            qdate = ' AND date:[%s TO %s]' %(start_date, end_date)
        if start_date and not end_date:
            qdate = ' AND date:[%s TO *}' %start_date
        if not start_date and end_date:
            qdate = ' AND date:{* TO %s]' %end_date
        if not start_date and not end_date:
            qdate = ''
        return qdate


    def _query(self, query_d):
        endpoint = '/api/records/'  # FIXME, it has to be the same endpoint set by the livesync plugin
        url = '{0}{1}'.format(self.url, endpoint)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer <ACCESS_TOKEN>'
        }
        response = requests.get(url, headers=headers, query_d)
        if response.ok:
            content = json.loads(response.content)
            return content


