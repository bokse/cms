#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2014 Fabian Gundlach <320pointsguy@gmail.com>
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

"""Print-job-related database interface for SQLAlchemy.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Unicode, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from . import Base, Participation, FilenameConstraint, DigestConstraint


class PrintJob(Base):
    """Class to store a print job.

    """
    __tablename__ = 'printjobs'

    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    # Participation (id and object) that did the submission.
    participation_id = Column(
        Integer,
        ForeignKey(Participation.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True)
    participation = relationship(
        Participation,
        back_populates="printjobs")

    # Submission time of the print job.
    timestamp = Column(
        DateTime,
        nullable=False)

    # Filename and digest of the submitted file.
    filename = Column(
        Unicode,
        FilenameConstraint("filename"),
        nullable=False)
    digest = Column(
        String,
        DigestConstraint("digest"),
        nullable=False)

    done = Column(
        Boolean,
        nullable=False,
        default=False)

    status = Column(
        ARRAY(String),
        nullable=False,
        default=[])
