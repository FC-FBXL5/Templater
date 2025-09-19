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
"""
This Tool creates an auxiliary view
from 2 points or one edge selected in a base view
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
import os    # built-in modules
import math  # to use some predefined conversions
import SvgToolkit
from TechDrawTools import TDToolsUtil
from PySide import QtCore
from PySide.QtGui import QGroupBox
from PySide.QtWidgets import (QGridLayout, QLabel, QCheckBox, QLineEdit)

translate = FreeCAD.Qt.translate

icons_path = SvgToolkit.icons_path
symbols_path = SvgToolkit.symbols_path

class TaskAuxView():
    """Provides the TechDraw AuxView Task Dialog"""
    def __init__(self, new_view, new_symbol, dir_tag, view_tag):

        self.view = new_view
        self.symbol = new_symbol
        self.dir_tag = dir_tag
        self.view_tag = view_tag

        self.setWindowTexts()

        #- Add a Box container to group widgets
        self.groupBox = QGroupBox(self.text_panel)
        #- Add a grid to order widgets
        self.grid = QGridLayout() # instantiates a QGridLayout
        self.groupBox.setLayout(self.grid) # puts the grid inside the groupBox

        #- Add some labels to the grid
        self.label_marker = QLabel(self.text_marker)
        self.grid.addWidget(self.label_marker, 0, 0)
        self.label_direction = QLabel(self.text_direction)
        self.grid.addWidget(self.label_direction, 1, 0)

        #- Set up a LineEdit - Marker
        self.lineEdit_marker = QLineEdit()
        self.lineEdit_marker.setToolTip(self.tooltip_marker)
        self.lineEdit_marker.setText("X")
        self.lineEdit_marker.textChanged.connect(self.onLineEditMarker)
        self.grid.addWidget(self.lineEdit_marker, 0, 1)

        #- Set up a CheckBox - Reverse
        self.checkBox_reverse = QCheckBox(self.text_reverse)
        self.checkBox_reverse.setToolTip(self.tooltip_reverse)
        self.checkBox_reverse.setChecked(False)
        self.checkBox_reverse.stateChanged.connect(
            self.onCheckboxReverseChanged
            )
        self.grid.addWidget(self.checkBox_reverse, 1, 1)

        #- Set up a CheckBox - Along
        self.checkBox_along = QCheckBox(self.text_along)
        self.checkBox_along.setToolTip(self.tooltip_along)
        self.checkBox_along.setChecked(False)
        self.checkBox_along.stateChanged.connect(
            self.onCheckboxAlongChanged
            )
        self.grid.addWidget(self.checkBox_along, 2, 1)

        #- Show the QGroupBox
        self.form = self.groupBox

    def setWindowTexts(self):
        """Supplies default texts or translations if available"""
        self.text_panel     = translate("Templater",
            "Auxiliary view settings"
            )
        self.text_marker    = translate("Templater",
            "Marker of the auxiliary view: "
            )
        self.text_direction = translate("Templater", "Direction: ")
        self.text_reverse   = translate("Templater", "Reverse direction")
        self.text_along     = translate("Templater", "Along edge")

        self.tooltip_marker  = translate("Templater",
            "Sets the view marker"
            )
        self.tooltip_reverse = translate("Templater",
            "Reverses the view direction"
            )
        self.tooltip_along = translate("Templater",
            "If checked the line of sight will be aligned with the edge \n"
            "instead of being perpendicular to it"
            )

    def on_lineEdit_marker(self, value):
        """Renames the view markers"""
        self.dir_tag.Text = value
        self.view_tag.Text = ("AuxView " + value)

    def onCheckboxReverseChanged(self, value):
        """Reverses the direction and the view arrow"""
        self.reverseDirection()
        self.reverseArrow()

    def onCheckboxAlongChanged(self, value):
        """Reverses the direction and the view arrow"""
        if value:
            self.alignDirection(90)
            self.alignArrow(90)
        else:
            self.alignDirection(-90)
            self.alignArrow(-90)

    def reverseArrow(self):
        """2D - Reverses the view arrow"""
        angle = float(self.symbol.Rotation)
        if angle >180:
            angle -= 180
        else:
            angle += 180
        self.symbol.Rotation = angle

    def alignArrow(self, align_angle):
        """2D - Aligns the view arrow by turning it 90°"""
        angle = float(self.symbol.Rotation)
        if align_angle > 0:
            if angle < 270:
                angle += 90
            else:
                angle -= 270
        else:
            if angle < 90:
                angle += 270
            else:
                angle -= 90

        self.symbol.Rotation = angle

    def rotateVector(self, direction_vector, axis_vector, align_angle = 180):
        """
        3D - Rotates a direction vector around an axis vector.
        Default reverses direction.
        Returns the new direction.
        """
        #- Create rotation
        # Remember: angle input in float (for degrees), stored in rad
        vector_rotation = FreeCAD.Rotation(axis_vector, align_angle)
        #- Apply rotation
        return vector_rotation.multVec(direction_vector)

    def reverseDirection(self):
        """3D - Reverses the view direction"""
        #- Rotate the view around its x axis:
        self.view.Direction = self.rotateVector(
            self.view.Direction,
            self.view.XDirection
            )
        Gui.runCommand("TechDraw_RedrawPage",0)

    def alignDirection(self, align_angle):
        """
        3D - Changes the alignment of the view direction (line of sight).
        A positive align_angle value (90) changes from perpendicular (default)
        to parallel while a negative value (-90) reverts to perpendicular.
        The checkbox logic allows only one step forward and one back again.
        """
        #- Tilt back the view around its x axis:
        self.view.Direction = self.rotateVector(
            self.view.Direction,
            self.view.XDirection,
            align_angle
            )
        #- Turn the view around the base view's z axis:
        self.view.XDirection = self.rotateVector(
            self.view.XDirection,
            self.view.BaseView.Direction,
            (align_angle * -1)
            )
        #- Tilt the view to its new alignment:
        self.view.Direction = self.rotateVector(
            self.view.Direction,
            self.view.XDirection,
            align_angle
            )
        #- Adapt the rotation of the view according to the page
        self.view.Rotation = float(self.view.Rotation) + (align_angle * -1)
        Gui.runCommand("TechDraw_RedrawPage",0)

    def accept(self):
        """slot: OK pressed"""
        Gui.Control.closeDialog()

    def reject(self):
        return True

def getActiveDocument():
    """Returns the active document or sends a message"""
    ado = FreeCAD.activeDocument()
    if ado is not None:
        return ado
    message = translate("Templater", "No active document available!")
    TDToolsUtil.displayMessage("AuxView", message)
    return False

def getPageOfSelection(doc, b_view):
    """Retrieves the Page that holds the selected elements"""
    #- Find an object starting with 'Page' that contains the selected object
    for each in doc.Objects:
        if each.Name.startswith("Page"):
            for item in each.OutList: # Search items belonging to a Page object
                if item.Name.startswith("ProjGroup"): # Look into projection groups
                    for view in item.OutList: # Search views belonging to a ProjGroup object
                        if view.Name == b_view.Name:
                            return each
                else:
                    if item.Name == b_view.Name:
                        return each
    return False

def getCcwAngle(vertex1,vertex2,view_rotation):
    """
    Creates 3D vectors to calculate the 2D angle towards the x direction of the
    base view which is parallel to the page view's x direction.
    The direction of the XDirection property is not parallel to the view's
    x direction if the view is rotated! This angle also has to be taken into
    account to calculate the 3D angle
    """
    #- Extract position vectors from the points
    vector_start = FreeCAD.Vector(vertex1.X, vertex1.Y, vertex1.Z)
    vector_end   = FreeCAD.Vector(vertex2.X, vertex2.Y, vertex2.Z)
    #- Calculate the 2D Direction vector from start vertex to end vertex
    # on the XY plane of the base view/work page (z = 0)
    direction = vector_end.sub(vector_start)
    x_direction = FreeCAD.Vector(1, 0, 0)
    angle_x = math.degrees(direction.getAngle(x_direction))
    # getAngle() returns positive (absolute) values only (in rad)
    # -> convert to degrees and check orientation
    if vertex1.Y > vertex2.Y:
        angle_x *= -1  # switches angle orientation
    #- Turn back the base view rotation
    # angle_x is a float value now but view_rotation is deg
    angle_x -= float(view_rotation)
    return angle_x

def symbolAngle(vertex1,vertex2):
    """
    Creates 3D vectors to calculate the 2D angle towards the
    x direction of the base view
    """
    #- Extract position vectors from the points
    vector_start = FreeCAD.Vector(vertex1.X, vertex1.Y, vertex1.Z)
    vector_end   = FreeCAD.Vector(vertex2.X, vertex2.Y, vertex2.Z)
    #- Calculate the 2D Direction vector from start vertex to end vertex
    # on the XY plane of the base view/work page (z = 0)
    direction = vector_end.sub(vector_start)
    y_direction = FreeCAD.Vector(0, -1, 0)
    angle_y = math.degrees(direction.getAngle(y_direction))
    # getAngle() returns positive (absolute) values only (in rad)
    # -> convert to degrees and check orientation
    if vertex1.X > vertex2.X:
        angle_y *= -1  # switches angle orientation
    return angle_y

def mainSection():
    """
    The main section, no more, no less
    """
    # Operations are performed in the active document of the application
    #- Retrieve the active document
    active_doc = getActiveDocument()
    if not active_doc:  # (active_doc is None/False)
        return
    #- Retrieve the selection view
    if TDToolsUtil.getSelView():
        base_view = TDToolsUtil.getSelView()
    else:
        return
    #- Retrieve the selected edge or vertices
    if TDToolsUtil.getSelEdges(0):
        edges = TDToolsUtil.getSelEdges(0)
        edge = edges[0]
        vertices = edge.Vertexes
    elif TDToolsUtil.getSelVertexes(2):
        vertices = TDToolsUtil.getSelVertexes(2)  # required number of vertices
    else:
        return
    #- Retrieve the page that holds the view
    work_page = getPageOfSelection(active_doc, base_view)
    #- To see changes immediately
    work_page.KeepUpdated = True
    # At this point the input elements are gathered:
    #  active_doc, work_page, base_view, and vertices

    #- Create a new view
    new_view = active_doc.addObject("TechDraw::DrawViewPart", "AuxView")
    #- Add the new view to the page
    work_page.addView(new_view)
    #- Add a BaseView property to the new view and link the BaseView object
    #  to the BaseView property in one step
    new_view.addProperty("App::PropertyLink", "BaseView", "AuxView",
        "Base view of this auxiliary view"
        ).BaseView = active_doc.getObject(base_view.Name)
    #- Hand over the source objects
    new_view.Source = new_view.BaseView.Source

    #- 2D: Calculate the ccw angle between the x axes of base view and new view
    turn_ccw = getCcwAngle(vertices[0],vertices[1],new_view.BaseView.Rotation)
    # Returns a float value representing degrees

    # 3D: Turn base_view.XDirection around base_view.Direction to get
    #     new_view.XDirection
    #- Create a rotation, angle input in float (for degrees), stored in rad
    around_direction = FreeCAD.Rotation(new_view.BaseView.Direction, turn_ccw)
    #- Apply rotation to the base_view.XDirection
    new_view.XDirection = around_direction.multVec(new_view.BaseView.XDirection)
    #- The cross-product of base view Z and new view X
    #  gives new view Z direction
    new_view.Direction = new_view.BaseView.Direction.cross(new_view.XDirection)

    # 2D: Take base_view.Rotation into account, it has to be converted
    #     to float since it is stored in deg
    #- Add the rotation of the base view to the angle between the x axes
    new_view.Rotation = turn_ccw + float(new_view.BaseView.Rotation)
    # At this point the Auxiliary View is complete

    #- Retrieve the view arrow
    arrow_path = os.path.join(symbols_path, "ViewArrow.svg")
    s = open(arrow_path, "r", encoding="utf-8")
    svg = s.read()
    s.close()

    #- Create an arrow symbol
    new_symbol = active_doc.addObject('TechDraw::DrawViewSymbol', 'ViewArrow')
    new_symbol.Symbol = svg
    new_symbol.Owner = base_view
    new_symbol.Rotation = symbolAngle(vertices[0],vertices[1])
    #- Add the new symbol to the page
    work_page.addView(new_symbol)
    #- Create a direction tag
    dir_tag = active_doc.addObject('TechDraw::DrawViewAnnotation', 'AuxMarker')
    dir_tag.Text = "X"
    dir_tag.Owner = new_symbol
    #- Add the new symbol to the page
    work_page.addView(dir_tag)

    #- Create a direction tag
    view_tag = active_doc.addObject('TechDraw::DrawViewAnnotation', 'AuxHeader')
    view_tag.Text = ["AuxView X"]
    view_tag.Owner = new_view
    #- Add the new symbol to the page
    work_page.addView(view_tag)

    Gui.runCommand("TechDraw_RedrawPage",0)

    panel = TaskAuxView(new_view, new_symbol, dir_tag, view_tag)
    Gui.Control.showDialog(panel)

    Gui.runCommand("TechDraw_RedrawPage",0)
    #- To no longer see changes immediately
    work_page.KeepUpdated = False

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

    ##########################################################################################################
    # Command
    ##########################################################################################################

    class AuxViewCommandClass():
        """
        Creates an auxiliary view from two vertices selected individually
        or from the end vertices of a selected edge
        """ 

        def GetResources(self):
            return {
                "Pixmap": os.path.join(
                    icons_path, "Templater_AuxView.svg"
                ),  # the name of an svg file available in the resources
                "MenuText": QT_TRANSLATE_NOOP("Templater_AuxView",
                    "Auxiliary view"
                    ),
                #"Accel": "S, H",
                "ToolTip": QT_TRANSLATE_NOOP("Templater_AuxView",
                    "Creates an auxiliary view\n"
                    "1. Select 2 vertices or 1 edge.\n"
                    "2. Invoke this Command",
                    )
                }

        def Activated(self):
            mainSection()
            return

        def IsActive(self):
            return True

    Gui.addCommand("Templater_AuxView", AuxViewCommandClass())
