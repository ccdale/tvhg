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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="unset")

    def setTitle(self, title):
        self.set_title(title)


def main():
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.setTitle("TV Guide")
    win.show_all()
    Gtk.main()

if __name__=="__main__":
    main()
