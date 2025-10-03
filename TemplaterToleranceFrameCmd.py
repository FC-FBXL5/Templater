# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2025 FBXL5 available on the forum:                      *
# *   https://forum.freecad.org/memberlist.php?mode=viewprofile&u=26761     *
# *                                                                         *
# *   This file is part of FreeCAD.                                         *
# *                                                                         *
# *   FreeCAD is free software: you can redistribute it and/or modify it    *
# *   under the terms of the GNU Lesser General Public License as           *
# *   published by the Free Software Foundation, either version 2.1 of the  *
# *   License, or (at your option) any later version.                       *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful, but        *
# *   WITHOUT ANY WARRANTY; without even the implied warranty of            *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU      *
# *   Lesser General Public License for more details.                       *
# *                                                                         *
# *   You should have received a copy of the GNU Lesser General Public      *
# *   License along with FreeCAD. If not, see                               *
# *   <https://www.gnu.org/licenses/>.                                      *
# *                                                                         *
# ***************************************************************************
"""Creates a tolerance frame or a datum frame with editable texts"""


"""
I have tried to follow this naming rule:
 class names:    CamelCase
 function names: mixedCase
 constant names: ALL_CAPITAL + underscore
 variable names: lower_case + underscore
"""

# imports and constants
import FreeCAD
import SvgToolkit
import os     # built-in modules
from TechDrawTools import TDToolsUtil
from PySide import QtCore
from PySide.QtCore import QT_TRANSLATE_NOOP
from PySide.QtGui import (QAction, QGroupBox, QMessageBox)
from PySide.QtWidgets import (QGridLayout, QLabel, QComboBox, QDoubleSpinBox)

translate = FreeCAD.Qt.translate

icons_path = SvgToolkit.icons_path
mod_path = SvgToolkit.mod_path
file_path = os.path.join(mod_path, "Resources", "NewSymbol.svg")


def getActiveDocument():
    """
    Returns the active document or exits the command
    """
    ado = FreeCAD.activeDocument()
    if ado is not None:
        return ado
    message = translate("Templater", "No active document available!")
    TDToolsUtil.displayMessage("AuxView", message)
    return False

def getPageOfSelection(doc, active_view):
    """
    Retrieves the Page that holds the selected elements
    """
    #- Find an object starting with 'Page' that contains the selected object
    for each in doc.Objects:
        if each.Name.startswith("Page"):
            for item in each.OutList: # Search items belonging to a Page object
                if item.Name.startswith("ProjGroup"): # Look into projection groups
                    for view in item.OutList: # Search views belonging to a ProjGroup object
                        if view.Name == active_view.Name:
                            return each
                else:
                    if item.Name == active_view.Name:
                        return each
    return False

def ediText(entry_name, x, y, str_value, str_angle="0"):
    """
    Generates an svg-instruction to place an editable text element
    with the given values.
    Optional str_angle enables vertical and arbitrarily rotated editable texts
    """
    #- Offsets to place DIN Alternate texts with a height of 6.5 properly
    x = str(float(x) + 0.9) # offset from the cell center
    y = str(float(y) + 2.4) # offset fron the middle of the cell

    if str_angle == "0":
        svg_line = (
            "<text freecad:editable=\"" + entry_name + "\" x=\"" + x
            + "\" y=\"" + y + "\" fill=\"#000\"> <tspan>" + str_value
            + "</tspan> </text>"
            )
    else:
        svg_line = (
            "<text freecad:editable=\"" + entry_name + "\" x=\"" + x
            + "\" y=\"" + y + "\" fill=\"#000\" transform=\"rotate("
            + str_angle +  "," + x + "," + y + ")\"> <tspan>" + str_value
            + "</tspan> </text>"
            )
    return svg_line

