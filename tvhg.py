#!/usr/bin/env python3
# Copyright (c) 2019, Chris Allison
#
#     This file is part of tvhg.
#
#     tvhg is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tvhg is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tvhg.  If not, see <http://www.gnu.org/licenses/>.

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import tvhg
from tvhg import verstr
import tvhg.tvh as TVH
import tvhg.config as CONF
import tvhg.utils as UT
from tvhg.errors import errorExit

class ChannelImage(Gtk.Image):
    def __init__(self, filename, height=-1, width=-1):
        super().__init__()
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        self.origw = self.pixbuf.get_width()
        self.origh = self.pixbuf.get_height()
        self.cw = self.origw
        self.ch = self.origh

    def redraw(self,width=-1,height=-1):
        xw, xh = self.resize(width, height)
        npixbuf = self.pixbuf.scale_simple(xw, xh, GdkPixbuf.InterpType.BILINEAR)
        self.set_from_pixbuf(npixbuf)

    def resize(self,width=-1,height=-1):
        if width<1 and height<1:
            xw = self.origw
            xh = self.origh
            # print("original size: {} x {}".format(xw,xh))
        elif width<1 and height>1:
            xpc = (height/self.origh)*100
            xh = height
            xw = int((self.origw/100)*xpc)
            # print("resize height: {} x {}".format(xw,xh))
        elif width>1 and height<1:
            xpc = (width/self.origw)*100
            xw = width
            xh = int((self.origh/100)*xpc)
            # print("resize width: {} x {}".format(xw,xh))
        elif width >1 and height>1:
            xh = height
            xw = width
        self.cw = xw
        self.ch = xh
        return [xw, xh]


class ChannelButton(Gtk.Button):
    def __init__(self, channame, channum, height=-1, width=-1):
        super().__init__()
        label = UT.padStr(str(channum), 3) + " " + channame
        self.set_label(label)
        logopath = os.path.dirname(__file__) + "/channellogos"
        filename = logopath + "/" + channame + ".png"
        if not UT.fileExists(filename):
            print("logo not found {}".format(filename))
            self.img = None
        else:
            self.img = ChannelImage(filename, height, width)
            self.img.redraw()
            self.set_image(self.img)
            # self.set_always_show_image(True)

    def redraw(self, width=-1, height=-1):
        if self.img is not None:
            self.img.redraw(width, height)
            # self.set_width(self.img.cw)
            # self.set_height(self.img.ch)


class channelGrid(Gtk.Grid):
    def __init__(self, window):
        super().__init__()
        self.win = window

    def makeGrid(self):
        sents = TVH.channels()
        nchans = len(sents)
        lsize = 80
        ncols = 4
        nrows = int(nchans / ncols)
        if nchans % ncols > 0:
            nrows += 1
        buttons = []
        for chan in sents:
            btn = ChannelButton(chan["name"], chan["number"])
            # label = UT.padStr(str(chan["number"]), 3) + " " + chan["name"]
            # btn.set_label(label)
            btn.connect("clicked", self.win.channelButtonClicked, (chan['uuid'], chan['name']))
            btn.redraw(lsize)
            buttons.append(btn)
        cn = 0
        for ix in range(nrows):
            for iy in range(ncols):
                self.attach(child=buttons[cn], left=iy, top=ix, width=1, height=1)
                cn += 1


class ChannelPrograms(Gtk.Box):
    def __init__(self, window, channame, uuid):
        super().__init__()
        self.win = window
        self.channel = channame
        self.uuid = uuid

    def channelData(self):
        progs = TVH.channelPrograms(self.uuid)
        store = Gtk.ListStore(str, str, str, str)
        curday = progs[0]["starts"][1]
        treeiter = store.append([curday, "", "", ""])
        for prog in progs:
            if prog["starts"][1] != curday:
                curday = prog["starts"][1]
                treeiter = store.append([curday, "", "", ""])
            treeiter = store.append([prog["starts"][3] + " - " + prog["stops"][3], prog["durs"], prog["title"], prog["description"]])
        tree = Gtk.TreeView(model=store)
        for i, coltitle in enumerate(["Time", "Dur", "Title", "Description"]):
            rend = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(coltitle, rend, text=i)
            tree.append_column(col)
        self.add(tree)


    def makePage(self):
        btn = Gtk.Button(label="All Channels")
        btn.connect("clicked", self.win.programButtonClicked)
        self.add(btn)
        self.channelData()


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="TV Guide")
        self.set_default_size(800, 600)
        self.set_border_width(10)
        self.page = None

    def setTitle(self, title):
        self.set_title(title + " " + verstr)

    def destroyPage(self):
        self.page.destroy()
        self.page = None

    def channelButtonClicked(self, button, chan):
        uuid, channel = chan
        print("Button {} clicked".format(channel))
        self.destroyPage()
        self.channelProgsPage(*chan)

    def programButtonClicked(self, button):
        print("All Channels button clicked")
        self.destroyPage()
        self.allChannelsPage()

    def allChannelsPage(self):
        if self.page is None:
            self.page = channelGrid(self)
            self.page.makeGrid()
            self.setTitle("All Channels")
            self.add(self.page)
            self.show_all()
        else:
            print("self.page is not yet empty, allChannelsPage")
            self.destroy()

    def channelProgsPage(self, uuid, channel):
        print("request progs for {}".format(channel))
        if self.page is None:
            self.page = ChannelPrograms(self, channel, uuid)
            self.page.makePage()
            self.setTitle(channel + " Programs")
            self.add(self.page)
            self.show_all()
        else:
            print("self.page is not yet empty, channelProgsPage")
            self.destroy()



def main():
    config = CONF.readConfig()
    tvhg.user = config["user"]
    tvhg.passw = config["pass"]
    tvhg.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    # win.setTitle("TV Guide")
    # sents = TVH.channels()
    # lsize = 80
    # ncols = 4
    # nchans = len(sents)
    # print(str(nchans) + " channels active")
    # nrows = int(nchans / ncols)
    # if nchans % ncols > 0:
    #     nrows += 1
    # buttons = []
    # for chan in sents:
    #     btn = ChannelButton(chan["name"], chan["number"])
    #     label = UT.padStr(str(chan["number"]), 3) + " " + chan["name"]
    #     btn.set_label(label)
    #     btn.connect("clicked", win.channelButtonClicked, chan["name"])
    #     btn.redraw(lsize)
    #     buttons.append(btn)
    # grid = Gtk.Grid()
    # cn = 0
    # for ix in range(nrows):
    #     for iy in range(ncols):
    #         grid.attach(child=buttons[cn], left=iy, top=ix, width=1, height=1)
    #         cn += 1

    # bbc4 = ChannelButton("BBC Four HD", 106)
    # bbc4.set_label("BBC Four HD")
    # bbc4.redraw(80)
    # grid.attach(child=bbc4, left=0, top=0, width=1, height=1)
    # bbc4.show()
    # grid = channelGrid()
    # grid.makeGrid()
    # win.add(grid)
    win.allChannelsPage()
    # win.show_all()
    Gtk.main()

if __name__=="__main__":
    main()
