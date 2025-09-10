# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2025 FBXL5                                              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""
This script provides methods to write svg code lines for the creation
of TechDraw templates and symbols.
"""

"""
I have tried to follow this naming rule:
 class names:    CamelCase
 function names: mixedCase
 constant names: ALL_CAPITAL + underscore
 variable names: lower_case + underscore
"""

# imports and constants
import time, os
import FreeCAD
from PySide import QtCore
from PySide.QtGui import QMessageBox

mod_path = os.path.dirname(__file__)
icons_path = os.path.join(mod_path, "Resources", "icons")
symbols_path = os.path.join(mod_path, "Resources", "symbols")

def isGuiLoaded():
    if hasattr(FreeCAD, "GuiUp"):
        return FreeCAD.GuiUp
    return False

# Methods to write svg code:

def levelOfIndentation(indent_level = 0):
    """
    Adds spaces according to the level of indentation
    odd numbers indicate indentation inside a tag,
    even numbers indicate nested tags
    """
    indent_spaces = ""
    if indent_level != 0:
        for value in range(0, indent_level):
            indent_spaces += "  " # adds 2 spaces
    return indent_spaces

def autoFillKey(text_name = ""):
    """
    Returns an auto-fill command for a given text name if possible
    """
    # Autofill key words: "author", "date", "page_number", "page_count", "scale",
    # "sheet", "title", "owner", "organization", "organisation", "company"
    AUTO_DICT = {
		"Author":"author",
        "AuDate":"date",
        "Page":"page_number",
        "Pages":"page_count",
        "Scale":"scale",
        "Sheets":"sheet",
        "Drawing Title":"title",
        "Owner":"owner"
    	}
    auto_fill = ""
    for item in AUTO_DICT:
        if text_name == item:
            auto_fill = "\" freecad:autofill=\"" + AUTO_DICT[item]
            print(auto_fill)
            return auto_fill
    return auto_fill

def svgRect(width, height, x, y):
    """
    Generates an svg-instruction to draw a rectangle with the given values
    """
    svg_line = "<rect width=\"{W}\" height=\"{H}\" x=\"{X}\" y=\"{Y}\" />"
    return svg_line.format(W = width, H = height, X = x, Y = y)

def svgPath(x1, y1, x2, y2):
    """
    Generates an svg-instruction to draw a path element (line)
    with the given values
    """
    if x2 in ["v", "V", "h", "H"]:
		# to draw a horizontal/vertical line
		# either relative or absolute
        svg_line = "<path d=\"m {X},{Y} {C} {D}\" />"
    else:
		# to draw a Line to a second point, only relative
        svg_line = "<path d=\"m {X},{Y} l {C},{D}\" />"
    return svg_line.format(X = x1, Y = y1, C = x2, D = y2)

def svgText(x, y, str_value, str_angle = "0"):
    """
    Generates an svg-instruction to place a text element with the given values.
    Optional str_angle enables vertical and arbitrarily rotated texts
    """
    if str_angle == "0":
        svg_line = "<text x=\"{X}\" y=\"{Y}\">{SV}</text>"
    else:
        svg_line = (
            "<text x=\"{X}\" y=\"{Y}\" transform=\"rotate({SA}," +
            "{X},{Y})\">{SV}</text>"
            )
    return svg_line.format(X = x, Y = y, SV = str_value, SA = str_angle)

def ediText(entry_name, x, y, str_value, str_angle="0"):
    """
    Generates an svg-instruction to place an editable text element
    with the given values and adds an autofill key if applicable.
    Optional str_angle enables vertical and arbitrarily rotated editable texts.
    """
    afk = autoFillKey(entry_name)

    if str_angle == "0":
        svg_line = (
            "<text freecad:editable=\"{EN}{AF}\"" +
            " x=\"{X}\" y=\"{Y}\"> <tspan>{SV}</tspan> </text>"
            )
    else:
        svg_line = (
            "<text freecad:editable=\"{EN}{AF}\"" +
            " x=\"{X}\" y=\"{Y}\" transform=\"rotate({SA}," +
            "{X},{Y})\"> <tspan>{SV}</tspan> </text>"
            )
    return svg_line.format(
        EN = entry_name, AF = afk, X = x, Y = y, SV = str_value, SA = str_angle
        )

def createSvgFile(file_path):
    """
    Creates a file and insert a header line
    (with t as the space saving variant of template)
    """
    t = open(file_path, "w")  # w = write, overwrites existing files
    t.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>")
    t.close

def startSvg(file_path, sheet_width = "20", sheet_height = "16"):
    """
    Creates an svg-tag including namespace and format definitions
    """
    t = open(file_path, "a", encoding="utf-8")
    # a = append, new lines are added at the end of an existing file
    # encoding="utf-8", helps with special characters if
    # the Python interpreter is in ASCII mode
    loi = levelOfIndentation(0)
    t.write(loi + "\n" + "\n")
    t.write(loi + "<svg\n")
    #- Namespace declarations
    loi = levelOfIndentation(1)
    t.write(loi + "xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\"\n")
    t.write(loi + "xmlns:freecad=\"https://wiki.freecad.org/Svg_Namespace\"\n")
    #- Format definition
    t.write(loi + "width =\"" + sheet_width + "mm\"\n")
    t.write(loi + "height=\"" + sheet_height + "mm\"\n")
    t.write(loi + "viewBox=\"0 0 " + sheet_width + " " + sheet_height + "\">\n")
    # identical values for width and height and Viewbox' width and height
    # will synchronise mm and svg-units
    t.close

def endSvg(file_path):
    """
    Creates a closing svg-tag
    """
    t = open(file_path, "a", encoding="utf-8")
    loi = levelOfIndentation(0)
    t.write(loi + "</svg>")
    t.close

# Methods to calculate values:

def sheetDimensions(format):
    """
    Returns width and height acccording to a given format string
    """
    if format.startswith("ANS"):
        if format.endswith("A"):
            width  = "216"
            height = "279"
        elif format.endswith("B"):
            width  = "432"
            height = "279"
        elif format.endswith("C"):
            width  = "559"
            height = "432"
        elif format.endswith("D"):
            width  = "864"
            height = "559"
        else: # E
            width  = "1118"
            height = "864"
    elif format.startswith("Arc"):
        if format.endswith("A"):
            width  = "229"
            height = "305"
        elif format.endswith("B"):
            width  = "457"
            height = "305"
        elif format.endswith("C"):
            width  = "610"
            height = "457"
        elif format.endswith("D"):
            width  = "914"
            height = "610"
        elif format.endswith("E"):
            width  = "1219"
            height = "914"
        else: # E1
            width  = "1067"
            height = "762"
    else: # ISO
        if format.endswith("4-"):
            width  = "297"
            height = "210"
        elif format.endswith("4"):
            width  = "210"
            height = "297"
        elif format.endswith("3"):
            width  = "420"
            height = "297"
        elif format.endswith("2"):
            width  = "594"
            height = "420"
        elif format.endswith("1"):
            width  = "841"
            height = "594"
        else: # A0
            width  = "1189"
            height = "841"
    print(format, width, height)
    return (width, height)

def drawingAreaOffsets(top = 10, bottom = 10, left = 20, right = 10):
    """
    Sets the offset values between drawing area and page edges
    either according to ISO 7200 (default) or by given values
    """
    return(top, bottom, left, right)

def sheetFrameOffsets(top = 5, bottom = 5, left = 5, right = 5):
    """
    Sets the offset values between sheet frame and drawing area
    either according to ISO 7200 (default) or by given values
    """
    return(top, bottom, left, right)

# Methods to generate frame-related geometry:

def createFrame(file_path, sheet_x, sheet_y):
    """
    Creates rectangles for sheet frame and drawing area
	(older version used for the wiki example)
    """
    t = open(file_path, "a", encoding="utf-8")
    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"drawing-frame\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"fill:none;stroke:#000000;stroke-width:0.5;\
stroke-linecap:round\">\n")
    #- set frame offsets
    dOffsets = drawingAreaOffsets()
    dTop    = dOffsets[0]
    dBottom = dOffsets[1]
    dLeft   = dOffsets[2]
    dRight  = dOffsets[3]
    sOffsets = sheetFrameOffsets()
    sTop    = sOffsets[0]
    sBottom = sOffsets[1]
    sLeft   = sOffsets[2]
    sRight  = sOffsets[3]
    #- upper left corner of inner Frame, drawing area
    frame_x = str(dLeft)
    frame_y = str(dTop)
    #- lower right corner (pre-use of dimension variables)
    frame_width = str(int(sheet_x) - dRight)
    frame_height = str(int(sheet_y) - dBottom)
    loi = levelOfIndentation(4)
    t.write(loi + "<!-- Drawing area " + frame_x + " " + frame_y + " "
        + frame_width + " " + frame_height + " -->\n"
        )
    #- frame dimensions
    frame_width = str(int(sheet_x) - dLeft - dRight)
    frame_height = str(int(sheet_y) - dTop - dBottom)
    #- frame rectangle
    t.write(loi + svgRect(frame_width, frame_height, frame_x, frame_y) + "\n")
    #- upper left corner of outer frame, sheet frame
    frame_x = str(dLeft - sLeft)
    frame_y = str(dTop - sTop)
    #- lower right corner
    frame_width = str(int(sheet_x) - dRight + sRight)
    frame_height = str(int(sheet_y) - dBottom + sBottom)
    t.write(loi + "<!-- Sheet frame " + frame_x + " " + frame_y + " "
        +frame_width+" "+frame_height+" -->\n"
        )
    #- frame dimensions
    frame_width = str(int(sheet_x) - dLeft - dRight + sLeft + sRight)
    frame_height = str(int(sheet_y) - dTop - dBottom + sTop + sBottom)
    #- frame rectangle
    t.write(loi + svgRect(frame_width, frame_height, frame_x, frame_y) + "\n")
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close

def createFrames(file_path, sheet_size, da_offsets, if_offsets):
    """
    Creates cutting marks and rectangles for index frame and drawing area
    """
    t = open(file_path, "a", encoding="utf-8")
    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"cutting-marks\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"fill:#000;stroke:none\">\n")
    loi = levelOfIndentation(4)
    sheet_x = sheet_size[0]
    sheet_y = sheet_size[1]
    t.write(loi + "<path d=\"m 0,0 h 10 v 5 h -5 v 5 h -5 z\"/>\n")
    t.write(loi + "<path d=\"m {},0 h -10 v 5 h 5 v 5 h 5 z\"/>\n".format(
        sheet_x
        ))
    t.write(loi +
        "<path d=\"m {},{} h -10 v -5 h 5 v -5 h 5 z\"/>\n".format(
            sheet_x, sheet_y
            ))
    t.write(loi +
        "<path d=\"m 0,{} h 10 v -5 h -5 v -5 h -5 z\"/>\n".format(
            sheet_y
            ))
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")
    t.write(loi + "<g id=\"drawing-area\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"fill:none;stroke:#000;stroke-width:0.7;\
stroke-linecap:square\">\n")
    #- set offsets for drawing area and index frame
    da_top    = da_offsets[0]
    da_bottom = da_offsets[1]
    da_left   = da_offsets[2]
    da_right  = da_offsets[3]
    if_top    = if_offsets[0]
    if_bottom = if_offsets[1]
    if_left   = if_offsets[2]
    if_right  = if_offsets[3]
    #- upper left corner of drawing area
    frame_x = str(da_left)
    frame_y = str(da_top)
    #- lower right corner (pre-use of dimension variables)
    frame_width = str(int(sheet_x) - da_right)
    frame_height = str(int(sheet_y) - da_bottom)
    loi = levelOfIndentation(4)
    t.write(loi + "<!-- Drawing area {} {} {} {} -->\n".format(
        frame_x, frame_y, frame_width, frame_height
        ))
    #- frame dimensions
    frame_width = str(int(sheet_x) - da_left - da_right)
    frame_height = str(int(sheet_y) - da_top - da_bottom)
    #- frame rectangle
    t.write(loi + svgRect(frame_width, frame_height, frame_x, frame_y) + "\n")
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")
    t.write(loi + "<g id=\"index-frame\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"fill:none;stroke:#000;stroke-width:0.25;\
stroke-linecap:square\">\n")
    #- upper left corner of outer frame, sheet frame
    frame_x = str(da_left - if_left)
    frame_y = str(da_top - if_top)
    #- lower right corner
    frame_width = str(int(sheet_x) - da_right + if_right)
    frame_height = str(int(sheet_y) - da_bottom + if_bottom)
    t.write(loi + "<!-- Sheet frame {} {} {} {} -->\n".format(
        frame_x, frame_y, frame_width, frame_height
        ))
    #- frame dimensions
    frame_width = str(int(sheet_x) - da_left - da_right + if_left + if_right)
    frame_height = str(int(sheet_y) - da_top - da_bottom + if_top + if_bottom)
    #- frame rectangle
    t.write(loi + svgRect(frame_width, frame_height, frame_x, frame_y) + "\n")
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close

def createDecoration(file_path, sheet_width, sheet_height, tilt = "0"):
    """
    Creates indices, puncher mark, and folding marks
	(older variant)
    """
    t = open(file_path, "a", encoding="utf-8")
    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"index-separators\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"fill:none;stroke:#000000;stroke-width:0.25;\
stroke-linecap:round\">\n")
    #- set frame offsets
    dOffsets = drawingAreaOffsets()
    dTop    = dOffsets[0]
    dBottom = dOffsets[1]
    dLeft   = dOffsets[2]
    dRight  = dOffsets[3]
    sOffsets = sheetFrameOffsets()
    sTop    = sOffsets[0]
    sBottom = sOffsets[1]
    sLeft   = sOffsets[2]
    sRight  = sOffsets[3]

    frame_width  = str(int(sheet_width) - dLeft - dRight)
    frame_height = str(int(sheet_height) - dTop - dBottom)

    #- starting point values of center lines
    index_center = str(int(frame_width) / 2 + dLeft)
    index_middle = str(int(frame_height) / 2 + dTop)
    index_left   = str(dLeft + 5)
    index_right  = str(int(frame_width) + dLeft - 5)
    index_upper  = str(dTop + 5)
    index_lower  = str(int(frame_height) + dTop - 5)

    #- centre and middle markings of drawing area
    loi = levelOfIndentation(4)
    if sheet_width == "210": # format == "DIN-A4":
        index_left = str(dLeft)
        t.write(loi + svgPath(index_left, index_middle, "h", "-15") + "\n")
    elif sheet_width == "297": # format == "DIN-A4-":
        index_upper = str(dTop)
        t.write(loi + svgPath(index_center, index_upper, "v", "-15") + "\n")
    elif sheet_width == "420": # format == "DIN-A3":
        index_left = str(dLeft+5)
        t.write(loi + svgPath(index_center, index_upper, "v", "-10") + "\n")
        t.write(loi + svgPath(index_center, index_lower, "v", " 10")+  "\n")
        t.write(loi + svgPath(index_left, index_middle, "h", "-20") + "\n")
        t.write(loi + svgPath(index_right, index_middle, "h", " 10") + "\n")
    else :
        t.write(loi + svgPath(index_center, index_upper, "v", "-10") + "\n")
        t.write(loi + svgPath(index_center, index_lower, "v", " 10") + "\n")
        t.write(loi + svgPath(index_left, index_middle, "h", "-10") + "\n")
        t.write(loi + svgPath(index_right, index_middle, "h", " 10") + "\n")

    #- starting point values of separator lines
    index_left  = str(dLeft)
    index_right = str(int(frame_width) + dLeft)
    index_upper = str(dTop)
    index_lower = str(int(frame_height) + dTop)

    #- set number of horizontal and vertical indexes
    # this needs to be extended for American formats
    if sheet_width == "420": # format == "DIN-A3":
        index_count_x = 8
        index_count_y = 6
    elif sheet_width == "594": # format == "DIN-A2":
        index_count_x = 12
        index_count_y = 8
    elif sheet_width == "841": # format == "DIN-A1":
        index_count_x = 16
        index_count_y = 12
    elif sheet_width == "1189": # format == "DIN-A0":
        index_count_x = 24
        index_count_y = 16
    else :
        index_count_x = 0
        index_count_y = 0

    #- index_center and index_middle contain strings but floating point
    #   numbers are needed to calculate
    float_center = int(frame_width) / 2 + dLeft
    float_middle = int(frame_height) / 2 + dTop

    #- horizontal index separators
    max = int(index_count_x / 2 - 1)
    for value in range(0, max):
        index_x = str(float_center + (value + 1) * 50)
        t.write(loi + svgPath(index_x, index_upper, "v", " -5") + "\n")
        t.write(loi + svgPath(index_x, index_lower, "v", "  5") + "\n")
        index_x = str(float_center - (value + 1) * 50)
        t.write(loi + svgPath(index_x, index_upper, "v", " -5") + "\n")
        t.write(loi + svgPath(index_x, index_lower, "v", "  5") + "\n")

    #- vertical index separators
    max = int(index_count_y / 2 - 1)
    for value in range(0, max):
        index_y = str(float_middle + (value + 1) * 50)
        t.write(loi + svgPath(index_left, index_y, "h", " -5") + "\n")
        t.write(loi + svgPath(index_right, index_y, "h", "  5") + "\n")
        index_y = str(float_middle - (value + 1) * 50)
        t.write(loi + svgPath(index_left, index_y, "h", " -5") + "\n")
        t.write(loi + svgPath(index_right, index_y, "h", "  5") + "\n")

    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")

    t.write(loi + "<g id=\"indexes\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"font-size:3.5;text-anchor:middle;fill:#000000;\
font-family:osifont\">\n")

    #- position point values of indexes for upright characters
    index_left = str(dLeft - sLeft / 2)
    index_right = str(int(frame_width) + dLeft + sRight / 2)
    index_upper = str(dTop - 1)
    index_lower = str(int(frame_height) + dTop + sBottom - 1)
    if tilt != "0":
        # Adapted values for upper and right indexes rotated by -90°
        index_right = str(int(frame_width) + dLeft + sRight - 1)
        index_upper = str(dTop - sTop / 2)

    loi = levelOfIndentation(4)
    #- horizontal indexes, numbers
    max = int(index_count_x / 2)
    for value in range(0, max):
        index_x = str(float_center + value * 50 + 25)
        t.write(loi + svgText(index_x, index_upper,
            str(int(index_count_x / 2 + value + 1)), tilt) + "\n"
            )
        t.write(loi + svgText(index_x, index_lower,
            str(int(index_count_x / 2 + value + 1))) + "\n"
            )
        index_x = str(float_center - value * 50 - 25)
        t.write(loi + svgText(index_x, index_upper,
            str(int(index_count_x / 2 - value)), tilt) + "\n"
            )
        t.write(loi + svgText(index_x, index_lower,
            str(int(index_count_x / 2 - value))) + "\n"
            )

    #- vertical indexes, letters
    max = int(index_count_y / 2)
    for value in range(0, max):
        index_y = str(float_middle + value * 50 + 25)
        if int(index_count_y / 2 + value + 1) > 9 :
            # This avoids the letter J
            t.write(loi + svgText(index_left, index_y,
                chr(64 + int(index_count_y / 2 + value + 2))) + "\n"
                )
            t.write(loi + svgText(index_right, index_y,
                chr(64 + int(index_count_y / 2 + value + 2)), tilt) + "\n"
                )
        else :
            t.write(loi + svgText(index_left, index_y,
                chr(64 + int(index_count_y / 2 + value + 1))) + "\n"
                )
            t.write(loi + svgText(index_right, index_y,
                chr(64 + int(index_count_y / 2 + value + 1)), tilt) + "\n"
                )
        # no J expected below
        index_y = str(float_middle - value * 50 - 25)
        t.write(loi + svgText(index_left, index_y,
            chr(64 + int(index_count_y / 2 - value))) + "\n"
            )
        t.write(loi + svgText(index_right, index_y,
            chr(64 + int(index_count_y / 2 - value)), tilt) + "\n"
            )

    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")

    #- puncher mark
    t.write(loi + "<g id=\"puncher mark\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"fill:none;stroke:#b0b0b0;stroke-width:0.25;\
stroke-linecap:miter;stroke-miterlimit:4\">\n")
    loi = levelOfIndentation(4)
    if sheet_width in ["1189", "841", "594"] : # A3 and A4 have extended middle markings
        t.write(
            loi + svgPath(str(dLeft - sLeft),
            str(int(sheet_height) - (297 / 2)), "h", "-10") + "\n"
            )
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")

    #- folding marks
    t.write(loi + "<g id=\"folding marks\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"fill:none;stroke:#b0b0b0;stroke-width:0.25;\
stroke-linecap:miter;stroke-miterlimit:4\">\n")
    loi = levelOfIndentation(4)
    if sheet_width == "420": # DIN-A3
        t.write(loi + svgPath("125", str(dTop - sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("125",
            str(int(sheet_height) - dBottom + sBottom),"v","  5")+"\n"
            )
        t.write(loi + svgPath("230", str(dTop - sTop), "v", "-5") + "\n")
        t.write(loi + svgPath("230",
            str(int(sheet_height) - dBottom + sBottom),"v","  5")+"\n"
            )
    elif sheet_width == "594": # DIN-A2
        t.write(loi + svgPath("210", str(dTop-sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("210",
            str(int(sheet_height) - dBottom+sBottom),"v","  5")+"\n"
            )
        t.write(loi + svgPath("402", str(dTop-sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("402",
            str(int(sheet_height) - dBottom + sBottom),"v","  5")+"\n"
            )
        t.write(loi + svgPath("105", str(dTop-sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("  5", "123", "h", " -5") + "\n")
        t.write(loi + svgPath(
            str(int(sheet_width) - dRight + sRight), "123", "h",
            "  5") + "\n"
            )
    elif sheet_width == "841": # DIN-A1
        t.write(loi + svgPath("210", str(dTop-sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("210",
            str(int(sheet_height) - dBottom + sBottom), "v", "  5") + "\n"
            )
        t.write(loi + svgPath("400", str(dTop-sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("400",
            str(int(sheet_height) - dBottom + sBottom), "v", "  5") + "\n"
            )
        t.write(loi + svgPath("651", str(dTop-sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("651",
            str(int(sheet_height) - dBottom + sBottom), "v", "  5") + "\n"
            )
        t.write(loi + svgPath("105", str(dTop-sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("  5", "297", "h", " -5") + "\n")
        t.write(loi + svgPath(str(int(sheet_width) - dRight + sRight),
            "297", "h", "  5") + "\n"
            )
    elif sheet_width == "1189": # DIN-A0
        t.write(loi + svgPath("210", str(dTop - sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("210",
            str(int(sheet_height) - dBottom + sBottom), "v", "  5") + "\n"
            )
        t.write(loi + svgPath("400", str(dTop - sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("400",
            str(int(sheet_height) - dBottom + sBottom), "v", "  5") + "\n"
            )
        t.write(loi + svgPath("590", str(dTop - sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("590",
            str(int(sheet_height) - dBottom + sBottom), "v", "  5") + "\n"
            )
        t.write(loi + svgPath("780", str(dTop - sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("780",
            str(int(sheet_height) - dBottom + sBottom), "v", "  5") + "\n"
            )
        t.write(loi + svgPath("999", str(dTop - sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("999",
            str(int(sheet_height) - dBottom + sBottom), "v", "  5") + "\n"
            )
        t.write(loi + svgPath("105", str(dTop - sTop), "v", " -5") + "\n")
        t.write(loi + svgPath("  5", "247", "h", " -5") + "\n")
        t.write(loi + svgPath(str(int(sheet_width) - dRight + sRight),
            "247", "h", "  5") + "\n"
            )
        t.write(loi + svgPath("  5", "544", "h", " -5") + "\n")
        t.write(loi + svgPath(str(int(sheet_width) - dRight + sRight),
            "544", "h", "  5") + "\n"
            )

    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close

def createDecorations(
    file_path, sheet_size, da_offsets, if_offsets, tilt = "0"
    ):
    """
    Creates indices, puncher mark, and folding marks
    """
    t = open(file_path, "a", encoding="utf-8")
    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"index-separators\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"fill:none;stroke:#000;stroke-width:0.25;\
stroke-linecap:round\">\n")
    #- extract some values
    sheet_width  = sheet_size[0]
    sheet_height = sheet_size[1]

    da_top    = da_offsets[0]
    da_bottom = da_offsets[1]
    da_left   = da_offsets[2]
    da_right  = da_offsets[3]
    if_top    = if_offsets[0]
    if_bottom = if_offsets[1]
    if_left   = if_offsets[2]
    if_right  = if_offsets[3]

    frame_width  = str(int(sheet_width) - da_left - da_right)
    frame_height = str(int(sheet_height) - da_top - da_bottom)

    #- starting point values of center lines
    index_center = str(int(frame_width) / 2 + da_left)
    index_middle = str(int(frame_height) / 2 + da_top)
    index_left   = str(da_left + 5)
    index_right  = str(int(frame_width) + da_left - 5)
    index_upper  = str(da_top + 5)
    index_lower  = str(int(frame_height) + da_top - 5)

    #- centre and middle markings of drawing area
    loi = levelOfIndentation(4)
    if sheet_width == "210": # format == "DIN-A4":
        index_left = str(da_left)
        t.write(loi + svgPath(index_left, index_middle, "h", "-15") + "\n")
    elif sheet_width == "297": # format == "DIN-A4-":
        index_upper = str(da_top)
        t.write(loi + svgPath(index_center, index_upper, "v", "-15") + "\n")
    elif sheet_width == "420": # format == "DIN-A3":
        index_left = str(da_left+5)
        t.write(loi + svgPath(index_center, index_upper, "v", "-10") + "\n")
        t.write(loi + svgPath(index_center, index_lower, "v", " 10")+  "\n")
        t.write(loi + svgPath(index_left, index_middle, "h", "-20") + "\n")
        t.write(loi + svgPath(index_right, index_middle, "h", " 10") + "\n")
    else :
        t.write(loi + svgPath(index_center, index_upper, "v", "-10") + "\n")
        t.write(loi + svgPath(index_center, index_lower, "v", " 10") + "\n")
        t.write(loi + svgPath(index_left, index_middle, "h", "-10") + "\n")
        t.write(loi + svgPath(index_right, index_middle, "h", " 10") + "\n")

    #- starting point values of separator lines
    index_left  = str(da_left)
    index_right = str(int(frame_width) + da_left)
    index_upper = str(da_top)
    index_lower = str(int(frame_height) + da_top)

    #- set number of horizontal and vertical indices
    # this needs to be extended for American formats
    if sheet_width == "420": # format == "DIN-A3":
        index_count_x = 8
        index_count_y = 6
    elif sheet_width == "594": # format == "DIN-A2":
        index_count_x = 12
        index_count_y = 8
    elif sheet_width == "841": # format == "DIN-A1":
        index_count_x = 16
        index_count_y = 12
    elif sheet_width == "1189": # format == "DIN-A0":
        index_count_x = 24
        index_count_y = 16
    else :
        index_count_x = 0
        index_count_y = 0

    #- index_center and index_middle contain strings but floating point
    #   numbers are needed to calculate
    float_center = int(frame_width) / 2 + da_left
    float_middle = int(frame_height) / 2 + da_top

    #- horizontal index separators
    max = int(index_count_x / 2 - 1)
    for value in range(0, max):
        index_x = str(float_center + (value + 1) * 50)
        t.write(loi + svgPath(index_x, index_upper, "v", " -5") + "\n")
        t.write(loi + svgPath(index_x, index_lower, "v", "  5") + "\n")
        index_x = str(float_center - (value + 1) * 50)
        t.write(loi + svgPath(index_x, index_upper, "v", " -5") + "\n")
        t.write(loi + svgPath(index_x, index_lower, "v", "  5") + "\n")

    #- vertical index separators
    max = int(index_count_y / 2 - 1)
    for value in range(0, max):
        index_y = str(float_middle + (value + 1) * 50)
        t.write(loi + svgPath(index_left, index_y, "h", " -5") + "\n")
        t.write(loi + svgPath(index_right, index_y, "h", "  5") + "\n")
        index_y = str(float_middle - (value + 1) * 50)
        t.write(loi + svgPath(index_left, index_y, "h", " -5") + "\n")
        t.write(loi + svgPath(index_right, index_y, "h", "  5") + "\n")

    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")
    if sheet_width in ["210", "297"]:
        pass
    else:
        t.write(loi + "<g id=\"indices\"\n")
        loi = levelOfIndentation(3)
        t.write(loi + "style=\"font-size:3.5;text-anchor:middle;fill:#000000;\
font-family:osifont\">\n")

        #- position point values of indices for upright characters
        index_left = str(da_left - if_left / 2)
        index_right = str(int(frame_width) + da_left + if_right / 2)
        index_upper = str(da_top - 1)
        index_lower = str(int(frame_height) + da_top + if_bottom - 1)
        if tilt != "0":
            # Adapted values for upper and right indices rotated by 90° ccw
            index_right = str(int(frame_width) + da_left + if_right - 1)
            index_upper = str(da_top - if_top / 2)

        loi = levelOfIndentation(4)
        #- horizontal indices, numbers
        max = int(index_count_x / 2)
        for value in range(0, max):
            index_x = str(float_center + value * 50 + 25)
            t.write(loi + svgText(index_x, index_upper,
                str(int(index_count_x / 2 + value + 1)), tilt) + "\n"
                )
            t.write(loi + svgText(index_x, index_lower,
                str(int(index_count_x / 2 + value + 1))) + "\n"
                )
            index_x = str(float_center - value * 50 - 25)
            t.write(loi + svgText(index_x, index_upper,
                str(int(index_count_x / 2 - value)), tilt) + "\n"
                )
            t.write(loi + svgText(index_x, index_lower,
                str(int(index_count_x / 2 - value))) + "\n"
                )

        #- vertical indices, letters
        max = int(index_count_y / 2)
        for value in range(0, max):
            index_y = str(float_middle + value * 50 + 25)
            if int(index_count_y / 2 + value + 1) > 9 :
                # This avoids the letter J
                t.write(loi + svgText(index_left, index_y,
                    chr(64 + int(index_count_y / 2 + value + 2))) + "\n"
                    )
                t.write(loi + svgText(index_right, index_y,
                    chr(64 + int(index_count_y / 2 + value + 2)), tilt) + "\n"
                    )
            else :
                t.write(loi + svgText(index_left, index_y,
                    chr(64 + int(index_count_y / 2 + value + 1))) + "\n"
                    )
                t.write(loi + svgText(index_right, index_y,
                    chr(64 + int(index_count_y / 2 + value + 1)), tilt) + "\n"
                    )
            # no J expected below
            index_y = str(float_middle - value * 50 - 25)
            t.write(loi + svgText(index_left, index_y,
                chr(64 + int(index_count_y / 2 - value))) + "\n"
                )
            t.write(loi + svgText(index_right, index_y,
                chr(64 + int(index_count_y / 2 - value)), tilt) + "\n"
                )

        loi = levelOfIndentation(2)
        t.write(loi + "</g>\n\n")

        #- puncher mark
        t.write(loi + "<g id=\"puncher mark\"\n")
        loi = levelOfIndentation(3)
        t.write(loi + "style=\"fill:none;stroke:#b0b0b0;stroke-width:0.25;\
stroke-linecap:miter;stroke-miterlimit:4\">\n")
        loi = levelOfIndentation(4)
        if sheet_width in ["1189", "841", "594"] : # A3 and A4 have extended middle markings
            t.write(
                loi + svgPath(str(da_left - if_left),
                str(int(sheet_height) - (297 / 2)), "h", "-10") + "\n"
                )
        loi = levelOfIndentation(2)
        t.write(loi + "</g>\n\n")

        #- folding marks
        t.write(loi + "<g id=\"folding marks\"\n")
        loi = levelOfIndentation(3)
        t.write(loi + "style=\"fill:none;stroke:#b0b0b0;stroke-width:0.25;\
stroke-linecap:miter;stroke-miterlimit:4\">\n")
        loi = levelOfIndentation(4)
        if sheet_width == "420": # DIN-A3
            t.write(loi + svgPath("125", str(da_top - if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("125",
                str(int(sheet_height) - da_bottom + if_bottom),"v","  5")+"\n"
                )
            t.write(loi + svgPath("230", str(da_top - if_top), "v", "-5") + "\n")
            t.write(loi + svgPath("230",
                str(int(sheet_height) - da_bottom + if_bottom),"v","  5")+"\n"
                )
        elif sheet_width == "594": # DIN-A2
            t.write(loi + svgPath("210", str(da_top-if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("210",
                str(int(sheet_height) - da_bottom+if_bottom),"v","  5")+"\n"
                )
            t.write(loi + svgPath("402", str(da_top-if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("402",
                str(int(sheet_height) - da_bottom + if_bottom),"v","  5")+"\n"
                )
            t.write(loi + svgPath("105", str(da_top-if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("  5", "123", "h", " -5") + "\n")
            t.write(loi + svgPath(
                str(int(sheet_width) - da_right + if_right), "123", "h",
                "  5") + "\n"
                )
        elif sheet_width == "841": # DIN-A1
            t.write(loi + svgPath("210", str(da_top-if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("210",
                str(int(sheet_height) - da_bottom + if_bottom), "v", "  5") + "\n"
                )
            t.write(loi + svgPath("400", str(da_top-if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("400",
                str(int(sheet_height) - da_bottom + if_bottom), "v", "  5") + "\n"
                )
            t.write(loi + svgPath("651", str(da_top-if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("651",
                str(int(sheet_height) - da_bottom + if_bottom), "v", "  5") + "\n"
                )
            t.write(loi + svgPath("105", str(da_top-if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("  5", "297", "h", " -5") + "\n")
            t.write(loi + svgPath(str(int(sheet_width) - da_right + if_right),
                "297", "h", "  5") + "\n"
                )
        elif sheet_width == "1189": # DIN-A0
            t.write(loi + svgPath("210", str(da_top - if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("210",
                str(int(sheet_height) - da_bottom + if_bottom), "v", "  5") + "\n"
                )
            t.write(loi + svgPath("400", str(da_top - if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("400",
                str(int(sheet_height) - da_bottom + if_bottom), "v", "  5") + "\n"
                )
            t.write(loi + svgPath("590", str(da_top - if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("590",
                str(int(sheet_height) - da_bottom + if_bottom), "v", "  5") + "\n"
                )
            t.write(loi + svgPath("780", str(da_top - if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("780",
                str(int(sheet_height) - da_bottom + if_bottom), "v", "  5") + "\n"
                )
            t.write(loi + svgPath("999", str(da_top - if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("999",
                str(int(sheet_height) - da_bottom + if_bottom), "v", "  5") + "\n"
                )
            t.write(loi + svgPath("105", str(da_top - if_top), "v", " -5") + "\n")
            t.write(loi + svgPath("  5", "247", "h", " -5") + "\n")
            t.write(loi + svgPath(str(int(sheet_width) - da_right + if_right),
                "247", "h", "  5") + "\n"
                )
            t.write(loi + svgPath("  5", "544", "h", " -5") + "\n")
            t.write(loi + svgPath(str(int(sheet_width) - da_right + if_right),
                "544", "h", "  5") + "\n"
                )

        loi = levelOfIndentation(2)
        t.write(loi + "</g>\n\n")
    t.close

def createFreecadLogo(file_path, logo_position):
    """
    Creates a FreeCAD logo at a given position
    """
    t=open(file_path,"a", encoding="utf-8")
    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"freecad-logo\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "fill-rule=\"evenodd\"\n")
    #- Position from lower right corner of the drawing area
    st_x = logo_position[0]
    st_y = logo_position[1]
    t.write(loi + "transform=\"translate("+str(st_x)+","+str(st_y)+") scale(0.08)\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + "<path fill=\"#FF585D\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "d=\"m 15.5 0 h 43.5 v 10.5 l -10.5 10.5 v -10.5 h -33 v 43 \n")
    t.write(loi + "h 10.5 l -10.5 10.5 h -10.5 v -53.5 z\"/>\n")
    loi = levelOfIndentation(4)
    t.write(loi + "<path fill=\"#CB333B\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "d=\"m 15.5 43 l -10.5 10.5 v -43 l 10.5 -10.5 h 33 \n")
    t.write(loi + "l -10.5 10.5 h -22.5 z\"/>\n")
    loi = levelOfIndentation(4)
    t.write(loi + "<path fill=\"#418FDE\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "d=\"m 59 10.5 l -10.5 10.5 h -22.5 v 8 h 11 v 10.5 \n")
    t.write(loi + "h -11 v 14 l -10.5 10.5 \n")
    t.write(loi + "H 26.4675 C 27.2762 64 28 63.48 28.2424 62.71 L 30.173 56.7687 \n")
    t.write(loi + "C 30.3577 56.20 30.80 55.756 31.372 55.57 L 32.856 55.09 \n")
    t.write(loi + "C 33.425 54.904 34.047 55.0 34.53 55.3535 L 39.5836 59.026 \n")
    t.write(loi + "C 40.238 59.50 41.125 59.50 41.7789 59.026 L 46.3085 55.7338 \n")
    t.write(loi + "C 46.963 55.2585 47.2364 54.4166 46.9864 53.6475 L 45.0558 47.705 \n")
    t.write(loi + "C 44.87 47.137 44.97 46.515 45.3218 46.03 L 46.2396 44.7688 \n")
    t.write(loi + "C 46.59 44.285 47.15 43.9985 47.7485 43.9985 L 53.9965 44.0 \n")
    t.write(loi + "C 54.805 44.0 55.5215 43.4778 55.77 42.71 L 57.50 37.3839 \n")
    t.write(loi + "C 57.75 36.6148 57.4785 35.77 56.8242 35.2962 L 51.7696 31.6238 \n")
    t.write(loi + "C 51.2862 31.2725 51.0 30.7124 51.0 30.1148 V 28.5535 \n")
    t.write(loi + "C 51.0 27.956 51.2862 27.3944 51.77 27.0432 L 58.23 22.8333 \n")
    t.write(loi + "C 58.7144 22.4821 59 21.92 59 21.323 V 10.6666 Z\"/>\n")
    loi = levelOfIndentation(4)
    t.write(loi + "<path fill=\"white\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "d=\"m 15.5 10.5 h 33 v 10.5 h -22.5 v 8 h 11 v 10.5 \n")
    t.write(loi + "h -11 v 14 h -10.5 z\"/>\n")
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close

def createProjectionSymbol(file_path, proj_symb_position):
    """
    Creates a symbol for the projection method in the title block
    at a given position
    """
    # order top and side symbols
    if projectionGroupAngle() == 1:
        # Third angle projection
        top_offset  = "-3.5"
        side_offset =  "3.5"
    else:
        # First angle projection
        top_offset  =  "3.5"
        side_offset = "-3.5"

    t = open(file_path, "a", encoding = "utf-8")
    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"Projection-symbol\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "stroke=\"#000000\"\n")
    t.write(loi + "stroke-width=\"0.18\"\n")
    t.write(loi + "stroke-linecap=\"round\"\n")
    t.write(loi + "stroke-linejoin=\"round\"\n")
    t.write(loi + "fill=\"none\"\n")
    st_x = proj_symb_position[0]
    st_y = proj_symb_position[1]
    t.write(loi + "transform=\"translate(" + str(st_x) + "," + str(st_y) + ")\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + "<g id=\"Top\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "transform=\"translate(" + top_offset + "," + "0.0" + ")\">\n")
    loi = levelOfIndentation(6)
    t.write(loi + "<circle cx=\"0.0\" cy=\"0.0\" r=\"1.0\"\n")
    loi = levelOfIndentation(7)
    t.write(loi + "stroke=\"#0000d0\" stroke-width=\"0.35\"/>\n")
    loi = levelOfIndentation(6)
    t.write(loi + "<circle cx=\"0.0\" cy=\"0.0\" r=\"2.0\"\n")
    loi = levelOfIndentation(7)
    t.write(loi + "stroke=\"#0000d0\" stroke-width=\"0.35\"/>\n")
    loi = levelOfIndentation(6)
    t.write(loi + svgPath(" -2.5 ", " 0   ", "h", " 1") + "\n")
    t.write(loi + svgPath(" -1.15", " 0   ", "h", " 0.3") + "\n")
    t.write(loi + svgPath(" -0.5 ", " 0   ", "h", " 1") + "\n")
    t.write(loi + svgPath("  0.85", " 0   ", "h", " 0.3") + "\n")
    t.write(loi + svgPath("  1.5 ", " 0   ", "h", " 1") + "\n")
    t.write(loi + svgPath("  0   ", "-2.5 ", "v", " 1") + "\n")
    t.write(loi + svgPath("  0   ", "-1.15", "v", " 0.3") + "\n")
    t.write(loi + svgPath("  0   ", "-0.5 ", "v", " 1") + "\n")
    t.write(loi + svgPath("  0   ", " 0.85", "v", " 0.3") + "\n")
    t.write(loi + svgPath("  0   ", " 1.5 ", "v", " 1") + "\n")
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    t.write(loi + "<g id=\"Side\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "transform=\"translate(" + side_offset + "," + "0.0" + ")\">\n")
    loi = levelOfIndentation(6)
    t.write(loi + "<path d=\"m -2.5 1.0 v -2.0 l 5.0 -1.0 v 4.0 z \"\n")
    loi = levelOfIndentation(7)
    t.write(loi + "stroke=\"#0000d0\" stroke-width=\"0.35\"/>\n")
    loi = levelOfIndentation(6)
    t.write(loi + svgPath(" -3.0 ", " 0   ", "h", " 1") + "\n")
    t.write(loi + svgPath(" -0.5 ", " 0   ", "h", " 1") + "\n")
    t.write(loi + svgPath("  2.0 ", " 0   ", "h", " 1") + "\n")
    t.write(loi + svgPath(" -1.4 ", " 0   ", "h", " 0.3") + "\n")
    t.write(loi + svgPath("  1.1 ", " 0   ", "h", " 0.3") + "\n")
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close

# Methods to generate document-related data:

def existingPages(document):
    """
    Counts existing pages in the given document
    """
    number_of_pages = 0
    for item in document.Objects:
        if item.Name.startswith("Page"):
            number_of_pages += 1
    return number_of_pages

def getDate():
    today = time.strftime("%Y-%m-%d") # %Y: YYYY, %y: YY
    return today

def getVersion():
    """
    Reads the FreeCAD version from the running application
    """
    av = App.Version()
    if av[2] == "0":
        app_version = (av[0] + "." + av[1] + "." + av[2] + " - " + av[3][:-5])
    else:
        app_version = ("FC v. " + av[0] + "." + av[1] + "." + av[2])
    return app_version

def projectionGroupAngle():
    """
    Reads the projection convention from the preferences settings
    """
    parameter_path = FreeCAD.ParamGet(
        "User parameter:BaseApp/Preferences/Mod/TechDraw/General"
        )
    projection_angle = parameter_path.GetInt("ProjectionAngle")
    return projection_angle

def getAktiveDocument():
    # Returns the active document or exits the program
    ado = FreeCAD.activeDocument()
    if ado is None:
        QMessageBox.warning(None, "", "No active document!")
        exit()
    return ado

def getTemplatePath(template_name = "NewTemplate.svg"):
    '''
    Defines the path to the folder to store the template file
    including the file name.
    '''
    # Extracts the path to the template folder from the FreeCAD parameters
    parameter_path = FreeCAD.ParamGet(
        "User parameter:BaseApp/Preferences/Mod/TechDraw/Files"
        )
    template_path = parameter_path.GetString("TemplateDir")
    if template_path == "":
        QMessageBox.warning(
            None, "", "No template file has been set yet!"
            )
        exit()
    #- Link template_path and template_name for any OS
    file_path = os.path.join(template_path, template_name)
    return file_path
