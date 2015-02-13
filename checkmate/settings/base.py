# -*- coding: utf-8 -*-
"""
This file is part of checkmate, a meta code checker written in Python.

Copyright (C) 2015 Andreas Dewes, QuantifiedCode UG

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from checkmate.lib.stats.helpers import directory_splitter
from checkmate.lib.models import (DiskProject,
                                  DiskSnapshot,
                                  DiskFileRevision,
                                  Issue,
                                  IssueClass,
                                  CodeObject)

import logging
import sys
import traceback

logger = logging.getLogger(__name__)

language_patterns = { 'python':
                        {
                            'name' : 'Python',
                            'patterns' : [u'\.py$',u'\.pyw$'],
                        },
                      'javascript' : {
                            'name' : 'Javascript',
                            'patterns' : [u'\.js$'],
                      },
                      'php' : {
                            'name' : 'PHP',
                            'patterns' : [u'\.php$'],
                      },
                      'ruby' : {
                            'name' : 'Ruby',
                            'patterns' : [u'\.rb'],
                      },
                    }

analyzers = {}

commands = {
    'init' : 'checkmate.management.commands.init.Command',
    'analyze' : 'checkmate.management.commands.analyze.Command',
    'reset' : 'checkmate.management.commands.reset.Command',
    'shell' : 'checkmate.management.commands.shell.Command',
    'summary' : 'checkmate.management.commands.summary.Command',
    'snapshots' : 'checkmate.management.commands.snapshots.Command',
    'issues' : 'checkmate.management.commands.issues.Command',
}

models = {
    'DiskProject' : DiskProject,
    'DiskSnapshot' : DiskSnapshot,
    'DiskFileRevision' : DiskFileRevision,
    'Issue' : Issue,
    'IssueClass' : IssueClass,
    'CodeObject' : CodeObject,
}

plugins = {
           'pep8' : 'checkmate.contrib.plugins.python.pep8',
           'pylint' : 'checkmate.contrib.plugins.python.pylint',
           'pyflakes' : 'checkmate.contrib.plugins.python.pyflakes',
           'jshint' : 'checkmate.contrib.plugins.javascript.jshint',
           'metrics' : 'checkmate.contrib.plugins.python.metrics',
           'git' : 'checkmate.contrib.plugins.git',
           }

aggregators = {
    'directory' :
        {
            'mapper' : lambda file_revision:directory_splitter(file_revision['path'])
        }
}

{
    'type' : 'import',
    'name' : 'foo.bar',
    'imported_names' : ['bar','baz','ball'],
}

default_checkignore = """*/site-packages/*
*/dist-packages/*
*/build/*
*/eggs/*
*/migrations/*
*/alembic/versions/*
"""

import importlib
import logging

logger = logging.getLogger(__name__)

def load_plugin(module,name = None):
    logger.debug("Loading plugin: %s" % name)
    if hasattr(module,'analyzers'):
        analyzers.update(module.analyzers)
    if hasattr(module,'commands'):
        if name is None:
            raise AttributeError("You must specify a name for your plugin if you defined new commands!")
        commands.update({name : module.commands})
    if hasattr(module,'models'):
        models.update(module.models)
    if hasattr(module,'top_level_commands'):
        commands.update(module.top_level_commands)

def load_plugins(abort_on_error = False,verbose = False):
    for name,module_name in plugins.items():
        try:
            module = importlib.import_module(module_name+'.setup')
            load_plugin(module,name)
        except:
            logger.error("Cannot import plugin %s (module %s)" % (name,module_name))
            if verbose:
                logger.error(traceback.format_exc())
            if abort_on_error:
                raise

def get_issues_data(settings = None):
    issues_data = {}
    if settings is None:
        settings = {}
    for name,analyzer in analyzers.items():
        language_data = issues_data.setdefault(analyzer['language'],{'title' : analyzer['language']})
        if 'issues_data' in analyzer:
            analyzers_data = language_data.setdefault('analyzers',{})
            analyzers_data[name] = {'title' : analyzer['title']}
            if 'issues_data' in analyzer:
                analyzers_data[name]['codes'] = analyzer['issues_data'].copy()
            if 'analyzers' in settings and name in settings['analyzers']:
                analyzer_settings = settings['analyzers'][name]
                if 'disable_all' in analyzers_settings and analyzers_settings['ignore_all']:
                    analyzers_data[name]['codes'] = {}
                    if 'enable' in analyzer_settings:
                        for code in analyzer_settings['enable']:
                            if code in analyzer['issues_data']:
                                analyzers_data[name]['codes'][code] = analyzer['issues_data'][code]
                else:
                    if 'ignore' in analyzer_settings:
                        for code in analyzer_settings['ignore']:
                            if code in analyzers_data[name]['codes']:
                                del analyzers_data[name]['codes'][code]
    return issues_data
