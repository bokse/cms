#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2013 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2015 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
# Copyright © 2012-2014 Luca Wehrstedt <luca.wehrstedt@gmail.com>
# Copyright © 2014 Artem Iglikov <artem.iglikov@gmail.com>
# Copyright © 2014 Fabian Gundlach <320pointsguy@gmail.com>
# Copyright © 2015 William Di Luigi <williamdiluigi@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Ranking-related handlers for AWS for a specific contest.

"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import csv
import io
import sys

from sqlalchemy.orm import joinedload

from cms.db import Contest
from cms.grading import task_score

from .base import BaseHandler, require_permission


class RankingHandler(BaseHandler):
    """Shows the ranking for a contest.

    """
    @require_permission(BaseHandler.AUTHENTICATED)
    def get(self, contest_id, format="online"):
        # This validates the contest id.
        self.safe_get_item(Contest, contest_id)

        # This massive joined load gets all the information which we will need
        # to generating the rankings.
        self.contest = self.sql_session.query(Contest)\
            .filter(Contest.id == contest_id)\
            .options(joinedload('participations'))\
            .options(joinedload('participations.submissions'))\
            .options(joinedload('participations.submissions.token'))\
            .options(joinedload('participations.submissions.results'))\
            .first()

        self.r_params = self.render_params()
        show_teams = any(map(lambda participation: participation.team_id,
                             self.contest.participations))
        self.r_params["show_teams"] = show_teams
        if format == "txt":
            self.set_header("Content-Type", "text/plain")
            self.set_header("Content-Disposition",
                            "attachment; filename=\"ranking.txt\"")
            self.render("ranking.txt", **self.r_params)
        elif format == "csv":
            self.set_header("Content-Type", "text/csv")
            self.set_header("Content-Disposition",
                            "attachment; filename=\"ranking.csv\"")

            if sys.version_info >= (3, 0):
                output = io.StringIO()  # untested
            else:
                # In python2 we must use this because its csv module does not
                # support unicode input
                output = io.BytesIO()
            writer = csv.writer(output)

            include_partial = True

            contest = self.r_params["contest"]

            row = ["Username", "User"]
            if show_teams:
                row.append("Team")
            for task in contest.tasks:
                row.append(task.name)
                if include_partial:
                    row.append("P")

            row.append("Global")
            if include_partial:
                row.append("P")
            row.append("Number of submissions")
            row.append("Last submission time")

            writer.writerow(row)

            for p in sorted(contest.participations,
                            key=lambda p: p.user.username):
                if p.hidden:
                    continue

                score = 0.0
                partial = False

                row = [p.user.username,
                       "%s (%s)" % (p.user.first_name, p.user.last_name)]  # JOGYO: to match with the form "name (school name)", not sure
                if show_teams:
                    row.append(p.team.name if p.team else "")

                last_submission_timestamps = []

                for task in contest.tasks:
                    t_score, t_partial = task_score(p, task)
                    t_score = round(t_score, task.score_precision)
                    score += t_score
                    partial = partial or t_partial
                    if t_score > 0:
                        last_submission_timestamps.append(min(map(lambda s: s.timestamp, filter(lambda s: s.task_id == task.id and s.get_result().score == t_score, p.submissions))))
                    row.append(t_score)
                    if include_partial:
                        row.append("*" if t_partial else "")

                row.append(round(score, contest.score_precision))
                if include_partial:
                    row.append("*" if partial else "")

                row.append("%d" % len(p.submissions))
                # JOGYO: last column equals to the number of submissions
                # JOGYO-TODO: how to only count the number of official submissions?

                row.append("%s" % (max(last_submission_timestamps) if len(last_submission_timestamps) > 0 else "-"))

                if sys.version_info >= (3, 0):
                    writer.writerow(row)  # untested
                else:
                    writer.writerow([unicode(s).encode("utf-8") for s in row])

            self.finish(output.getvalue())
        else:
            self.render("ranking.html", **self.r_params)
