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
This tool creates and inserts a template similar to the result of the
TechDraw TemplateGenerator tutorial in the wiki.
In this case the svg generating code is stored in a separate file.
"""


"""
I have tried to follow this naming rule:
 class names:    CamelCase
 function names: mixedCase
 constant names: ALL_CAPITAL + underscore
 variable names: lower_case + underscore
"""

# imports and constants
import FreeCAD
import FreeCADGui
import os     # built-in modules
import SvgToolkit
from PySide import QtCore
from PySide.QtGui import (QAction, QGroupBox, QMessageBox)
from PySide.QtWidgets import (QGridLayout, QLabel, QComboBox,
    QDoubleSpinBox, QCheckBox
    )
from SvgToolkit import (
    levelOfIndentation,
    svgPath,
    svgText,
    ediText
    )

#from PySide.QtGui import QMessageBox

icons_path = SvgToolkit.icons_path
mod_path = SvgToolkit.mod_path
file_path = os.path.join(mod_path, "Resources", "WikiTemplate.svg")

def getActiveDocument():
    """
    Returns the active document or exits the command
    """
    ado = FreeCAD.activeDocument()
    if ado is None:
        QMessageBox.warning(None, "", "No active document available!")
        #exit()
    return ado

def existingPages(document):
    """
    Counts existing pages in the active document
    """
    number_of_pages = 0
    for item in document.Objects:
        if item.Name.startswith("Page"):
            number_of_pages += 1
    return number_of_pages

def insertTemplate(active_doc, template_path):
    """
    Inserts a page and a template in the active document
    """
    #- Count existing pages and add one for the new page number
    page_mumber = existingPages(active_doc) + 1
    #- Define the new page's name and the new template's name
    #  (with only 2 trailing digits starting with 01)
    if page_mumber < 10:
        # insert leading zero
        next = ("0" + str(page_mumber))
    else:
        next = str(page_mumber)
    new_page = ("Page" + next)
    new_template = ('Template' + next)
    # add a page object to the active document
    active_doc.addObject('TechDraw::DrawPage',new_page)
    # add a template object to the active document
    active_doc.addObject('TechDraw::DrawSVGTemplate',new_template)
    # load the svg template into the template object
    active_doc.getObject(new_template).Template = template_path
    # add the template object to the page's object list
    active_doc.getObject(new_page).Template = active_doc.getObject(new_template)
    # At this point the document received a new page with a new template
    result = [page_mumber, new_page]
    return result

def createTitleBlock(file_path, sheet_width, sheet_height):
    """
    Calls external methods to create a movable title block
    according to DIN EN ISO 7200
    """
    #- Lower left corner of the title block (origin)
    tb_x = str(int(sheet_width) - 10 - 180)  # 180 according to DIN EN ISO 7200
    tb_y = str(int(sheet_height) - 10)

    #- Creates a group to move all elements in one step
    t = open(file_path, "a", encoding = "utf-8")
    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"titleblock\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "transform=\"translate(" + tb_x + "," + tb_y + ")\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + "<!-- Title block base point -->\n\n")
    #- title block
    t.write(loi + "<g id=\"titleblock-frame\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "style=\"fill:none;stroke:#000000;stroke-width:0.25;\
stroke-linecap:miter;stroke-miterlimit:4\">\n")
    loi = levelOfIndentation(6)
    t.write(loi + svgPath("  0","  0","  0","-63") + "\n")
    t.write(loi + svgPath("  0","-63","180","  0") + "\n")
    t.write(loi + svgPath("  0","-30","h","155") + "\n")
    t.write(loi + svgPath("155","  0","v","-63") + "\n")
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    #- texts
    t.write(loi + "<g id=\"titleblock-text-non-editable\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "style=\"font-family:osifont;font-size:5.0;\
fill:#000;text-anchor:start;\">\n")
    loi = levelOfIndentation(6)
    t.write(loi + svgText("  4.5","-43.5 ","Some static text") + "\n")
    t.write(loi + svgText("  4.5","-13.5 ","More static text") + "\n")
    t.write(loi + svgText("162.5","-3.5 ","Vertical static text","-90") + "\n")
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close

def createEditableText(file_path, sheet_width, sheet_height, ink = "#000"):
    """
    Calls external methods to create editable texts
    """
    #- Offsets from page origin to title block origin to calculate absolute
    #- coordinates for editable texts.
    #  (adds to relative coordinates from title block origin)
    edX = int(sheet_width) - 10 - 180 # 180 according to DIN EN ISO 7200
    edY = int(sheet_height) - 10

    t = open(file_path, "a", encoding="utf-8")

    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"titleblock-text-editable\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"font-family:osifont;font-size:7.0;fill:" + ink
        + ";text-anchor:start\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + ediText("EdiText-1",str(edX + 60),str(edY - 43.5),
        "Some editable text") + "\n"
        ) # Author
    t.write(loi + ediText("EdiText-2",str(edX + 60),str(edY - 13.5),
        "More editable text") + "\n"
        )
    t.write(loi + ediText("EdiText-3",str(edX + 173),str(edY - 4.5),
        "90° editable text","-90") + "\n"
        )
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close

def insertGroups(file_path, sheet_x, sheet_y, rows, ink):
    """
    Calls external methods to embed groups between the outer body tags.
    (<g>...</g> to set common attributes and transformations
    for grouped elements)
    """
    SvgToolkit.createFrame(file_path, sheet_x, sheet_y)
    #SvgToolkit.createDecoration(file_path, sheet_x, sheet_y, "-90")
    createTitleBlock(file_path, sheet_x, sheet_y)
    createEditableText(file_path, sheet_x, sheet_y, ink)
    return

def createTemplate(format, rows, ink):
    """
    Calls external methods to build head and outer body tags.
    (<svg>...</svg> to embed grouped elements)
    """
    size = SvgToolkit.sheetDimensions(format)
    sheet_x = size[0]
    sheet_y = size[1]
    SvgToolkit.createSvgFile(file_path)
    SvgToolkit.startSvg(file_path, sheet_x, sheet_y)
    insertGroups(file_path, sheet_x, sheet_y, rows, ink)
    SvgToolkit.endSvg(file_path)
    return

##########################################################################################################
# Gui code
##########################################################################################################

if SvgToolkit.isGuiLoaded():
    from FreeCAD import Gui

    ##########################################################################################################
    # View Provider
    ##########################################################################################################

    ##########################################################################################################
    # Task Panel
    ##########################################################################################################

    class TemplateTaskPanel():
        """
        Creates a task panel to edit template options.
        """
        def __init__(self):
            self.initUI()

        def initUI(self):
            # Sets some default values and places the widgets
            #- Get the language value from the FreeCAD parameters
            parameter_path = FreeCAD.ParamGet("User parameter:BaseApp" +
                "/Preferences/General")
            app_language = parameter_path.GetString("Language")

            #- Add a Box container to group widgets
            self.groupBox = QGroupBox("Tempate Properties")
            #- Add a grid to order widgets
            self.grid = QGridLayout() # instantiates a QGridLayout
            self.groupBox.setLayout(self.grid) # puts the grid inside the groupBox
            #- Add some labels to the grid
            self.label_ink = QLabel("Color of text entries")
            self.grid.addWidget(self.label_ink, 0, 0)
            self.label_warning = QLabel("Don't forget to save, close, and " +
                "reopen between different templates"
                )
            self.grid.addWidget(self.label_warning, 1, 0, 1, -1)

            #- Create some result containers and set default values
            self.result_ink = "#000"

            # Add some input widgets

            #- Set up a CheckBox - Ink
            self.checkBox_ink = QCheckBox("Ink-blue")
            self.checkBox_ink.setToolTip("Toggles the color of text entries" +
                "between black (default) and ink-blue")
            self.checkBox_ink.setChecked(False)
            self.checkBox_ink.stateChanged.connect(self.on_checkbox_changed)
            self.grid.addWidget(self.checkBox_ink, 0, 1)

            # Show the QGroupBox
            self.form = self.groupBox

        def on_checkbox_changed(self, value):
            '''Toggles the color of editable texts'''
            if value:
                self.result_ink = "#00d"
            else:
                self.result_ink = "#000"
            print(value, self.result_ink)

        def accept(self):
            '''
            This is triggered by the panel's OK button.
            But also prevents the closing of the panel
            '''
            #- Hard coded values for this wiki example
            rows = 0
            format = "ISO A3"
            # Collect results
            ink = self.result_ink
            FreeCADGui.Control.closeDialog()
            createTemplate(format, rows, ink)
            active_doc = getActiveDocument()
            if not active_doc:
                return
            #- Add a Page object to the active document and insert the template
            page = insertTemplate(active_doc, file_path)
            number_of_pages = page[0]
            new_page = page[1]
            # open the page object for editing
            active_doc.getObject(new_page).ViewObject.doubleClicked()

        def reject(self):
            '''
            This is triggered by the panel's Cancel button.
            But also prevents the closing of the panel
            '''
            FreeCADGui.Control.closeDialog()
            print("Cancel, es gibt nichts mehr zu tun")

    ##########################################################################################################
    # Command
    ##########################################################################################################

    class NewTemplateCommandClass():
        """Creates and inserts a new template"""

        def GetResources(self):
            return {
                "Pixmap": os.path.join(
                    icons_path, "Templater_NewTemplateWiki.svg"
                    ),  # the name of a svg file available in the resources
                "MenuText": "New Template Wiki",
                #"Accel": "W, T",
                "ToolTip":
                    "Creates and inserts a new template like described in the\n"
                    "TechDraw TemplateGenerator tutorial in the wiki\n\n"
                    "Just invoke this Command",
                }

        def Activated(self):
            panel = TemplateTaskPanel()
            FreeCADGui.Control.showDialog(panel)
            # Further steps are launched from the OK option of the panel
            return

        def Deactivated(self):
            """
            This function is executed whenever the workbench is deactivated
            """
            return

        def IsActive(self):
            return True

    Gui.addCommand("Templater_NewTemplateWiki", NewTemplateCommandClass())
