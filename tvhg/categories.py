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
categories module for tvh application
"""
import sys
import subprocess
from urllib import parse
from tvheadend.errors import errorRaise
import tvheadend.utils as UT


def findCategoryForTitle(title, config):
    category = xyear = None
    try:
        for cat in config["categories"]:
            for catname in cat:
                for xtitle in cat[catname]:
                    if xtitle == title:
                        category = catname
                        break
                if category is not None:
                    break
            if category is not None:
                break
        if category is None:
            if "Year" in config and config["Year"] is not None:
                for year in config["Year"]:
                    for yearname in year:
                        for xtitle in year[yearname]:
                            if xtitle == title:
                                xyear = yearname
                                break
                        if xyear is not None:
                            break
                    if xyear is not None:
                        break
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return (category, xyear)


def setCategories(entries, config):
    shows = []
    uncatshows = []
    ignores = []
    try:
        for entry in entries:
            if "disp_title" in entry:
                cat, year = findCategoryForTitle(entry["disp_title"], config)
                if cat is not None and cat != "ignore":
                    entry["category"] = cat
                    shows.append(entry)
                elif cat == "ignore":
                    ignores.append(entry)
                elif year is not None:
                    entry["year"] = year
                    shows.append(entry)
                else:
                    uncatshows.append(entry)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        xshows = {"shows": shows, "uncatshows": uncatshows, "ignores": ignores}
        return xshows


def decideCategory(response):
    try:
        year = cat = None
        r = response.lower()
        if r == "i":
            cat = "ignore"
        elif r == "c":
            cat = "comedy"
        elif r == "o":
            cat = "documentary"
        elif r == "d":
            cat = "Drama"
        elif r == "m":
            cat = "music"
        elif r == "s":
            cat = "Sci Fi"
        elif r == "g":
            pass
        elif int(r) > 0:
            year = int(r)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return cat, year


def addToCategory(title, category, config):
    try:
        changed = False
        cats = config["categories"]
        for cat in cats:
            for catname in cat:
                if catname == category:
                    # this works as cat and catname are references not copies
                    cat[catname].append(title)
                    changed = True
                    break
            if changed:
                break
        if not changed:
            xcat = {category: [title]}
            config["categories"].append(xcat)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def addToYear(title, year, config):
    try:
        changed = False
        syear = str(year)
        if "Year" not in config:
            config["Year"] = []
        years = config["Year"]
        if years is not None:
            for xyear in years:
                for yearname in xyear:
                    if yearname == syear:
                        xyear[yearname].append(title)
                        changed = True
                        break
                if changed:
                    break
        if not changed:
            xyear = {syear: [title]}
            if config["Year"] is None:
                config["Year"] = []
            config["Year"].append(xyear)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def movieSearch(title):
    try:
        q = {"q": title + " movie"}
        enc = parse.urlencode(q)
        url = "https://www.google.com/search?" + enc
        cmd = "xdg-open"
        subprocess.Popen([cmd, url])
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def setCategory(snum, shows, config):
    try:
        sn = UT.padStr(str(snum))
        msg = sn + ". " + UT.titleAndSubTitle(shows["uncatshows"][snum - 1])
        print(msg)
        msg = "(I)gnore, (C)omedy, d(O)cumentary, (D)rama, (M)usic, (S)ci Fi, (G)oogle Search or [YYYY]"
        resp = UT.askMe(msg, "D")
        cat, year = decideCategory(resp)
        if cat is None and year is None:
            movieSearch(shows["uncatshows"][snum - 1]["disp_title"])
        if cat is not None and cat == "ignore":
            ent = shows["uncatshows"].pop(snum - 1)
            shows["ignores"].append(ent)
            addToCategory(ent["disp_title"], "ignore", config)
            print("ignoring {}\n".format(UT.titleAndSubTitle(ent)))
        elif cat is not None:
            ent = shows["uncatshows"].pop(snum - 1)
            ent["category"] = cat
            shows["shows"].append(ent)
            addToCategory(ent["disp_title"], cat, config)
            print("Setting {} to {}\n".format(UT.titleAndSubTitle(ent), cat))
        elif year > 0:
            ent = shows["uncatshows"].pop(snum - 1)
            ent["year"] = str(year)
            shows["shows"].append(ent)
            addToYear(ent["disp_title"], year, config)
            print("Film: {}, Year: {}".format(UT.titleAndSubTitle(ent), year))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return shows
