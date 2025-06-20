# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   InitGui.py                                                            *
# *                                                                         *
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
"""A workbench related to TechDraw templates, views, and symbols."""

# Templater gui init module
#
# Gathering all the information to start FreeCAD
# This is the second one of three init scripts, the third one
# runs when the gui is up

import os
import FreeCAD
from FreeCAD import Gui
import AnSvgToolset

TemplaterPath = AnSvgToolset.mod_path
TemplaterIconPath = AnSvgToolset.icons_path

class Templater (Workbench):
    global TemplaterIconPath
    global TemplaterPath

    MenuText = "Templater"
    ToolTip = "Some tools to create auxiliary views, templates, and symbols"
    Icon = os.path.join(TemplaterIconPath, "Templater.svg")

    def Initialize(self):
        """
        This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the
        Activated function.
        """
        #- import here all the needed files that create your FreeCAD commands
        import AnSvgToolset
        import InsertTemplatePanelExtern
        import SayHello
        import WriteTemplate
        import WriteTemplateHHA38
        import WriteTemplateHHA60
        import WriteTemplateHHA63
        import SymbolTolerance
        import AuxView
        import os.path
        #- a list of command names created in the line above
        self.list = [
            "Templater_InsertTemplate",
            "Templater_SayHello",
            "Templater_WriteTemplate",
            "Templater_WriteTemplateHHA38",
            "Templater_WriteTemplateHHA60",
            "Templater_WriteTemplateHHA63",
            "Templater_SymbolTolerance",
            "Templater_AuxView"
            ]
        #- create a new toolbar with these commands
        self.appendToolbar("Templater Commands", self.list)
        #- create a new menu
        self.appendMenu("Templater", self.list)
        #- appends a submenu to an existing menu
        #self.appendMenu(["Templater", "My submenu"], self.list)
        #self.appendMenu(["Templater", "Mein submenu", "Bein"], self.list)

    def Activated(self):
        """This function is executed whenever the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This function is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        #- add commands to the context menu
        self.appendContextMenu("Templater", self.list)

    def GetClassName(self):
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"


Gui.addWorkbench(Templater())
