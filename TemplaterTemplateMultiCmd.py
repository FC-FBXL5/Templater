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
This script creates and inserts a TechDraw template into the active docoment.
Alternatively it only creates a frame inserts it and optionally adds
a titleblock symbol.
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
import os
import SvgToolkit
import TitleBlock_KG
from PySide import QtCore
from PySide.QtGui import (QAction, QGroupBox, QMessageBox, QPixmap)
from PySide.QtWidgets import (QGridLayout, QLabel, QComboBox,
    QDoubleSpinBox, QCheckBox, QRadioButton, QButtonGroup
    )

translate = FreeCAD.Qt.translate

icons_path = SvgToolkit.icons_path
mod_path = SvgToolkit.mod_path
file_path = os.path.join(mod_path, "Resources", "TemplateMulti.svg")
symbols_path = os.path.join(mod_path, "Resources", "symbols")

TITLE_BLOCKS = {
    "BM_1_min":os.path.join(symbols_path, "Titleblock_BM_1_minimal.svg"),
    "BM_2":os.path.join(symbols_path, "Titleblock_BM_2.svg"),
    "BM_3_adv":os.path.join(symbols_path, "Titleblock_BM_3_advanced.svg"),
    "BM_4":os.path.join(symbols_path, "Titleblock_BM_4.svg"),
    "BM_5_max":os.path.join(symbols_path, "Titleblock_BM_5_maximal.svg")
    }

def getActiveDocument():
    """
    Returns the active document or None
    """
    ado = FreeCAD.activeDocument()
    if ado is None:
        warning_text = translate("Templater", "There is no active document!")
        QMessageBox.warning(None, "", warning_text)
    return ado

def existingPages(document):
    """
    Counts existing pages in the active document
    """
    number_of_pages = 0
    for item in document.Objects:
        if item.Name.startswith("Page"):
        #if item.Name[:4] == "Page":
            number_of_pages += 1
    return number_of_pages

def insertSymbol(active_doc, work_page, format, symbol_path, symbol_height):
    """
    Inserts a symbol in the active document
    """
    #- Create the symbol as a document object
    sym = active_doc.addObject("TechDraw::DrawViewSymbol","TitleBlock")
    #- Load svg content into the symbol
    #symbol_name = "Titleblock_BM_1_minimal.svg"
    #symbol_path = os.path.join(mod_path, "Resources", "symbols", symbol_name)
    s = open(symbol_path, "r", encoding="utf-8")
    svg = s.read()
    s.close()
    sym.Symbol = svg
    #- insert the symbol into a page
    work_page.addView(sym)
    sym.Owner = work_page
    # Its bounding box center is placed at the lower left corner of the page
    sheet_size = SvgToolkit.sheetDimensions(format)
    sheet_x = sheet_size[0]
    sheet_y = sheet_size[1]
    title_x = 180
    title_y = symbol_height
    #- Symbol center offsets from lower left corner
    sym.X = float(sheet_x) - 10 - (title_x / 2)
    sym.Y = 10 + title_y /2

    work_page.ViewObject.doubleClicked()

    return

def insertTemplate(format, symbol, symbol_path, symbol_height):
    """
    Inserts a page and a template in the active document
    """
    active_doc = getActiveDocument()
    if not active_doc:
        return
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
    new_template = ("Template" + next)
    # add a page object to the active document
    page_object = active_doc.addObject("TechDraw::DrawPage", new_page)
    # add a template object to the active document
    active_doc.addObject("TechDraw::DrawSVGTemplate", new_template)
    # load the svg template into the template object
    active_doc.getObject(new_template).Template = file_path
    # add the template object to the page's object list
    active_doc.getObject(new_page).Template = active_doc.getObject(new_template)
    # At this point the document received a new page with a new template

    if symbol:
        insertSymbol(
            active_doc, page_object, format, symbol_path, symbol_height
            )
        # edit symbol text entries
        return
    # edit template text entries

    # open the page object for editing
    active_doc.getObject(new_page).ViewObject.doubleClicked()

    result = [page_mumber, new_page]
    return result