def annoItem(type = "A", pos_x = "5", pos_y = "5"):
    """
    Supplies geometries for the tolerance symbols or an editable datum marker
    """
    TYPE_DICT = {
        "Straightness":["<path d=\"m 2 5 h 6 \" />"],
        "Flatness":["<path d=\"m 2 7.25 l 2 -4.5  h 4 l -2 4.5 z \" />"],
        "Roundness":["<circle cx=\"5.0\" cy=\"5.0\" r=\"3.25\" />"],
        "Concentricity":["<circle cx=\"5.0\" cy=\"5.0\" r=\"3.25\" />"
            "<circle cx=\"5.0\" cy=\"5.0\" r=\"1.75\" />"],
        "Cylindricity":["<circle cx=\"5.0\" cy=\"5.0\" r=\"1.75\" />"
            "<path d=\"m 2 8.25 l 2 -6.5  m 4 0 l -2 6.5 \" />"],
        "Position":["<circle cx=\"5.0\" cy=\"5.0\" r=\"1.75\" />"
            "<path d=\"m 2 5 h 6  m -3 -3 v 6 \" />"],
        "Parallelism":["<path d=\"m 2.5 8.25 l 2 -6.5 m 3 0 l -2 6.5 \" />"],
        "Perpendicularity":["<path d=\"m 2 8.25 h 6 m -3 0 v -6 \" />"],
        "Angularity":["<path d=\"m 8 8.25 h -6 l 6 -6 \" />"],
        "Symmetry":["<path d=\"m 2 5 h 6 m -1 -2 h -4 m 0 4 h 4 \" />"],
        "LineProfile":["<path d=\"m 2 6 a 3 3 0 0 1 6 0 \" />"],
        "SurfaceProfile":["<path d=\"m 2 6 a 3 3 0 0 1 6 0 z \" />"],
        "CircularRunOut":[
            "<path d=\"m 4 8.5 l 2 -6.5 l -0.15 3 m 0.15 -3l -1.55 2.55 \" />"],
        "TotalRunOut":["<path d=\"m 8 2 l -2 6.5 l -4 0 l 2 -6.5 l -0.15 3" +
            "m 4 0 l 0.15 -3 l -1.55 2.55 m -4 0 l 1.55 -2.55 \" />"]
        }
    if type in TYPE_DICT:
        return TYPE_DICT[type]
    else:
        return [ediText("Datum", pos_x, pos_y, type)]  # 5, 5 for datum frame

def symbolObject(svg_path, symbol_name):
    """
    Creates a TechDraw symbol object in the active document
    """
    #- Create the symbol as a document object
    active_doc = getActiveDocument()
    new_symbol = active_doc.addObject("TechDraw::DrawViewSymbol",symbol_name)
    #- Load SVG file
    svg_file = open(svg_path, "r", encoding="utf-8")
    svg_code = svg_file.read()
    svg_file.close()
    new_symbol.Symbol = svg_code
    return new_symbol

def insertSymbol(td_symbol):
    """
    Inserts a symbol in the active document
    """
    Symbol_name = td_symbol.Name
    #- Retrieve the active document
    active_doc = getActiveDocument()
    #- Retrieve the selection view
    if TDToolsUtil.getSelView():
        active_view = TDToolsUtil.getSelView()
    else:
        return
    #- Retrieve the page that holds the view
    active_page = getPageOfSelection(active_doc, active_view)
    #- To see changes immediately
    active_page.KeepUpdated = True
    #- Add the symbol to the page
    active_page.addView(td_symbol)
    #- Add a view as owner to synchronise movements
    td_symbol.Owner = active_view

    Gui.runCommand("TechDraw_RedrawPage",0)
    #- To no longer see changes immediately
    active_page.KeepUpdated = False

    active_page.ViewObject.doubleClicked()
    return

def createFrame(file_path, strings, cell_widths = [10]):
    """
    Creates a rectangle and separator lines for the tolerance/datum frame
    """
    s = open(file_path, "a", encoding="utf-8")
    loi = levelOfIndentation(2)
    s.write(loi + "<g id=\"first-frame\"\n")
    loi = levelOfIndentation(3)
    s.write(loi +
        "style=\"fill:#fff;fill-opacity:1;stroke:#000;stroke-width:0.5;\n"
        )
    s.write(loi +
        "stroke-linecap:round;stroke-linejoin:round;font-size:6.5;\n"
        )
    s.write(loi +
        "text-anchor:middle;font-family:DIN Alternate\">\n"
        )
    loi = levelOfIndentation(4)

    #- set frame dimensions
    number_of_cells = len(cell_widths)
    anno_segments = annoItem(strings[0])

    if number_of_cells == 1:
        #- Create a single square datum frame
        s.write(loi + svgRect("9.5", "9.5", "0.25", "0.25") + "\n")
        s.write(loi + anno_segments[0] + "\n")
    else:
        #- Create a rectangle, with length of lines instead of outer length
        length = 0
        for value in cell_widths:
            length += (value - 0.5) # Outer length minus one line width
        #- Write the outer rectangle
        s.write(loi + svgRect(str(length), "9.5", "0.25", "0.25") + "\n")
        #- Create annotation and separators
        float_X = 0.25  # one half of the line width
        for each in range(number_of_cells):
            half_X = (float(cell_widths[each]) - 0.5) / 2
            float_X += half_X  # half width to the center of the cell
            if each == 0:
                for line in anno_segments:
                    s.write(loi + line + "\n")
            else:
                label = ("Value" + str(each))
                #- Write editable value
                s.write(loi + ediText(label, str(float_X), "5",
                    strings[each]) + "\n"
                    )
            float_X += half_X  # half width to the end of the cell
            if each < (number_of_cells - 1):
                #- Draw a separator line
                s.write(loi + "<path d=\"m " + str(float_X) +
                    " 0.25 v 9.5 \" />" + "\n"
                    )

    loi = levelOfIndentation(2)
    s.write(loi + "</g>\n")
    s.close

