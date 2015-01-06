# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from checkmate.management.commands.base import BaseCommand
from checkmate.lib.models import GitSnapshot

import sys
import os
import random
import os.path
import json
import time

class Command(BaseCommand):

    options = BaseCommand.options + [
        {
        'name'        : '--branch',
        'action'      : 'store',
        'dest'        : 'branch',
        'type'        : str,
        'default'     : 'master',
        'help'        : 'The branch for which to show the log.'
        },
        ]

    def run(self):

        if not self.opts['branch']:
            branch = self.project.repository.get_branches()[0]
        else:
            branch = self.opts['branch']

        snapshots = self.backend.filter(GitSnapshot,{'project' : self.project}).sort('committer_date_ts',-1)
        print len(snapshots)
        for snapshot in snapshots:
            print snapshot.committer_date,"  ",snapshot.pk
