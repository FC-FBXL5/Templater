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
"""This Makro creates an auxiliary view from 2 points in a base view"""


"""
I have tried to follow this naming rule:
 class names:    CamelCase
 function names: mixedCase
 constant names: ALL_CAPITAL + underscore
 variable names: lower_case + underscore
"""

# imports and constants
import FreeCAD
#import Templator
import os    # built-in modules
import math  # to use some predefined conversions
import AnSvgToolset
from TechDrawTools import TDToolsUtil
from PySide import QtGui, QtCore

icons_path = AnSvgToolset.icons_path
symbols_path = AnSvgToolset.symbols_path

class TaskAuxView():
    '''Provides the TechDraw AuxView Task Dialog.'''
    def __init__(self, new_view, new_symbol, dir_tag, view_tag):

        self.view = new_view
        self.symbol = new_symbol
        self.dir_tag = dir_tag
        self.view_tag = view_tag

        self.revert = False

        #- Add a Box container to group widgets
        self.groupBox = QGroupBox("GroupBox")
        #- Add a grid to order widgets
        self.grid = QGridLayout() # instantiates a QGridLayout
        self.groupBox.setLayout(self.grid) # puts the grid inside the groupBox

        #- Add some labels to the grid
        self.label_marker = QLabel("Marker of the auxiliary view: ")
        self.grid.addWidget(self.label_marker, 0, 0)
        self.label_direction = QLabel("Direction: ")
        self.grid.addWidget(self.label_direction, 1, 0)

        #- Set up a LineEdit - Marker
        self.lineEdit_marker = QLineEdit()
        self.lineEdit_marker.setToolTip("Tool tip")
        self.lineEdit_marker.setText("X")
        self.lineEdit_marker.textChanged.connect(self.on_lineEdit_marker)
        self.grid.addWidget(self.lineEdit_marker, 0, 1)

        #- Set up a CheckBox - Revert
        self.checkBox_reverse = QCheckBox("Reverse direction")
        self.checkBox_reverse.setToolTip("Reverts the view direction")
        self.checkBox_reverse.setChecked(self.revert)
        self.checkBox_reverse.stateChanged.connect(self.on_checkbox_changed)
        self.grid.addWidget(self.checkBox_reverse, 1, 1)

        # Show the QGroupBox
        self.form = self.groupBox

    def on_lineEdit_marker(self, value):
        '''Renames the view markers'''
        self.dir_tag.Text = value
        self.view_tag.Text = ("AuxView " + value)

    def on_checkbox_changed(self, value):
        '''Reverses the direction and the view arrow'''
        self.reverseDirection()
        self.reverseArrow()
        if value:
            self.result = True
        else:
            self.result = False

    def reverseArrow(self):
        '''2D - Reverses the view arrow '''
        angle = float(self.symbol.Rotation)
        if angle >180:
            angle -= 180
        else:
            angle += 180
        self.symbol.Rotation = angle
        #FreeCADGui.runCommand("TechDraw_RedrawPage",0)

    def reverseDirection(self):
        '''3D - Reverses the view direction'''
        axis_vector = self.view.XDirection
        z_direction = self.view.Direction
        #- Create a rotation, angle input in float (for degrees), stored in rad
        around_direction = FreeCAD.Rotation(axis_vector, 180)
        #- Apply rotation to the base_view.XDirection
        z_direction = around_direction.multVec(z_direction)
        self.view.Direction = z_direction
        Gui.runCommand("TechDraw_RedrawPage",0)

    def accept(self):
        '''slot: OK pressed'''
        Gui.Control.closeDialog()

    def reject(self):
        return True

def getActiveDocument():
    '''
    Returns the active document or sends a message
    '''
    ado = FreeCAD.activeDocument()
    if ado is not None:
        return ado
    TDToolsUtil.displayMessage("AuxView", "No active document available!")
    return False

def getPageOfSelection(doc, b_view):
    '''Retrieves the Page that holds the selected elements'''
    #- Find an object starting with 'Page' that contains the selected object
    for each in doc.Objects:
        if each.Name.startswith("Page"):  # [0:4] == 'Page':
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
    '''Creates 3D vectors to calculate the 2D angle towards the x direction of the
    base view which is parallel to the page view's x direction.
    The direction of the XDirection property is not parallel to the view's
    x direction if the view is rotated! This angle also has to be taken into
    account to calculate the 3D angle'''
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
    '''
    Creates 3D vectors to calculate the 2D angle towards the x direction of the
    base view
    '''
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
    '''
    The main section, no more, no less
    '''
    # Operations are performed in the active document of the application
    #- Retrieve the active document
    active_doc = getActiveDocument()
    if not active_doc:  # (active_doc is None/False)
        return
    #- Retrieve the selection view and selected vertices
    if TDToolsUtil.getSelView() and TDToolsUtil.getSelVertexes(2):
        base_view = TDToolsUtil.getSelView()
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

    #active_doc.recompute(None,True,True)
    Gui.runCommand("TechDraw_RedrawPage",0)

    return
##########################################################################################################
# Gui code
##########################################################################################################

if AnSvgToolset.isGuiLoaded():
    from FreeCAD import Gui
    from PySide import QtCore
    from PySide.QtGui import QGroupBox
    from PySide.QtWidgets import (QGridLayout, QLabel, QCheckBox, QLineEdit)

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
        """Creates an auxiliary view from two points"""

        def GetResources(self):
            return {
                "Pixmap": os.path.join(
                    icons_path, "Templater_AuxView.svg"
                ),  # the name of an svg file available in the resources
                "MenuText": "Auxiliary view",
                #"Accel": "S, H",
                "ToolTip":
                    "Creates an auxiliary view\n"
                    "1. Select two vertices.\n"
                    "2. Invoke this Command",
            }

        def Activated(self):
            mainSection()
            return

        def IsActive(self):
            return True

    Gui.addCommand("Templater_AuxView", AuxViewCommandClass())
