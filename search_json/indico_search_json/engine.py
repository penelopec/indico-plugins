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

from flask import redirect, request
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

        query_out = self._query()
        result = self._parse_query_out(query_out)
        return result 
    

    def _query(self):
        query_d = self._build_query()
        query_out_str = self._perform_query(query_d)
        query_out_json  = json.loads(query_out_str)
        return query_out_json


    def _build_query(self):
        qphrase = self._build_phrase_query()
        qdate = self._build_date_query()
        query = 'q=' + qphrase + qdate  # FIXME !! Is this needed ???
        query = query.replace(' ', '+')
        qpage = self._get_page_size()
        query = query + '&page=%s&size=%s' %(qpage, self.results_per_page)
        query_d = {}
        query_d['q'] = query
        return query_d


    def _build_phrase_query(self):
        phrase = self._get_arg_from_url('phrase')
        phrase = self._escape_symbols(phrase)
        field = self._get_arg_from_url('field')
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
        ####start_date = self.values['start_date']
        ####end_date = self.values['end_date']
        ####if start_date:
        ####    start_date = start_date.strftime('%Y-%m-%d')
        ####if end_date:
        ####    end_date = end_date.strftime('%Y-%m-%d')

        start_date = self._get_arg_from_url('start_date')
        end_date = self._get_arg_from_url('end_date')
        if start_date:
            start_date = self._fix_date_format(start_date)
        if end_date:
            end_date = self._fix_date_format(end_date)

        if start_date and end_date:
            qdate = ' AND date:[%s TO %s]' %(start_date, end_date)
        if start_date and not end_date:
            qdate = ' AND date:[%s TO *}' %start_date
        if not start_date and end_date:
            qdate = ' AND date:{* TO %s]' %end_date
        if not start_date and not end_date:
            qdate = ''
        return qdate


    def _fix_date_format(self, date_str):
        dd, mm, yyyy = date_str.split('/')
        return "%s-%s-%s" %(yyyy,mm,dd)


    def _get_page_size(self):
        return self._get_arg_from_url('page', '1')


    def _perform_query(self, query_d):
        """
        output of querying the CERN Search API looks like this

          {
            "aggregations": {},
            "hits": {
              "hits": [
                {
                  "created": "2018-03-19T08:16:53.218017+00:00",
                  "id": 5,
                  "links": {
                    "self": "http://<host:port>/api/record/5"
                  },
                  "metadata": {
                    "_access": {<access details>},
                    "control_number": "5",
                    "class": "B",
                    "description": "This is an awesome description for our first uploaded document",
                    "title": "Demo document"
                  },
                  "updated": "2018-03-19T08:16:53.218042+00:00"
                }
              ],
              "total": 2
            },
            "links": {
              "prev": "http://<host:port>/api/records/?page=1&size=1",
              "self": "http://<host:port>/api/records/?page=2&size=1"
            }
          }

        """
        endpoint = '/api/records/'  # FIXME, it has to be the same endpoint set by the livesync plugin
        url = '{0}{1}'.format(self.url, endpoint)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer <ACCESS_TOKEN>'
        }
        query_out = requests.get(url, headers=headers, query_d)
        if query_out.ok:
            return query_out.content


    def _parse_query_out(self, query_out):
        content = {}
        content["entries"] = []
        for result in query_out['hits']['hits']:
            content["entries"].append(result["metadata"])
        content["page"] = self._get_arg_from_url('page', '1')
        content["size"] = self.results_per_page
        content["total"] = query_out['hits']['total']
        return content


    def _get_arg_from_url(self, token, default=None):
        if not token.startswith('search-'):
            token = 'search-%s' %token
        value = request.args.get(token)
        if not value:
            value = default
        return value

