# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from checkmate.management.commands.base import BaseCommand
from checkmate.lib.models import GitSnapshot
from checkmate.lib.code import CodeEnvironment

import sys
import os
import random
import os.path
import json
import time
import pprint


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

        if len(self.raw_args) < 2:
            sys.stderr.write("Usage: checkmate git diff [snapshot-pk-1] [snapshot-pk-2]\n")
            return -1

        snapshot_a_pk,snapshot_b_pk = self.raw_args[:2]

        try:
            snapshot_a = self.backend.get(GitSnapshot,{'pk' : snapshot_a_pk})
        except GitSnapshot.DoesNotExist:
            sys.stderr.write("Snapshot does not exist: %s\n" % snapshot_a_pk)
            return -1

        try:
            snapshot_b = self.backend.get(GitSnapshot,{'pk' : snapshot_b_pk})
        except GitSnapshot.DoesNotExist:
            sys.stderr.write("Snapshot does not exist: %s\n" % snapshot_b_pk)
            return -1

        code_environment = CodeEnvironment([],{},{})

        diff = code_environment.diff_snapshots(snapshot_a,snapshot_b)

        for key,values in diff.issues.items():
            if not values:
                continue
            print key
            for value in values:
                print value.analyzer,value.description
