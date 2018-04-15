#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2015 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2018 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
# Copyright © 2013 Bernard Blackham <bernard@largestprime.net>
# Copyright © 2013-2014 Luca Wehrstedt <luca.wehrstedt@gmail.com>
# Copyright © 2014 Fabian Gundlach <320pointsguy@gmail.com>
# Copyright © 2016 Myungwoo Chun <mc.tamaki@gmail.com>
# Copyright © 2016 Amir Keivan Mohtashami <akmohtashami97@gmail.com>
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

"""High level functions to perform standardized white-diff comparison."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa

import logging

from .evaluation import EVALUATION_MESSAGES


logger = logging.getLogger(__name__)


# We take as definition of whitespaces the intersection between ASCII
# and Unicode White_Space characters (see
# http://www.unicode.org/Public/6.3.0/ucd/PropList.txt)
_WHITES = [b' ', b'\t', b'\n', b'\x0b', b'\x0c', b'\r']


def _white_diff_canonicalize(string):
    """Convert the input string to a canonical form for the white diff
    algorithm; that is, the strings a and b are mapped to the same
    string by _white_diff_canonicalize() if and only if they have to be
    considered equivalent for the purposes of the white-diff
    algorithm.

    More specifically, this function strips all the leading and
    trailing whitespaces from s and collapse all the runs of
    consecutive whitespaces into just one copy of one specific
    whitespace.

    string (string): the string to canonicalize.
    return (string): the canonicalized string.

    """
    # Replace all the whitespaces with copies of " ", making the rest
    # of the algorithm simpler
    for char in _WHITES[1:]:
        string = string.replace(char, _WHITES[0])

    # Split the string according to " ", filter out empty tokens and
    # join again the string using just one copy of the first
    # whitespace; this way, runs of more than one whitespaces are
    # collapsed into just one copy.
    string = _WHITES[0].join([x for x in string.split(_WHITES[0])
                              if len(x) > 0])
    return string


def _white_diff(output, res):
    """Compare the two output files. Two files are equal if for every
    integer i, line i of first file is equal to line i of second
    file. Two lines are equal if they differ only by number or type of
    whitespaces.

    Note that trailing lines composed only of whitespaces don't change
    the 'equality' of the two files. Note also that by line we mean
    'sequence of characters ending with \n or EOF and beginning right
    after BOF or \n'. In particular, every line has *at most* one \n.

    output (file): the first file to compare.
    res (file): the second file to compare.
    return (bool): True if the two file are equal as explained above.

    """

    while True:
        lout = output.readline()
        lres = res.readline()

        # Both files finished: comparison succeded
        if len(lres) == 0 and len(lout) == 0:
            return True

        # Only one file finished: ok if the other contains only blanks
        elif len(lres) == 0 or len(lout) == 0:
            lout = lout.strip(b''.join(_WHITES))
            lres = lres.strip(b''.join(_WHITES))
            if len(lout) > 0 or len(lres) > 0:
                return False

        # Both file still have lines to go: ok if they agree except
        # for the number of whitespaces
        else:
            lout = _white_diff_canonicalize(lout)
            lres = _white_diff_canonicalize(lres)
            if lout != lres:
                return False


def white_diff_step(sandbox, output_filename,
                    correct_output_filename):
    """Assess the correctedness of a solution by doing a simple white
    diff against the reference solution. It gives an outcome 1.0 if
    the output and the reference output are identical (or differ just
    by white spaces) and 0.0 if they don't (or if the output doesn't
    exist).

    sandbox (Sandbox): the sandbox we consider.
    output_filename (string): the filename of user's output in the
        sandbox.
    correct_output_filename (string): the same with reference output.

    return ((float, [unicode])): the outcome as above and a
        description text.

    """
    if sandbox.file_exists(output_filename):
        out_file = sandbox.get_file(output_filename)
        res_file = sandbox.get_file(correct_output_filename)
        if _white_diff(out_file, res_file):
            outcome = 1.0
            text = [EVALUATION_MESSAGES.get("success").message]
        else:
            outcome = 0.0
            text = [EVALUATION_MESSAGES.get("wrong").message]
    else:
        outcome = 0.0
        text = [EVALUATION_MESSAGES.get("nooutput").message, output_filename]
    return outcome, text
