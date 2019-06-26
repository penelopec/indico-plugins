# This file is part of the Indico plugins.
# Copyright (C) 2014 - 2018 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

from setuptools import find_packages, setup


setup(
    name='indico-plugin-livesync-json',
    version='1.0',
    #url='https://github.com/indico/indico-plugins',
    url='https://github.com/penelopec/indico-plugins/tree/Elasticsearch/livesync_json',
    license='MIT',
    author='Indico Team',
    author_email='indico-team@cern.ch',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'indico>=2.0',
        'indico-plugin-livesync>=1.0'
    ],
    entry_points={
        'indico.plugins': {'livesync_json = indico_livesync_json.plugin:JsonLiveSyncPlugin'}
    },
    classifiers=[
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
)
