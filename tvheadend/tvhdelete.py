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
Standalone tvheadend file delete for tvh application
"""

import sys
import os
import shutil
import time
import tvheadend
import tvheadend.tvh as TVH
import tvheadend.utils as UT
import tvheadend.config as CONF
import tvheadend.categories as CATS
import tvheadend.nfo as NFO
from tvheadend.errors import errorExit


class TvhInputError(Exception):
    pass


def tvhdelete():
    try:
        print("tvheadend file deletion " + tvheadend.__version__)
        if len(sys.argv) > 1:
            showfiles = sys.argv[1:]
        else:
            raise(TvhInputError("Please supply a filename"))
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        # ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        # tvhauth = {"ip": ipaddr, "xuser": config["user"], "xpass": config["pass"]}
        tot, ents = TVH.finishedRecordings()
        for show in ents:
            if show["filename"] in showfiles:
                print("Deleting {}".format(show["filename"]))
                TVH.deleteRecording(show["uuid"], **tvhauth)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == '__main__':
    tvhdelete()
