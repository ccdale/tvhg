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
menu module for tvh application
"""

import sys
import tvheadend
import tvheadend.tvh as TVH
import tvheadend.utils as UT
import tvheadend.config as CONF
import tvheadend.categories as CATS
from tvheadend.errors import errorExit


def tvh():
    try:
        print("tvheadend file utility " + tvheadend.__version__)
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        # ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        # tvhauth = {"ip": ipaddr, "xuser": config["user"], "xpass": config["pass"]}
        tot, ents = TVH.finishedRecordings()
        exit = False
        while not exit:
            shows = CATS.setCategories(ents, config)
            print("\nshows: {}, uncat: {}, ignore: {}\n".format(len(shows["shows"]), len(shows["uncatshows"]), len(shows["ignores"])))
            for ent in shows["shows"]:
                if "category" in ent:
                    cat = ent["category"]
                elif "year" in ent:
                    cat = ent["year"]
                else:
                    cat = None
                print("{}: {}: {}: {}".format(cat, ent["disp_title"], ent["disp_subtitle"], ent["filename"]))
            print("\n")
            if len(shows["uncatshows"]) == 0:
                exit = True
            else:
                exit = UT.mainMenu(shows, config)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)
    finally:
        CONF.writeConfig(config)


if __name__ == '__main__':
    tvh()
