# FreeCAD_Templater
A workbench related to templates, symbols, and auxiliary views for TechDraw drawings.
# Tools
Now 3 kinds of tools are available, tools to create templates and pages, and a tool to create views.
## Creating and inserting templates
Two tools to create a template and insert it into the active dokument.
* One resembles the example from the [TechDraw TemplateGenerator](https://wiki.freecad.org/TechDraw_TemplateGenerator) tutorial page.
* The other is a bit overloaded but shows how templates could be created and inserted automatically 
### Usage
1. Launch either the New Template Wiki, or the New Template Multi tool.
2. Adjust the parameters in the task panel.
3. OK finishes the selected tool, and you should find a new page with an embedded template in your document.
## Create an auxiliary view
This tool creates a secondary (auxiliary) view from 1 edge or 2 selected vertices of one existing view. It is based on the [Macro_TechDraw_AuxiliaryView](https://wiki.freecad.org/Macro_TechDraw_AuxiliaryView).
### Usage
1. Select 1 edge (2 end vertices) or 2 individual vertices to define the view direction.
2. Launch the Auxiliary View tool.
3. An auxiliary view is created, its view direction is perpendicular to the connecting line between the two selected vertices by default.
4. Optionally reverse the view direction in the task panel.
5. Optionally align the view direction with the connecting line in the task panel.
6. Click Ok to finish.
## Creating and inserting feature frames
This tool creates feature frames for GD&T purposes.
Line parameters match with a symbol height of 10 mm.
### Usage
1. Select 1 view.
2. Launch the Tolerance Frame tool.
3. Adjust the parameters in the task panel.
   * Select a geometric tolerance for a tolerance frame, or enter a single (upper case) letter for a datum frame.
   * Edit the size of the tolerance zone.
   * Edit the datum entries.
4. Click Ok to finish.


# Installation
The Templater WB can be installed via the [Addon Manager](https://github.com/FreeCAD/FreeCAD-addons) (in the Tools menu)

## Release notes:

* v.0.0.3 - 29.Sep.2025: A tool to create feature frames was added.
* v.0.0.2 - 22.Sep.2025: Minor adjusments.
* v.0.0.1 - 21.Sep.2025: Initial version.

