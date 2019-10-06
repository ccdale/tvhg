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
utils module for tvh application
"""
import sys
import os
import re
import time
import requests
from pathlib import Path
from tvheadend.errors import errorRaise
import tvheadend.categories as CATS


class FileDoesNotExist(Exception):
    pass


def askMe(q, default):
    try:
        ret = default
        val = input("{} ({}) > ".format(q, default))
        if len(val) > 0:
            ret = val
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def padStr(xstr, xlen=2, pad=" ", padleft=True):
    try:
        zstr = xstr
        while len(zstr) < xlen:
            if padleft:
                zstr = pad + zstr
            else:
                zstr += pad
        return zstr
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def fileExists(fn):
    try:
        return Path(fn).is_file()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def dirExists(dn):
    try:
        return Path(dn).is_dir()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def dfExists(dfn):
    try:
        ret = Path(dfn).is_file()
        if not ret:
            ret = Path(dfn).is_dir()
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)

def makePath(pn):
    try:
        if not dirExists(pn):
            p = Path(pn)
            ret = False
            p.mkdir(mode=0o755, parents=True, exist_ok=True)
            ret = True
        else:
            ret = True
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def makeFilePath(fn):
    try:
        pfn = os.path.basename(fn)
        ret = makePath(pfn)
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def absPath(fn):
    try:
        return os.path.abspath(os.path.expanduser(fn))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def rename(src, dest):
    try:
        if dfExists(src):
            p = Path(src)
            p.rename(dest)
        else:
            raise(FileDoesNotExist("src file does not exist: {}".format(src)))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def seriesId(show):
    show["series"] = None
    try:
        m = re.match(".*([sS][0-9]{1,2}[eE][0-9]{1,3}).*", show["filename"])
        if m is not None and len(m.groups()) > 0:
            show["series"] = m.groups()[0]
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def showParts(show):
    try:
        show["title"] = show["disp_title"]
        if "disp_subtitle" in show:
            show["subtitle"] = show["disp_subtitle"]
            if show["subtitle"].startswith(" - "):
                show["subtitle"] = show["subtitle"][3:]
        else:
            show["subtitle"] = None
        seriesId(show)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def addBaseFn(show):
    try:
        show["opbase"] = None
        showParts(show)
        if "year" in show and show["year"] is not None:
            bfn = delimitString(show["title"], str(show["year"]), " (")
            bfn += ")"
        else:
            bfn = show["title"]
            # bfn = delimitString(bfn, show["subtitle"])
            bfn = delimitString(bfn, show["series"])
        show["opbase"] = bfn
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def titleAndSubTitle(show):
    msg = None
    try:
        if "opbase" not in show:
            addBaseFn(show)
            print("had to re-evaluate the show")
        msg = show["opbase"]
        # showParts(show)
        # msg = show["title"]
        # if dparts is not None:
        #     if "year" in show:
        #         msg += " (" + show["year"] + ")"
        #     else:
        #         sub = dparts["subtitle"] if dparts["subtitle"] is not None else ""
        #         series = dparts["series"] if dparts["series"] is not None else ""
        #         filler = "" if len(sub) == 0 else " - "
        #         msg += filler + sub
        #         filler = "" if len(series) == 0 else " - "
        #         msg += filler + series
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return msg


def displayNumberedShows(xdict):
    try:
        cn = 1
        for entry in xdict:
            sn = padStr(str(cn))
            msg = sn + ". "
            addBaseFn(entry)
            # dts = titleAndSubTitle(entry)
            if entry["opbase"] is not None:
                msg += entry["opbase"]
                if "subtitle" in entry and len(entry["subtitle"]) > 0:
                    msg += " {}".format(entry["subtitle"])
                print(msg)
            cn += 1
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def mainMenu(shows, config):
    ret = False
    try:
        displayNumberedShows(shows["uncatshows"])
        menu = "Select a programme or (E)xit"
        res = askMe(menu, "1")
        prog = 1
        rlow = res.lower()
        if rlow == "e" or rlow == "x" or rlow == "q":
            ret = True
        elif int(res) > 0:
            prog = int(res)
            CATS.setCategory(prog, shows, config)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return ret

def delimitString(xstr, addstr, delimeter=" - "):
    ret = xstr
    try:
        if addstr is not None:
            if len(addstr) > 0:
                ret += delimeter + addstr
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return ret

def reduceTime(unit, secs):
    rem = units = 0
    if unit > 0:
        units = int(secs / unit)
        rem = int(secs % unit)
    else:
        raise ValueError("divide by zero requested in reduceTime: unit: {}, secs: {}".format(unit, secs))
    return (units, rem)


def displayValue(val, label, zero=True):
    if zero and val == 0:
        return ""
    dlabel = label if val == 1 else label + "s"
    return str(val) + " " + dlabel


def hms(secs):
    # print("hms: input: {} seconds".format(secs))
    days = hours = minutes = seconds = 0
    oneday = 86400
    onehour = 3600
    oneminute = 60
    days, rem = reduceTime(oneday, secs)
    # print("days: {} rem: {}".format(days, rem))
    hours, rem = reduceTime(onehour, rem)
    # print("hours: {} rem {}".format(hours, rem))
    minutes, seconds = reduceTime(oneminute, rem)
    # print("minutes: {} seconds: {}".format(minutes, seconds))
    msg = ""
    msg = displayValue(days, "day")
    msg = addToStr(msg, displayValue(hours, "hour"))
    msg = addToStr(msg, displayValue(minutes, "min"))
    msg = addToStr(msg, displayValue(seconds, "sec"))
    # print("hms output: {}".format(msg))
    return msg


def addToStr(xstr, addstr, delimiter=" "):
    ostr = xstr + delimiter + addstr if len(xstr) else addstr
    return ostr


def progStartAndDur(start, stop):
    dispstart = time.strftime("%H:%M", time.localtime(int(start)))
    dmsg = hms(int(stop) - int(start))
    return padStr(dispstart + " " + dmsg, 22, padleft=False)


def displayProgramList(plist, hours=4, singlechannel=None):
    print("singlechannel is {}".format(singlechannel))
    mindur = 3600
    minprog = None
    now = int(time.time())
    xlhours = hours * 3600
    twentyfour = 3600 * 24
    lhours = now + xlhours if singlechannel is None else now + twentyfour
    print("lhours is {}".format((lhours - now)/3600))
    chanproglist = {}
    # sort by channel
    for prog in plist:
        if prog["start"] < lhours:
            dur = prog["stop"] - prog["start"]
            if dur < mindur:
                mindur = dur
                minprog = prog
            if prog["channelName"] in chanproglist:
                chanproglist[prog["channelName"]].append(prog)
            else:
                chanproglist[prog["channelName"]] = [prog]
    cn = 0
    if singlechannel is not None and singlechannel in chanproglist:
        print(singlechannel, "next 24 hours")
        for prog in chanproglist[singlechannel]:
            cn += 1
            sstart = progStartAndDur(prog["start"], prog["stop"])
            print(progStartAndDur(prog["start"], prog["stop"]), prog["title"])
    else:
        for channel in chanproglist:
            for prog in chanproglist[channel]:
                # if "channelIcon" in prog and len(prog["channelIcon"]) > 0:
                #     channelLogo(prog["channelName"], prog["channelIcon"])
                cn += 1
                sstart = progStartAndDur(prog["start"], prog["stop"])
                print(padStr(prog["channelName"], 19, padleft=False), progStartAndDur(prog["start"], prog["stop"]), prog["title"])
    print("{} programs".format(cn))
    return (mindur, minprog)


def channelLogo(channel, url):
    if len(url) > 0:
        imgs = "/home/chris/Pictures"
        imgpath = imgs + "/{}.png".format(channel)
        if not fileExists(imgpath):
            print("Getting logo for {}".format(channel))
            r = requests.get(url)
            if r.status_code == 200:
                print("Logo retrieved ok")
                with open(imgpath, 'wb') as ifn:
                    ifn.write(r.content)
