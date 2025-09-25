# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-3.0-or-later
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2025 FBXL5 available on the forum:                      *
# *   https://forum.freecad.org/memberlist.php?mode=viewprofile&u=26761     *
# *                                                                         *
# *   This file is part of FreeCAD.                                         *
# *                                                                         *
# *   FreeCAD is free software: you can redistribute it and/or modify it    *
# *   under the terms of the GNU Lesser General Public License as           *
# *   published by the Free Software Foundation, either version 3.0 of the  *
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
"""A workbench related to TechDraw templates, views, and symbols."""

# Templater gui init module
#
# Gathering all the information to start FreeCAD
# This is the second one of three init scripts, the third one
# runs when the gui is up

import os
import FreeCAD
from FreeCAD import Gui
import SvgToolkit

templator_path = SvgToolkit.mod_path
templator_icon_path = SvgToolkit.icons_path
translations_path = SvgToolkit.translations_path

#- Adds the translations folder path to the default search paths
Gui.addLanguagePath(translations_path)
Gui.updateLocale()

translate = FreeCAD.Qt.translate

class Templater (Workbench):
    global templator_icon_path
    global templator_path
    global translate

    MenuText = translate("Templater", "Templater")
    ToolTip = translate(
        "Templater",
        "Some tools to create auxiliary views, templates, and symbols"
        )
    Icon = os.path.join(templator_icon_path, "TemplaterWorkbench.svg")

    def Initialize(self):
        """
        This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the
        Activated function.
        """
        from PySide import QtCore
        from PySide.QtCore import QT_TRANSLATE_NOOP
        #- import here all the needed files that create your FreeCAD commands
        import os.path
        import SvgToolkit
        import TemplaterAuxViewCmd
        import TemplaterToleranceFrameCmd
        import TitleBlock_KG
        import TemplaterTemplateWikiCmd
        import TemplaterTemplateMultiCmd
        #- a list of command names created in the line above
        self.list = [
            "Templater_AuxView",
            "Templater_ToleranceFrame",
            "Templater_NewTemplateWiki",
            "Templater_NewTemplateMulti"
            ]
        #- create a new toolbar with these commands
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Templater"), self.list)
        #- create a new menu
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "Templater"), self.list)
        #- appends a submenu to an existing menu
        #self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "Templater"), self.list)

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
        self.appendContextMenu(translate("Templater", "Templater"), self.list)

    def GetClassName(self):
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"


Gui.addWorkbench(Templater())





