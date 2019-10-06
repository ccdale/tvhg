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
errors module for tvh application
"""
import sys


def formatErrorMsg(funcname, exc):
    return "Error in {}: Exception: {}: {}\n".format(funcname, type(exc).__name__, exc)


def errorExit(funcname, exc, errorvalue=1):
    sys.stderr.write(formatErrorMsg(funcname, exc))
    sys.exit(errorvalue)


def errorRaise(funcname, exc):
    sys.stderr.write(formatErrorMsg(funcname, exc))
    raise(exc)


def errorNotify(funcname, exc):
    sys.stderr.write(formatErrorMsg(funcname, exc))
