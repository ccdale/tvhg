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
from tvhg import verstr
import tvheadend
import tvheadend.tvh as TVH
import tvheadend.config as CONF
import tvheadend.utils as UT
from tvheadend.errors import errorExit

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


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="unset")
        self.set_default_size(800, 600)

    def setTitle(self, title):
        self.set_title(title + " " + verstr)


def main():
    config = CONF.readConfig()
    tvheadend.user = config["user"]
    tvheadend.passw = config["pass"]
    tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.setTitle("TV Guide")
    sents = TVH.channels()
    lsize = 80
    ncols = 4
    nchans = len(sents)
    print(str(nchans) + " channels active")
    nrows = int(nchans / ncols)
    if nchans % ncols > 0:
        nrows += 1
    buttons = []
    for chan in sents:
        btn = ChannelButton(chan["name"], chan["number"])
        label = UT.padStr(str(chan["number"]), 3) + " " + chan["name"]
        btn.set_label(label)
        btn.redraw(lsize)
        buttons.append(btn)
    grid = Gtk.Grid()
    cn = 0
    for ix in range(nrows):
        for iy in range(ncols):
            grid.attach(child=buttons[cn], left=iy, top=ix, width=1, height=1)
            cn += 1

    # bbc4 = ChannelButton("BBC Four HD", 106)
    # bbc4.set_label("BBC Four HD")
    # bbc4.redraw(80)
    # grid.attach(child=bbc4, left=0, top=0, width=1, height=1)
    # bbc4.show()
    win.add(grid)
    win.show_all()
    Gtk.main()

if __name__=="__main__":
    main()
