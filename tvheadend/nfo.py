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
nfo module for tvh application
"""

import time
from tvheadend.errors import errorRaise


def makeNfoString(nfodict, maintag="episodedetails"):
    snfo = content = ""
    try:
        xmlargs = {"attrs": None, "oneline": True, "newline": True}
        for tag in nfodict:
            content += makeXmlTag(tag, nfodict[tag], **xmlargs)
        xmlargs["oneline"] = False
        snfo = makeXmlTag(maintag, content, **xmlargs)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return snfo


def makeFilmNfo(show):
    fnfo = ""
    try:
        mtags = nfoTags(show)
        mtags["premiered"] = show["year"]
        mtags["year"] = show["year"]
        fnfo = makeNfoString(mtags, "movie")
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return fnfo


def makeProgNfo(show):
    pnfo = ""
    try:
        ptags = nfoTags(show)
        if "subtitle" in show and show["subtitle"] is not None and len(show["subtitle"]) > 0:
            ptags["showtitle"] = show["subtitle"]
        if "series" in show and show["series"] is not None:
            ptags["series"] = show["series"]
        pnfo = makeNfoString(ptags)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return pnfo


def nfoTags(show):
    tags = None
    try:
        tags = {
                "title": show["title"],
                "plot": show["disp_description"],
                "startsecs": str(show["start_real"]),
                "stopsecs": str(show["stop_real"]),
                "start": timestampDisplay(show["start_real"]),
                "stop": timestampDisplay(show["stop_real"]),
                "durationsecs": str(show["duration"]),
                "duration": hmsDisplay(show["duration"]),
                "channel": show["channelname"]
                }
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return tags


def makeXmlAtts(attrs):
    satts = ""
    try:
        for attr in attrs:
            satts += attr + "=" + attrs[attr]
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return satts


def makeXmlTag(tag, content, attrs=None, oneline=False, newline=True):
    xml = filler = ""
    try:
        if not oneline:
            filler = "\n"
        xml = "<" + tag
        if content is None and attrs is not None:
            xml += makeXmlAtts(attrs)
            xml += " />"
        elif content is not None:
            if attrs is not None:
                xml += makeXmlAtts(attrs)
            xml += ">" + filler
            xml += content + filler
            xml += "</" + tag + ">"
        if newline and oneline:
            xml += "\n"
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return xml


def valMod(value, divisor):
    val = rem = 0
    try:
        val = int(value / divisor)
        rem = value % divisor
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return [val, rem]


def hms(seconds):
    hrs = mins = secs = 0
    try:
        hrs, rem = valMod(seconds, 3600)
        mins, secs = valMod(rem, 60)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return [hrs, mins, secs]


def displayWord(value, word):
    ret = ""
    try:
        if value > 0:
            ret = "{} {}".format(value, word)
            if value > 1:
                ret += "s"
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return ret


def hmsDisplay(seconds):
    ret = ""
    try:
        h, m, s = hms(seconds)
        hstr = displayWord(h, "hour")
        mstr = displayWord(m, "minute")
        sstr = displayWord(s, "second")
        ret = ""
        if len(hstr) and len(mstr) and len(sstr):
            ret = "{}, {} and {}".format(hstr, mstr, sstr)
        elif len(hstr) and len(mstr):
            ret = "{} and {}".format(hstr, mstr)
        elif len(hstr) and len(sstr):
            ret = "{}, 0 minutes and {}".format(hstr, sstr)
        elif len(hstr):
            ret = hstr
        elif len(mstr) and len(sstr):
            ret = "{} and {}".format(mstr, sstr)
        elif len(mstr):
            ret = mstr
        else:
            ret = sstr
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return ret


def timestampDisplay(ts):
    ret = ""
    try:
        ret = time.ctime(ts)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return ret
