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
tvheadend module for tvh application
"""
import sys
import requests
import json
import time
import tvheadend
import json
from operator import attrgetter, itemgetter
import tvheadend.utils as UT
from tvheadend.errors import errorNotify

class TVHError(Exception):
    pass


def sendToTVH(route,  data=None):
    """
    send a request to tvheadend
    """
    try:
        # auth = (xuser, xpass)
        auth = (tvheadend.user, tvheadend.passw)
        url = "http://" + tvheadend.ipaddr + "/api/" + route
        r = requests.post(url, data=data, auth=auth)
        # r = requests.get(url, auth=auth)
        if r.status_code is not 200:
            raise TVHError("error from tvh: {}".format(r))
        return r.json()
    except json.decoder.JSONDecodeError as je:
        # output needs cleaning up
        # tvh sometimes has character 25 in place of an apostrophe
        txt = r.text.replace(chr(25), " ")
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, je)
        return json.loads(txt)
    except Exception as e:
        print("{}".format(e))
        print("text: {}".format(r.text))
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)


def finishedRecordings():
    """
    grid_finished returns a dict
    """
    entries = None
    total = 0
    try:
        data = {"limit": 100}
        j = sendToTVH("dvr/entry/grid_finished", data)
        if "entries" in j:
            entries = j["entries"]
        if "total" in j:
            total = int(j["total"])
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)
    finally:
        return (total, entries)

def deleteRecording(uuid):
    try:
        data = {"uuid": uuid}
        sendToTVH("dvr/entry/remove", data)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)


def channels():
    """
    return a sorted list of enabled channels
    """
    try:
        sents = None
        data = {"limit": 200}
        j = sendToTVH("channel/grid", data)
        if "entries" in j:
            sents = sorted(j["entries"], key=itemgetter("number"), reverse=False)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)
    finally:
        return sents


def channelPrograms(channel="BBC Four HD"):
    """
    return a time sorted dict of programs for the named channel

    each event looks like:
    {
      'eventId': 5050806,
      'episodeId': 5050807,
      'serieslinkId': 91157,
      'serieslinkUri': 'ddprogid:///usr/bin/tv_grab_zz_sdjson/SH000191120000',
      'channelName': 'BBC Four HD',
      'channelUuid': '2f6501b00ef0982c8fc3aa67b0229ecc',
      'channelNumber': '106',
      'channelIcon': 'https://s3.amazonaws.com/schedulesdirect/assets/stationLogos/s83282_h3_aa.png',
      'start': 1567936800,
      'stop': 1567965480,
      'title': 'SIGN OFF',
      'description': 'Sign off.',
      'summary': 'Sign off.', # optional
      'nextEventId': 5050808,
    }
    """
    try:
        # chans = channels()
        now = int(time.time())
        # xfilter = [ { "field": "name", "type": "string", "value": channel, "comparison": "eq", } ]
        xfilter = [{"field": "stop", "type": "numeric", "value": str(now), "comparison": "gt"},
                {"field": "start", "type": "numeric", "value": str(now + (3600 * 24)), "comparison": "lt"}]
        # if chans is not None:
            # for chan in chans:
                # if chan["name"] == channel:
        # data = {"filter": xfilter}
        data = {"limit": "999"}
        j = sendToTVH("epg/events/grid", data)
        print(str(j["totalCount"]) + " programs")
        mindur, minprog = UT.displayProgramList(j["entries"], 24, channel)
        print("min duration: {}".format(mindur))
        print("{}".format(minprog))
        # break
        # else:
            # print("chans is none")
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)


def timeSlotPrograms(start=0, length=2):
    try:
        now = int(time.time())
        if start == 0:
            start = int(time.time())
        xfilter = [{"field": "stop", "type": "numeric", "value": str(now), "comparison": "gt"},
                {"field": "start", "type": "numeric", "value": str(now + (3600 * length)), "comparison": "lt"}]
        data = {"filter": xfilter}
        data = {"limit": "999"}
        j = sendToTVH("epg/events/grid", data)
        if "entries" in j:
            mindur, minprog = UT.displayProgramList(j["entries"], length)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)
