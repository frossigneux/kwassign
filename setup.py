#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: François Rossigneux <francois.rossigneux@inria.fr>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import setuptools

from kwassign.openstack.common import setup as common_setup

requires = common_setup.parse_requirements(['pip-requires'])
depend_links = common_setup.parse_dependency_links(['pip-requires'])
project = 'kwassign'
version = common_setup.get_version(project, '2013.3')


setuptools.setup(

    name='kwassign',
    version=version,

    description='Assigning power consumption to virtual cluster tenants.',

    author='François Rossigneux',
    author_email='francois.rossigneux@inria.fr',

    url='https://github.com/frossigneux/kwassign',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Setuptools Plugin',
        'Environment :: OpenStack',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ],

    packages=setuptools.find_packages(),

    scripts=['bin/kwassign'],

    data_files=[('etc/kwassign', ['etc/kwassign/kwassign.conf'])],

    install_requires=requires,
    dependency_links=depend_links,
)
