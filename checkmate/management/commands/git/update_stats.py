# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from checkmate.management.commands.base import BaseCommand
from checkmate.settings import analyzers,aggregators
from checkmate.lib.code.environment import CodeEnvironment
from checkmate.lib.stats.helpers import directory_splitter

import sys
import os
import random
import os.path
import json
import pprint
import time
import datetime
import logging
import pprint

from collections import defaultdict

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    options = BaseCommand.options + [
        ]

    def run(self):

        branches = self.backend.filter(self.project.Branch,{'project.pk' : self.project.pk})

        branches_by_name = dict([(branch.name,branch) for branch in branches])

        if 'default_branch' in self.project and self.project.default_branch in branches_by_name:
            master_branch = branches_by_name[self.project.default_branch]
        elif 'origin/master' in branches_by_name:
            master_branch = branches_by_name['origin/master']
        else:
            logger.error("No default branch defined!\n")
            return -1

        stats = {
            'contributors' : self.project.repository.get_contributors(),
            'branch' : master_branch.name
        }

        stats['n_commits'] = sum([contributor['n_commits'] for contributor in stats['contributors']])

        snapshots = self.backend.filter(self.project.GitSnapshot,{'sha' : {'$in' : master_branch.snapshots}}).sort('committer_date_ts',-1)

        logger.info("Found %d snapshots" % len(snapshots))


        if snapshots:
            latest_snapshot = snapshots[0]
            stats['snapshot'] = latest_snapshot.sha
            if 'summary' in latest_snapshot:
                stats['summary'] = latest_snapshot.summary

            query = {
                'project.pk' : self.project.pk,
                'file_revision.pk' : {'$in' : latest_snapshot['file_revisions']},
                }

            issues = list(self.backend.filter(self.project.Issue,query))

            environment = CodeEnvironment([],analyzers,aggregators = [
                {'mapper' : 
                    lambda f: directory_splitter(f['path'],
                        include_filename = False)
                }])

            group_by = ["language","analyzer","code"]
            issues_summary = environment.summarize_issues(issues,group_by = group_by)
            stats['issues_summary'] = issues_summary

        logger.info("Updating statistics...")

        self.project.stats = stats  
        self.backend.save(self.project)
        self.backend.commit()
