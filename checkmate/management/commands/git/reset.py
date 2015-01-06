# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import os
import os.path
import json
import time

from checkmate.management.commands.reset import Command as ResetCommand

class Command(ResetCommand):

    def get_snapshots(self):
        snapshots = self.backend.filter(self.project.GitSnapshot,{'project.pk' : self.project.pk})
        return snapshots

    def get_file_revisions(self,snapshots):
        file_revisions = self.backend.filter(self.project.GitSnapshot.FileRevision,{'project.pk' : self.project.pk})
        return file_revisions