def createSymbol(
    tolerance,
    value,
    reference1,
    reference2,
    reference3):
    """
    First determines the length of the frame then calls external methods
    to build the head and outer body tags.
    (<svg>...</svg> to embed grouped elements)
    """
    #- String list for the frame
    strings = [tolerance, value, reference1, reference2, reference3]
    #- Widths list for the frame
    if (len(tolerance) == 1):
        widths = [10]
    else:
        #- set default width values
        width1 = 10
        width2 = 10
        width3 = 10
        width4 = 10
        width5 = 10
        #- add extra length for string values
        width2 += len(value) * 2.0
        widths = [width1, width2]
        if reference1 != "":
            if len(reference1) > 1:
                width3 += len(reference1) * 1.5
            widths.append(width3)
            if reference2 != "":
                if len(reference2) > 1:
                    width4 += len(reference2) * 1.5
                widths.append(width4)
                if reference3 != "":
                    if len(reference3) > 1:
                        width5 += len(reference3) * 1.5
                    widths.append(width5)
    #- calculate the symbol length
    length = 0.5 # start with one line width
    for value in widths:
        length += (float(value) - 0.5) # Outer length minus one line width
    symbol_width = str(length)
    symbol_height = "10"

    SvgToolkit.createSvgFile(file_path)
    SvgToolkit.startSvg(file_path, symbol_width, symbol_height)
    createFrame(file_path, strings, widths)
    SvgToolkit.endSvg(file_path)
    # At this point an SVG symbol file is created in the given directory
    #- Create a symbol object and insert it into a drawig pages
    frame_symbol = symbolObject(file_path, "FeatureFrame")
    insertSymbol(frame_symbol)
    return
##########################################################################################################
# Gui code
##########################################################################################################

