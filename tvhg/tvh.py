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
tvh module for tvhg application
"""
import sys
import requests
import json
import time
import json
from operator import attrgetter, itemgetter
import tvhg
import tvhg.utils as UT
from tvhg.errors import errorNotify

class TVHError(Exception):
    pass


def sendToTVH(route,  data=None):
    """
    send a request to tvheadend
    """
    try:
        # auth = (xuser, xpass)
        auth = (tvhg.user, tvhg.passw)
        url = "http://" + tvhg.ipaddr + "/api/" + route
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

    each channel looks like:
    {
        'uuid': '7850356b3dfa39eeb499762503854ffc',
        'enabled': True,
        'autoname': False,
        'name': 'Quest HD',
        'number': 114,
        'icon': 'https://s3.amazonaws.com/schedulesdirect/assets/stationLogos/s105894_ll_h3_aa.png',
        'icon_public_url': 'https://s3.amazonaws.com/schedulesdirect/assets/stationLogos/s105894_ll_h3_aa.png',
        'epgauto': True,
        'epggrab': ['77574f7496c8cc15fa46f2f58a493596'],
        'dvr_pre_time': 0,
        'dvr_pst_time': 0,
        'epg_running': 1,
        'services': ['ad21baedd3d343584cd82e4676475891'],
        'tags': ['1b60450bd20f38fb360da33bcff1e558', '4623848c6069fe05581f726488f9dbde'],
        'bouquet': ''
    },
    {
        'uuid': 'd33cebc511185ed33f86fe3301c4074b',
        'enabled': True,
        'autoname': False,
        'name': 'BBC RB 1',
        'number': 601,
        'epgauto': True,
        'epggrab': [],
        'dvr_pre_time': 0,
        'dvr_pst_time': 0,
        'epg_running': 1,
        'services': ['39bfa36f9c217ba13f2cfce96ed8b3f9'], 'tags': ['d2ba279c081822c50e925f345343815e',
        '1b60450bd20f38fb360da33bcff1e558'],
        'bouquet': ''
    }
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


def channelPrograms(uuid):
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

    will have tuples of strings for time added
    prog["starts"] = (21st, Fri, Jan, 13:24)
    prog["stops"] = (21st, Fri, Jan, 15:00)
    prog["durs"] = "1 hr 36 mins"
    """
    try:
        # chans = channels()
        now = int(time.time())
        then = now + (3600 * 24)
        # xfilter = [ { "field": "name", "type": "string", "value": channel, "comparison": "eq", } ]
        xfilter = [{"field": "stop", "type": "numeric", "value": str(now), "comparison": "gt"},
                {"field": "start", "type": "numeric", "value": str(then), "comparison": "lt"}]
        # if chans is not None:
            # for chan in chans:
                # if chan["name"] == channel:
        # data = {"filter": xfilter}
        data = {"limit": "999"}
        data = {"channel": uuid, "filter": xfilter, "limit": "999"}
        j = sendToTVH("epg/events/grid", data)
        print(str(j["totalCount"]) + " programs")
        progs = []
        for prog in j["entries"]:
            if int(prog["stop"]) > now and int(prog["start"]) < then and uuid == prog["channelUuid"]:
                prog["starts"] = UT.makeTimeStrings(prog["start"])
                prog["stops"] = UT.makeTimeStrings(prog["stop"])
                prog["durs"] = UT.hms(int(prog["stop"]) - int(prog["start"]))
                progs.append(prog)
        print("filtered progs {}".format(len(progs)))
        return progs
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
        print(str(j["totalCount"]) + " programs")
        progs = []
        minp = 9999999
        maxp = 0
        cn = 0
        for prog in j["entries"]:
            if int(prog["stop"]) > now and int(prog["start"]) < then:
                cn += 1
                prog["duration"] = int(prog["stop"]) - int(prog["start"])
                if prog["duration"] < minp:
                    minp = prog["duration"]
                if prog["duration"] > maxp:
                    maxp = prog["duration"]
                prog["starts"] = UT.makeTimeStrings(prog["start"])
                prog["stops"] = UT.makeTimeStrings(prog["stop"])
                prog["durs"] = UT.hms(dur)
                if prog["channelUuid"] not in progs:
                    progs[prog["channelUuid"]] = []
                progs[prog["channelUuid"]].append(prog)
        progs["minp"] = minp
        progs["maxp"] = maxp
        print("filtered progs {}".format(cn))
        return progs
        # if "entries" in j:
        #     mindur, minprog = UT.displayProgramList(j["entries"], length)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)