def insertGroups(
    format,
    sheet_size,
    indices,
    tilt,
    title_block,
    ink,
    bom_rows
    ):
    """
    Calls external methods to embed groups between the outer body tags.
    (<g>...</g> to set common attributes and transformations
    for grouped elements)
    """
    sheet_x = sheet_size[0]
    sheet_y = sheet_size[1]
    #- Drawing area offsets according to ISO 7200, might need a switch
    #  to comply to US standards
    da_top    = 10
    da_bottom = 10
    da_left   = 20
    da_right  = 10
    da_offsets = (da_top, da_bottom, da_left, da_right)
    #- Index frame offsets according to ISO 7200, might need a switch
    #  to comply to US standards
    if_top    = 5
    if_bottom = 5
    if_left   = 5
    if_right  = 5
    if_offsets = (if_top, if_bottom, if_left, if_right)
    SvgToolkit.createFrames(file_path, sheet_size, da_offsets, if_offsets)
    if indices:
        if tilt:
            SvgToolkit.createDecorations(
                file_path, sheet_size, da_offsets, if_offsets, "-90"
                )
        else:
            SvgToolkit.createDecorations(
                file_path, sheet_size, da_offsets, if_offsets
                )
    if title_block:
        tb_offsets = TitleBlock_KG.createTitleBlock(
            file_path, sheet_size, da_offsets
            )
        TitleBlock_KG.createEditableText(file_path, sheet_x, sheet_y, ink)
        logo_position = tb_offsets[0]
        proj_symb_position = tb_offsets[1]
        Title_block_height = tb_offsets[2]
        SvgToolkit.createFreecadLogo(file_path, logo_position)
        SvgToolkit.createProjectionSymbol(file_path, proj_symb_position)
        if bom_rows == 0:
            return
        TitleBlock_KG.createBOMLines(file_path, sheet_x, sheet_y, bom_rows, ink)
    return