if SvgToolkit.isGuiLoaded():
    from FreeCAD import Gui
    from SvgToolkit import (
        levelOfIndentation,
        svgPath,
        svgRect,
        svgText,
        )

    ##########################################################################################################
    # View Provider
    ##########################################################################################################

    ##########################################################################################################
    # Task Panel
    ##########################################################################################################

    class ToleranceFramePanel(object):
        """
        A task panel to gather all settings for a certain tolerance frame
        """

        def __init__(self):
            self.initUI()

        def initUI(self):
            """
            Sets some default values and places the widgets
            """
            #- Some default values
            self.result            = "Cancelled" # Default return status
            self.result_tolrance   = "Position" # Default tolerance type
            self.result_value      = "⌀ 0,01" # Size of tolerance area
            self.result_reference1 = "A" # first datum element
            self.result_reference2 = "B" # second datum element
            self.result_reference3 = "C" # third datum element

            self.setWindowTexts()

            #- Add a Box container to group widgets
            self.groupBox = QGroupBox(self.text_panel)
            #- Add a grid to order widgets
            self.grid = QGridLayout() # instantiates a QGridLayout
            self.groupBox.setLayout(self.grid) # puts the grid inside the groupBox
            #- Add some labels to the grid
            #self.label_title = QLabel('Grid-Überschrift')
            #self.grid.addWidget(self.label_title, 0, 0)
            self.label_tolerance_type = QLabel(self.text_type)
            self.grid.addWidget(self.label_tolerance_type, 1, 0)
            self.label_tolerance_value = QLabel(self.text_value)
            self.grid.addWidget(self.label_tolerance_value, 2, 0)
            self.label_first_datum = QLabel(self.text_first)
            self.grid.addWidget(self.label_first_datum, 3, 0)
            self.label_second_datum = QLabel(self.text_second)
            self.grid.addWidget(self.label_second_datum, 4, 0, 1, -1)
            self.label_third_datum = QLabel(self.text_third)
            self.grid.addWidget(self.label_third_datum, 5, 0, 1, -1)

            # Add some input widgets
            #- set up a ComboBox - Tolerance type
            self.coBox_tolerance = QComboBox()
            self.tolerance_list = (
                self.option_01,
                self.option_02,
                self.option_03,
                self.option_04,
                self.option_05,
                self.option_06,
                self.option_07,
                self.option_08,
                self.option_09,
                self.option_10,
                self.option_11,
                self.option_12,
                self.option_13,
                self.option_14,
                self.option_15,
                )  # see setWindowTexts()
            self.coBox_tolerance.setToolTip(self.tooltip_tol)
            #self.coBox_tolerance.setFixedWidth(150)
            self.coBox_tolerance.setEditable(True)
            self.coBox_tolerance.addItems(self.tolerance_list)
            self.coBox_tolerance.setCurrentIndex(
                self.tolerance_list.index(self.option_06)
                )
            self.coBox_tolerance.currentTextChanged.connect(
                self.onCoBoxTolerance
                )
            self.grid.addWidget(self.coBox_tolerance, 1, 1)
            # set up ComboBox - Tolerance value
            self.coBox_value = QComboBox()
            self.value_list = ("⌀ 0,001", "⌀ 0,01", "⌀ 0,1", "⌀ 1,0", "")
            self.coBox_value.setToolTip(self.tooltip_tol)
            self.coBox_value.setEditable(True)
            self.coBox_value.addItems(self.value_list)
            self.coBox_value.setCurrentIndex(self.value_list.index("⌀ 0,1"))
            #self.input_value.activated[str].connect(self.onInputValue)
            self.coBox_value.currentTextChanged.connect(self.onCoBoxValue)
            self.grid.addWidget(self.coBox_value, 2, 1)
            # set up ComboBox - Reference1
            self.coBox_Reference1 = QComboBox()
            self.reference1_list = ("A", "A-B", "X", "X-Y", "")
            self.coBox_Reference1.setToolTip(self.tooltip_tol)
            self.coBox_Reference1.setEditable(True)
            self.coBox_Reference1.addItems(self.reference1_list)
            self.coBox_Reference1.setCurrentIndex(
                self.reference1_list.index("A"))
            #self.input_Reference1.activated[str].connect(self.ononCoBoxReference1)
            self.coBox_Reference1.currentTextChanged.connect(
                self.onCoBoxReference1)
            self.grid.addWidget(self.coBox_Reference1, 3, 1)
            # set up ComboBox - Reference2
            self.coBox_Reference2 = QComboBox()
            self.reference2_list = ("B", "B-C", "Y", "Y-Z", "")
            self.coBox_Reference2.setToolTip(self.tooltip_tol)
            self.coBox_Reference2.setEditable(True)
            self.coBox_Reference2.addItems(self.reference2_list)
            self.coBox_Reference2.setCurrentIndex(
                self.reference2_list.index("B"))
            #self.input_Reference2.activated[str].connect(self.ononCoBoxReference2)
            self.coBox_Reference2.currentTextChanged.connect(
                self.onCoBoxReference2)
            self.grid.addWidget(self.coBox_Reference2, 4, 1)
            # set up ComboBox - Reference3
            self.coBox_Reference3 = QComboBox()
            self.reference3_list = ("C", "C-D", "Z", "Z-R", "")
            self.coBox_Reference3.setToolTip(self.tooltip_tol)
            self.coBox_Reference3.setEditable(True)
            self.coBox_Reference3.addItems(self.reference3_list)
            self.coBox_Reference3.setCurrentIndex(
                self.reference3_list.index("C"))
            #self.input_Reference3.activated[str].connect(self.onCoBoxReference3)
            self.coBox_Reference3.currentTextChanged.connect(
                self.onCoBoxReference3)
            self.grid.addWidget(self.coBox_Reference3, 5, 1)

            # Show the QGroupBox
            self.form = self.groupBox

        def setWindowTexts(self):
            self.text_panel    = translate("Templater", "Feature Frame Settings")
            self.text_ok       = translate("Templater", "OK")
            self.text_cancel   = translate("Templater", "Cancel")
            self.text_type     = translate("Templater", "Tolerance type")
            self.text_value    = translate("Templater", "Tolerance value")
            self.text_first    = translate("Templater", "Datum1")
            self.text_second   = translate("Templater", "Datum2")
            self.text_third    = translate("Templater", "Datum3")
            self.text_area     = translate("Templater",
                "Circular tolerance area"
                )
            self.text_square   = translate("Templater", "Square")
            self.text_round    = translate("Templater", "Round")
            self.text_default  = translate("Templater", "0,02")
            self.text_maximum  = translate("Templater", "1,0")
            self.tooltip_tol   = translate("Templater",
                "Selects the tolerance type \n"
                "Select from the list or type \n"
                "a sinngle upper case letter for a datum frame"
                )
            self.tooltip_datum = translate("Templater", "Sets a datum marker")
            self.tooltip_value = translate("Templater",
                "Sets the size of the tolerance field"
                )

            self.option_01 = "⏤ " + translate("Templater", "Straightness")
            self.option_02 = "⏥ " + translate("Templater", "Flatness")
            self.option_03 = "○ " + translate("Templater", "Roundness")
            self.option_04 = "◎ " + translate("Templater", "Concentricity")
            self.option_05 = "⌭ " + translate("Templater", "Cylindricity")
            self.option_06 = "⌖ " + translate("Templater", "Position")
            self.option_07 = "∥ " + translate("Templater", "Parallelism")
            self.option_08 = "⟂ " + translate("Templater", "Perpendicularity")
            self.option_09 = "∠ " + translate("Templater", "Angularity")
            self.option_10 = "⌯ " + translate("Templater", "Symmetry")
            self.option_11 = "⌒ " + translate("Templater", "LineProfile")
            self.option_12 = "⌓ " + translate("Templater", "SurfaceProfile")
            self.option_13 = "↗ " + translate("Templater", "CircularRunOut")
            self.option_14 = "⌰ " + translate("Templater", "TotalRunOut")
            self.option_15 = "X " + translate("Templater", "Datum")
            return

        def onCoBoxTolerance(self, current_text):
            if len(current_text) == 1:
                self.result_tolrance = current_text
            elif current_text.endswith(self.option_15[2:]):
                self.result_tolrance = current_text[0]
            else:
                self.result_tolrance = current_text[2:]

        def onCoBoxValue(self, current_text):
            self.result_value = current_text

        def onCoBoxReference1(self, current_text):
            self.result_reference1 = current_text

        def onCoBoxReference2(self, current_text):
            self.result_reference2 = current_text

        def onCoBoxReference3(self, current_text):
            self.result_reference3 = current_text

        def retranslate(self, tolerance):
            """
            This is required since the instructions to draw the related
            tolerance symbols are addressed by their English names for clarity.
            This worked well until translation was involved.
            """
            TOL_DICT = {
                self.option_01[2:]:"Straightness",
                self.option_02[2:]:"Flatness",
                self.option_03[2:]:"Roundness",
                self.option_04[2:]:"Concentricity",
                self.option_05[2:]:"Cylindricity",
                self.option_06[2:]:"Position",
                self.option_07[2:]:"Parallelism",
                self.option_08[2:]:"Perpendicularity",
                self.option_09[2:]:"Angularity",
                self.option_10[2:]:"Symmetry",
                self.option_11[2:]:"LineProfile",
                self.option_12[2:]:"SurfaceProfile",
                self.option_13[2:]:"CircularRunOut",
                self.option_14[2:]:"TotalRunOut",
                self.option_15[2:]:"Datum",
                }
            if tolerance in TOL_DICT:
                return TOL_DICT[tolerance]
            return tolerance

        def accept(self):
            '''
            This is triggered by the panel's OK button.
            But also prevents the closing of the panel
            '''
            # Collect results
            tolerance = self.retranslate(self.result_tolrance)
            value = self.result_value
            reference1 = self.result_reference1
            reference2 = self.result_reference2
            reference3 = self.result_reference3
            Gui.Control.closeDialog()
            createSymbol(
                tolerance,
                value,
                reference1,
                reference2,
                reference3
                )
            return

        def reject(self):
            '''
            This is triggered by the panel's Cancel button.
            But also prevents the closing of the panel
            '''
            FreeCADGui.Control.closeDialog()
            print("Cancelled, there is nothing left to do...")

    ##########################################################################################################
    # Command
    ##########################################################################################################

    class TolFrameCommandClass():
        """Creates a tolerance frame for several tolerances"""

        def GetResources(self):
            return {
                "Pixmap": os.path.join(
                    icons_path, "Templater_ToleranceFrame.svg"
                    ),  # the name of a svg file available in the resources
                "MenuText": QT_TRANSLATE_NOOP("Templater_ToleranceFrame",
                    "Tolerance frame"
                    ),
                # "Accel": "S, H",
                "ToolTip": QT_TRANSLATE_NOOP("Templater_ToleranceFrame",
                    "Creates a tolerance frame for a specific geometric tolerance\n"
                    "1. Invoke this Command.\n"
                    "2. Adjust parameters",
                    ),
                }

        def Activated(self):
            panel = ToleranceFramePanel()
            Gui.Control.showDialog(panel)
            # Further steps are launched from the OK option of the panel
            return

        def IsActive(self):
            return True

    Gui.addCommand("Templater_ToleranceFrame", TolFrameCommandClass())
