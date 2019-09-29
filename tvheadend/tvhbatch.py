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
batch module for tvh application
"""

import sys
import os
import shutil
import time
import requests
from requests.exceptions import ConnectionError
import tvheadend
import tvheadend.tvh as TVH
import tvheadend.utils as UT
import tvheadend.config as CONF
import tvheadend.categories as CATS
import tvheadend.nfo as NFO
from tvheadend.errors import errorExit


class CopyFailure(Exception):
    pass

def sizeof_fmt(num, suffix='B'):
    """
    from article by Fred Cirera: https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
    and stackoverflow: https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "{:3.1f}{}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:3.1f}{}{}".format(num, "Y", suffix)


def removeFromYear(show, config):
    try:
        if "year" in show:
            if config["Year"] is not None:
                syear = str(show["year"])
                years = config["Year"]
                changed = False
                for xyear in years:
                    for yearname in xyear:
                        if yearname == syear:
                            if show["title"] in xyear[yearname]:
                                xyear[yearname].remove(show["title"])
                                changed = True
                                break
                    if changed:
                        break
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def moveShow(show, config):
    try:
        then = time.time()
        tvhstat = os.stat(show["filename"])
        print("{}: {}".format(show["opbase"], sizeof_fmt(tvhstat.st_size)))
        if "year" in show:
            opdir = "/".join([config["filmhome"], show["title"][0:1].upper(), show["opbase"]])
            snfo = NFO.makeFilmNfo(show)
        else:
            opdir = "/".join([config["videohome"], show["category"], show["title"]])
            snfo = NFO.makeProgNfo(show)
        print("making directory {}".format(opdir))
        UT.makePath(opdir)
        basefn = "/".join([opdir, show["opbase"]])
        opfn = basefn + ".mpg"
        nfofn = basefn + ".nfo"
        print("writing nfo to {}".format(nfofn))
        with open(nfofn, "w") as nfn:
            nfn.write(snfo)
        print("copying {} to {}".format(show["filename"], opfn))
        shutil.copy2(show["filename"], opfn)
        if UT.fileExists(opfn):
            cstat = os.stat(opfn)
            if cstat.st_size == tvhstat.st_size:
                print("copying {} took: {}".format(sizeof_fmt(cstat.st_size), NFO.hmsDisplay(int(time.time() - then))))
                print("show copied to {} OK.".format(opfn))
                print("deleting from tvheadend")
                TVH.deleteRecording(show["uuid"])
                # it is safe to run removeFromYear for all shows
                # as it tests whether this is a movie or not
                removeFromYear(show, config)
                print("\n")
        else:
            raise(CopyFailure("Failed to copy {} to {}".format(show["filename"], opfn)))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def updateKodi():
    try:
        data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan"}
        headers = {"content-type": "application/json"}
        url = "http://127.0.0.1:8080/jsonrpc"
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code < 399:
            print("Kodi update starting")
            print("response: {}".format(resp))
            print("response text: {}".format(resp.text))
        else:
            print("Failed to update Kodi")
            print("response: {}".format(resp))
            print("response text: {}".format(resp.text))
    except ConnectionError as ce:
        print("Kodi isn't running")
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)



def tvhbatch():
    try:
        print("tvheadend batch utility " + tvheadend.__version__)
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        # ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        # tvhauth = {"ip": ipaddr, "xuser": config["user"], "xpass": config["pass"]}
        tot, ents = TVH.finishedRecordings()
        shows = CATS.setCategories(ents, config)
        cn = 0
        for show in shows["shows"]:
            UT.addBaseFn(show)
            moveShow(show, config)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)
    finally:
        CONF.writeConfig(config)
        updateKodi()

if __name__ == '__main__':
    tvhbatch()
