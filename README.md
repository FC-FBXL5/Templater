# FreeCAD_Templater
A workbench related to templates, symbols, and auxiliary views for TechDraw drawings.
# Tools
Now 2 kinds of tools are available, tools to create templates and pages, and a tool to create views.
## Creating and inserting templates
Two tools to create a template and insert it into the active dokument.
* One resembles the example from the [TechDraw TemplateGenerator](https://wiki.freecad.org/TechDraw_TemplateGenerator) tutorial page.
* The other is a bit overloaded but shows how templates could be created and inserted automatically 
### Usage
1. Launch either the New Template Wiki, or the New Template Multi tool.
2. Adjust the parameters in the task panel.
3. OK finishes the selected tool, and you should find a new page with an embedded template in your document
## Create an auxiliary view
This tool creates a secondary (auxiliary) view from 2 selected vertices of one existing view. It is based on the [Macro_TechDraw_AuxiliaryView](https://wiki.freecad.org/Macro_TechDraw_AuxiliaryView).
### Usage
1. Select 2 vertices to define the projection plane.
2. Launch the Auxiliary View tool.
3. Optionally reverse the direction in the task panel.

# Installation
The Templater WB can be installed via the [Addon Manager](https://github.com/FreeCAD/FreeCAD-addons) (in the Tools menu)

## Release notes:

* 2025.0.1  11. Sep. 2025: New Template Multi tool added.
* 2025.0.0  20. Jun. 2025: Initial version. Auxiliary View and New Template Wiki tools.

