#!/usr/bin/env python3
#
# Copyright (c) 2018, Christopher Allison
#
#     This file is part of tvh.
#
#     tvh is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tvh is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tvh.  If not, see <http://www.gnu.org/licenses/>.
"""
Standalone tvheadend channel lister for tvh application
"""

import sys
import time
from operator import attrgetter, itemgetter
import tvheadend
import tvheadend.tvh as TVH
import tvheadend.config as CONF
import tvheadend.utils as UT
from tvheadend.errors import errorExit


class TvhInputError(Exception):
    pass


def tvhc():
    """
    decide whether we want to show a single channels programs for the next 24 hours
    or
    the channel grid
    params:
        channel name - will detect if it has spaces in it's name
        or
        start - number of hours relative to now()
        length - number of hours to show programs for - optional
    """
    try:
        starth = 0
        length = 2
        channel = None
        cn = len(sys.argv)
        if cn > 2:
            # could be a channel name with spaces or a start and length parameter
            if sys.argv[1].isnumeric():
                starth = int(sys.argv[1])
                length = int(sys.argv[2])
            else:
                channel = " ".join(sys.argv[1:])
        elif cn == 2:
            if sys.argv[1].isnumeric():
                starth = int(sys.argv[1])
            else:
                channel = sys.argv[1]
        if channel is not None:
            tvhChannels(channel)
        else:
            start = int(time.time()) + (3600 * starth)
            tvhPrograms(start, length)
    except:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def tvhChannels(channel="BBC ONE HD"):
    try:
        print("tvheadend enabled channel lister " + tvheadend.__version__)
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        sents = TVH.channels()
        for chan in sents:
            print(UT.padStr(str(chan["number"]), 3), chan["name"])
        TVH.channelPrograms(channel)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def tvhPrograms(start=0, length=2):
    try:
        print("tvheadend enabled channel lister " + tvheadend.__version__)
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        TVH.timeSlotPrograms(start, length)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)