def createTemplate(
    format,
    frame,
    indices,
    tilt,
    title_block,
    ink,
    bom_rows
    ):
    """
    Calls external methods to build head and outer body tags.
    (<svg>...</svg> to embed grouped elements)
    The result is an empty sheet for other than technical drafting purposes.
    """
    sheet_size = SvgToolkit.sheetDimensions(format)
    sheet_x = sheet_size[0]
    sheet_y = sheet_size[1]
    SvgToolkit.createSvgFile(file_path)
    SvgToolkit.startSvg(file_path, sheet_x, sheet_y)
    if frame:
        insertGroups(
            format,
            sheet_size,
            indices,
            tilt,
            title_block,
            ink,
            bom_rows
            )
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
    Creates a task panel to select template options.
    """
    def __init__(self):
        self.initUI()

    def initUI(self):
        """Sets some default values and places the widgets"""

        self.setWindowTexts()

        #- Add a Box container to group widgets
        self.groupBox = QGroupBox(self.text_panel)
        #- Add a grid to order widgets
        self.grid = QGridLayout() # instantiates a QGridLayout
        self.groupBox.setLayout(self.grid) # puts the grid inside the groupBox
        #- Add some labels to the grid
        self.label_format = QLabel(self.text_format)
        self.grid.addWidget(self.label_format, 0, 0)
        self.label_frame = QLabel(self.text_frame)
        self.grid.addWidget(self.label_frame, 1, 0)
        self.label_indices = QLabel(self.text_indices)
        self.grid.addWidget(self.label_indices, 2, 0)
        self.label_tilt = QLabel(self.text_tilt)
        self.grid.addWidget(self.label_tilt, 3, 0)
        self.label_title_block = QLabel(self.text_title_block)
        self.grid.addWidget(self.label_title_block, 4, 0)
        self.label_ink = QLabel(self.text_ink)
        self.grid.addWidget(self.label_ink, 5, 0)
        self.label_BOM_rows = QLabel(self.text_bom)
        self.grid.addWidget(self.label_BOM_rows, 6, 0)
        self.label_page = QLabel(self.text_page)
        self.grid.addWidget(self.label_page, 7, 0)
        self.label_symbol = QLabel(self.text_symbol)
        self.label_symbol.hide()
        self.grid.addWidget(self.label_symbol, 8, 0)

        self.label_warning = QLabel(self.text_warning)
        self.grid.addWidget(self.label_warning, 20, 0, 1, -1)

        #- Create some result containers and set default values
        self.result_button = "BM_1_min"
        self.result_format = "ISO A4"
        self.result_ink = "#000"

        # Add some input widgets

        #- Set up a ComboBox - Format
        self.coBox_format = QComboBox()
        format_list = ("ISO A0","ISO A1","ISO A2","ISO A3","ISO A4",\
            "ISO A4-","ANSI A","ANSI B","ANSI C","ANSI D","ANSI E",\
            "Arch A","Arch B","Arch C","Arch D","Arch E","Arch E1"
            )
        self.coBox_format.setToolTip(self.tooltip_format)
        self.coBox_format.addItems(format_list)
        self.coBox_format.setCurrentIndex(format_list.index("ISO A4"))
        self.coBox_format.currentTextChanged.connect(self.onCoBoxFormat)
        self.grid.addWidget(self.coBox_format, 0, 1)

        #- Set up a CheckBox - Frame
        self.checkBox_frame = QCheckBox(self.label_cb_frame)
        self.checkBox_frame.setToolTip(self.tooltip_frame)
        self.checkBox_frame.setChecked(True)
        self.checkBox_frame.stateChanged.connect(
            self.on_checkbox_frame_changed
            )
        self.grid.addWidget(self.checkBox_frame, 1, 1)

        #- Set up a CheckBox - Indices
        self.checkBox_indices = QCheckBox(self.label_cb_indices)
        self.checkBox_indices.setToolTip(self.tooltip_indices)
        self.checkBox_indices.setChecked(True)
        self.checkBox_indices.stateChanged.connect(
            self.on_checkbox_indices_changed
            )
        self.grid.addWidget(self.checkBox_indices, 2, 1)

        #- Set up a CheckBox - Tilt indices
        self.checkBox_tilt = QCheckBox(self.label_cb_tilt)
        self.checkBox_tilt.setToolTip(self.tooltip_tilt)
        self.checkBox_tilt.setChecked(True)
        self.checkBox_tilt.stateChanged.connect(
            self.on_checkbox_tilt_changed
            )
        self.grid.addWidget(self.checkBox_tilt, 3, 1)

        #- Set up a CheckBox - TitleBlock
        self.checkBox_title_block = QCheckBox(self.label_cb_title_block)
        self.checkBox_title_block.setToolTip(self.tooltip_title_block)
        self.checkBox_title_block.setChecked(True)
        self.checkBox_title_block.stateChanged.connect(
            self.on_checkbox_title_block_changed
            )
        self.grid.addWidget(self.checkBox_title_block, 4, 1)

        #- Set up a CheckBox - Ink
        self.checkBox_ink = QCheckBox(self.label_cb_ink)
        self.checkBox_ink.setToolTip(self.tooltip_ink)
        self.checkBox_ink.setChecked(False)
        self.checkBox_ink.stateChanged.connect(self.on_checkbox_ink_changed)
        self.grid.addWidget(self.checkBox_ink, 5, 1)

        #- Set up a DoubleSpinBox - Number of BOM rows
        self.dsBox_BOM_rows = QDoubleSpinBox()
        self.dsBox_BOM_rows.setToolTip(self.tooltip_bom)
        self.dsBox_BOM_rows.setMinimum(0)
        self.dsBox_BOM_rows.setMaximum(34) # default value for ISO A4
        self.dsBox_BOM_rows.setDecimals(0) # no decimals
        self.dsBox_BOM_rows.setValue(0)    # no BOM as default
        self.grid.addWidget(self.dsBox_BOM_rows, 6, 1)
        # Set contextual menu options for the DoubleSpinBox
        #- Reset text field to default value (0)
        self.BOM_action1 = QAction()
        self.BOM_action1.setText(self.text_none)
        self.BOM_action1.triggered.connect(self.onBOMAction1)
        #- Set text field to maximum value
        self.BOM_action2 = QAction()
        self.BOM_action2.setText(self.text_maximum)
        self.BOM_action2.triggered.connect(self.onBOMAction2)
        #- Define RMB-menu and add options
        self.dsBox_BOM_rows.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.dsBox_BOM_rows.addAction(self.BOM_action1)
        self.dsBox_BOM_rows.addAction(self.BOM_action2)

        #- Set up a CheckBox - Page
        self.checkBox_page = QCheckBox(self.label_cb_page)
        self.checkBox_page.setToolTip(self.tooltip_page)
        self.checkBox_page.setChecked(True)
        self.checkBox_page.stateChanged.connect(self.on_checkbox_page_changed)
        self.grid.addWidget(self.checkBox_page, 7, 1)

        #- Set up a CheckBox - Symbol
        self.checkBox_symbol = QCheckBox(self.label_cb_symbol)
        self.checkBox_symbol.setToolTip(self.tooltip_symbol)
        self.checkBox_symbol.setChecked(False)
        self.checkBox_symbol.hide()
        self.checkBox_symbol.stateChanged.connect(self.on_checkbox_symbol_changed)
        self.grid.addWidget(self.checkBox_symbol, 8, 1)

        #- Set up radio buttons - Title blocks
        self.radio_button_BM_1 = QRadioButton("BM_1_min")
        self.radio_button_BM_1.setToolTip(self.tool_tip_buttons)
        self.radio_button_BM_1.setChecked(True)
        self.radio_button_BM_1.hide()
        self.radio_button_BM_1.toggled.connect(
            self.on_radio_button_toggled
            )
        self.grid.addWidget(self.radio_button_BM_1, 9, 0)

        self.radio_button_BM_2 = QRadioButton("BM_2")
        self.radio_button_BM_2.setToolTip(self.tool_tip_buttons)
        self.radio_button_BM_2.setChecked(False)
        self.radio_button_BM_2.hide()
        self.radio_button_BM_2.toggled.connect(
            self.on_radio_button_toggled
            )
        self.grid.addWidget(self.radio_button_BM_2, 10, 0)

        self.radio_button_BM_3 = QRadioButton("BM_3_adv")
        self.radio_button_BM_3.setToolTip(self.tool_tip_buttons)
        self.radio_button_BM_3.setChecked(False)
        self.radio_button_BM_3.hide()
        self.radio_button_BM_3.toggled.connect(
            self.on_radio_button_toggled
            )
        self.grid.addWidget(self.radio_button_BM_3, 11, 0)

        self.radio_button_BM_4 = QRadioButton("BM_4")
        self.radio_button_BM_4.setToolTip(self.tool_tip_buttons)
        self.radio_button_BM_4.setChecked(False)
        self.radio_button_BM_4.hide()
        self.radio_button_BM_4.toggled.connect(
            self.on_radio_button_toggled
            )
        self.grid.addWidget(self.radio_button_BM_4, 12, 0)

        self.radio_button_BM_5 = QRadioButton("BM_5_max")
        self.radio_button_BM_5.setToolTip(self.tool_tip_buttons)
        self.radio_button_BM_5.setChecked(False)
        self.radio_button_BM_5.hide()
        self.radio_button_BM_5.toggled.connect(
            self.on_radio_button_toggled
            )
        self.grid.addWidget(self.radio_button_BM_5, 13, 0)

        # Group the buttons
        self.group = QButtonGroup()
        self.group.addButton(self.radio_button_BM_1)
        self.group.addButton(self.radio_button_BM_2)
        self.group.addButton(self.radio_button_BM_3)
        self.group.addButton(self.radio_button_BM_4)
        self.group.addButton(self.radio_button_BM_5)

        self.label_image = QLabel()
        self.image_path = TITLE_BLOCKS["BM_1_min"]
        image = QPixmap(self.image_path)
        # only geometry within the ViewBox will be shown in a QPixmap
        self.label_image.setPixmap(image)
        self.label_image.setScaledContents(True) #(False)
        self.label_image.setFixedSize(400, 75)
        self.label_image.hide()
        self.Symbol_size = (180, 36)
        self.grid.addWidget(self.label_image, 19, 0, 1, -1)

        # Show the QGroupBox
        self.form = self.groupBox

    def setWindowTexts(self):

        self.text_panel       = translate("Templater", "Template settings")
        self.text_format      = translate("Templater",
            "Select the desired \n"
            "sheet format",
            )
        self.text_frame       = translate("Templater",
            "Does the drawing need a Frame?",
            )
        self.text_indices     = translate("Templater",
            "Does the frame require zone indices?",
            )
        self.text_tilt        = translate("Templater",
            "Should the upper and right indices be tilted?",
            )
        self.text_title_block = translate("Templater",
            "Should the template integrate a title block?"
            )
        self.text_ink         = translate("Templater",
            "Do text entries require a different color?"
            )
        self.text_bom         = translate("Templater",
            "Enter the number of rows if the template \n"
            "requires a bill of material?"
            )
        self.text_page        = translate("Templater",
            "Should the created template be inserted in \n"
            "the active document to add a new page?"
            )
        self.text_symbol      = translate("Templater",
            "Should a symbol containing a title block \n"
            "be added to the new page?"
            )
        self.text_warning     = translate("Templater",
            "Don't forget to save, close and reopen the file \n"
            "before insering another template!"
            )
        self.tooltip_format   = translate("Templater",
            "Selects a sheet format for the new page and\n"
            "resets the number of BOM rows to 0, if changed"
            )
        self.label_cb_frame   = translate("Templater","Draw a Frame")
        self.tooltip_frame    = translate("Templater",
            "Adds a frame to the new page"
            )
        self.label_cb_indices = translate("Templater","Place zone indices")
        self.tooltip_indices  = translate("Templater",
            "Adds zone indices and separators to the frame"
            )
        self.label_cb_tilt    = translate("Templater","Tilt indices 90° ccw")
        self.tooltip_tilt     = translate("Templater",
            "Tilts upper and right indices to be readable from the right"
            )
        self.label_cb_title_block = translate("Templater","Add a title block")
        self.tooltip_title_block  = translate("Templater",
            "Adds a titleblock with some editable texts to the new page"
            )
        self.label_cb_ink     = translate("Templater","Change to ink-blue")
        self.tooltip_ink      = translate("Templater",
            "Colors editable texts in ink-blue"
            )
        self.tooltip_bom      = translate("Templater",
            "Enter the number \n"
            "of BOM rows or use \n"
            "right mouse buton \n"
            "to select \"None\" or \n\"Maximum\""
            )
        self.text_none        = translate("Templater", "None")
        self.text_default     = translate("Templater", "Standard (2)")
        self.text_maximum     = translate("Templater", "Maximum")
        self.label_cb_page    = translate("Templater","Insert template")
        self.tooltip_page     = translate("Templater",
            "Inserts the saved template into the active document \n"
            "to create a new page"
            )
        self.label_cb_symbol  = translate("Templater",
            "Insert title block symbol"
            )
        self.tooltip_symbol   = translate("Templater",
            "Inserts a title block as a symbols into the new page"
            )
        self.tool_tip_buttons = translate("Templater",
            "Selects a template coded after one of Benjamin May's proposals"
            )
        self.text_cancel      = translate("Templater", "Cancel")
        self.text_ok          = translate("Templater", "OK")

    def onBOMAction1(self):
        # Resets the number of BOM rows to 0
        self.dsBox_BOM_rows.setValue(0)

    def onBOMAction2(self):
        # Sets the number of BOM rows to maximum
        self.dsBox_BOM_rows.setValue(self.dsBox_BOM_rows.maximum())

    def onCoBoxFormat(self, selected_text):
        # Sets the format result and the number of BOM rows
        self.result_format = selected_text
        format_dict = {"ISO A0":125, "ISO A1":83, "ISO A2":54,
            "ISO A3":34, "ISO A4":34, "ISO A4-":18, "ANSI A":31,
            "ANSI B":31, "ANSI C":56, "ANSI D":78, "ANSI E":128,
            "Arch A":35, "Arch B":35, "Arch C":61, "Arch D":86,
            "Arch E":137, "Arch E1":111}
        max_row = format_dict[selected_text]
        self.dsBox_BOM_rows.setMaximum(max_row) # max. value for selected format
        self.dsBox_BOM_rows.setValue(0)         # reset default value

    def on_checkbox_frame_changed(self, value):
        """Hides following options if no frame is needed (empty page)"""
        if value:
            self.label_indices.show()
            self.checkBox_indices.show()
            self.label_tilt.show()
            self.checkBox_tilt.show()
            self.label_title_block.show()
            self.checkBox_title_block.show()
            self.label_ink.show()
            self.checkBox_ink.show()
            self.label_BOM_rows.show()
            self.dsBox_BOM_rows.show()
            self.label_page.show()
            self.checkBox_page.show()
            self.result_frame = True
        else:
            self.label_indices.hide()
            self.checkBox_indices.hide()
            self.label_tilt.hide()
            self.checkBox_tilt.hide()
            self.label_title_block.hide()
            self.checkBox_title_block.hide()
            self.label_ink.hide()
            self.checkBox_ink.hide()
            self.label_BOM_rows.hide()
            self.dsBox_BOM_rows.hide()
            self.label_page.hide()
            self.checkBox_page.hide()
            self.result_ink = False

    def on_checkbox_indices_changed(self, value):
        """Hides the tilt option if no zone indices are needed"""
        if value:
            self.label_tilt.show()
            self.checkBox_tilt.show()
            self.result_indices = True
        else:
            self.label_tilt.hide()
            self.checkBox_tilt.hide()
            self.result_indices = False

    def on_checkbox_tilt_changed(self, value):
        """Toggles the tilt value"""
        if value:
            self.result_tilt = True
        else:
            self.result_tilt = False

    def on_checkbox_title_block_changed(self, value):
        """Hides ink and BOM options if no title block will be integrated"""
        if value:
            self.label_ink.show()
            self.checkBox_ink.show()
            self.label_BOM_rows.show()
            self.dsBox_BOM_rows.show()
            self.label_symbol.hide()
            self.checkBox_symbol.hide()
            self.checkBox_symbol.setChecked(False)
            self.radio_button_BM_1.hide()
            self.radio_button_BM_2.hide()
            self.radio_button_BM_3.hide()
            self.radio_button_BM_4.hide()
            self.radio_button_BM_5.hide()
            self.label_image.hide()
            self.result_title_block = True
        else:
            self.label_ink.hide()
            self.checkBox_ink.hide()
            self.label_BOM_rows.hide()
            self.dsBox_BOM_rows.hide()
            self.label_symbol.show()
            self.checkBox_symbol.show()
            self.result_title_block = False

    def on_checkbox_ink_changed(self, value):
        """Toggles the color of the editable text entries"""
        if value:
            self.result_ink = "#00d"
        else:
            self.result_ink = "#000"

    def on_checkbox_page_changed(self, value):
        """Toggles if the created temlate will be inserted to create a page"""
        if value:
            self.result_page = True
        else:
            self.result_page = False

    def on_checkbox_symbol_changed(self, value):
        """Toggles if a symbol will be inserted into the created page"""
        if value:
            self.radio_button_BM_1.show()
            self.radio_button_BM_2.show()
            self.radio_button_BM_3.show()
            self.radio_button_BM_4.show()
            self.radio_button_BM_5.show()
            self.label_image.show()
            self.result_symbol = True
        else:
            self.radio_button_BM_1.hide()
            self.radio_button_BM_2.hide()
            self.radio_button_BM_3.hide()
            self.radio_button_BM_4.hide()
            self.radio_button_BM_5.hide()
            self.label_image.hide()
            self.result_symbol = False

    def on_radio_button_toggled(self):
        """Selects the title block symbol to be inserted"""
        # get the radio button that sent the signal
        for button in self.group.buttons():
            if button.isChecked():
                self.image_path = TITLE_BLOCKS[button.text()]
                image = QPixmap(self.image_path)
                self.label_image.setPixmap(image)
                self.result_button = button.text()
                if button.text().startswith("BM_1"):
                    self.label_image.setFixedSize(400, 75)
                    self.Symbol_size = (180, 36)
                elif button.text().startswith("BM_2"):
                    self.label_image.setFixedSize(400, 75)
                    self.Symbol_size = (180, 36)
                elif button.text().startswith("BM_5"):
                    self.label_image.setFixedSize(400, 125)
                    self.Symbol_size = (180, 60)
                else:
                    self.label_image.setFixedSize(400, 100)
                    self.Symbol_size = (180, 48)
            #print( button.text())
        return

    def accept(self):
        """
        This is triggered by the panel's OK button.
        """
        #- Close the dialog (variables will stay accessible)
        FreeCADGui.Control.closeDialog()
        #- Launch template creation and hand over values
        createTemplate(
            self.result_format,
            self.checkBox_frame.isChecked(),
            self.checkBox_indices.isChecked(),
            self.checkBox_tilt.isChecked(),
            self.checkBox_title_block.isChecked(),
            self.result_ink,
            self.dsBox_BOM_rows.value()
            )
        #- launch the integration of the template into the document
        if self.checkBox_page.isChecked():
            format = self.result_format  # For annotation purposes
            symbol = self.checkBox_symbol.isChecked()
            symbol_path = self.image_path  # to the selected title block
            symbol_height = self.Symbol_size[1]
            insertTemplate(format, symbol, symbol_path, symbol_height)
        return

    def reject(self):
        '''
        This is triggered by the panel's Cancel button.
        But also prevents the closing of the panel
        '''
        FreeCADGui.Control.closeDialog()

    ##########################################################################################################
    # Command
    ##########################################################################################################

    class NewTemplateCommandClass():
        """Creates and inserts a new template"""

        def GetResources(self):
            return {
                "Pixmap": os.path.join(
                    icons_path, "Templater_NewTemplateMulti.svg"
                    ),  # the name of an svg file available in the resources
                "MenuText": translate("Templater", "New Template Multi"),
                #"Accel": "W, T",
                "ToolTip": translate(
                    "Templater",
                    "Creates and inserts a new template\n"
                    "in the active document",
                    ),
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

    Gui.addCommand("Templater_NewTemplateMulti", NewTemplateCommandClass())
