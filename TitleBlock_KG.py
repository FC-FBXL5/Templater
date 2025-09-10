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
This script creates a title block for a template.
"""

# imports and constants
import FreeCAD
from SvgToolkit import (
    levelOfIndentation,
    svgPath,
    svgText,
    ediText
    )

translate = FreeCAD.Qt.translate

def fixed_texts():
    """Creates a translated dictionary for title block annotations"""
    fixed_texts = {
        "drawn"        : translate("Templater", "Drawn:"),
        "approved"     : translate("Templater", "Approved:"),
        "name"         : translate("Templater", "Name:"),
        "CAD_version"  : translate("Templater", "CAD version:"),
        "date"         : translate("Templater", "Date:"),
        "title"        : translate("Templater", "Title:"),
        "part_number"  : translate("Templater", "Part number:"),
        "scale"        : translate("Templater", "Scale:"),
        "material"     : translate("Templater", "Material:"),
        "mass"         : translate("Templater", "Mass:"),
        "sheet_format" : translate("Templater", "Format:"),
        "sheet_count"  : translate("Templater", "Sheet:"),
        "owner"        : translate("Templater", "Owner:")
        }
    return fixed_texts

def bom_texts():
    """Creates a translated dictionary for BOM annotations"""
    fixed_texts = {
        "position" : translate("Templater", "Pos."),
        "amount"   : translate("Templater", "Amount"),
        "unit"     : translate("Templater", "Unit"),
        "title"    : translate("Templater", "Title"),
        "number"   : translate("Templater", "Part number"),
        "material" : translate("Templater", "Material"),
        "mass"     : translate("Templater", "Mass"),
        "remark"   : translate("Templater", "Remark")
        }
    return fixed_texts

def createTitleBlock(file_path, sheet_size, da_offsets):
    """
    Calls external methods to create a movable title block
    according to DIN EN ISO 7200
    """
    sheet_width = sheet_size[0]
    sheet_height = sheet_size[1]
    #- Set offsets between drawing area and page edges
    offset_right  = da_offsets[3]
    offset_bottom = da_offsets[1]
    #- Set title block width
    tb_width = 180  # 180 acc. to ISO 7200
    tb_height = 35
    #- Lower left corner of the title block (origin)
    tb_x = str(int(sheet_width) - offset_right - tb_width)
    tb_y = str(int(sheet_height) - offset_bottom)

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
    t.write(loi + "style=\"fill:none;stroke:#000000;stroke-width:0.35;\
stroke-linecap:miter;stroke-miterlimit:4\">\n")
    loi = levelOfIndentation(6)
    if sheet_width != "210": # DIN-A4
        t.write(loi + svgPath("  0","  0","  0","-35") + "\n")
    t.write(loi + svgPath("  0", "-35", "180"," 0") + "\n")
    t.write(loi + svgPath("  0", "-14", "h", "180") + "\n")
    t.write(loi + svgPath(" 60", "  0", "v", "-35") + "\n")
    t.write(loi + svgPath("152", "  0", "v", "-35") + "\n")
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")

    t.write(loi + "<g id=\"titleblock-structure\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "style=\"fill:none;stroke:#000000;stroke-width:0.18;\
stroke-linecap:miter;stroke-miterlimit:4\">\n")
    loi = levelOfIndentation(6)
    t.write(loi + svgPath("  0", "-21", "h", " 60") + "\n")
    t.write(loi + svgPath("  0", "-28", "h", " 60") + "\n")
    t.write(loi + svgPath("152", " -7", "h", " 28") + "\n")
    t.write(loi + svgPath("152", "-21", "h", " 28") + "\n")
    t.write(loi + svgPath("152", "-28", "h", " 28") + "\n")
    t.write(loi + svgPath(" 12", "-14", "v", "-21") + "\n")
    t.write(loi + svgPath(" 36", "-14", "v", "-21") + "\n")
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    #- small texts, left-aligned
    t.write(loi + "<g id=\"titleblock-text-non-editable\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "style=\"font-size:2.0;text-anchor:start;fill:#000000;\
font-family:osifont\">\n")
    loi = levelOfIndentation(6)
    ft = fixed_texts()
    t.write(loi + svgText("  1.5", "-31  ", ft["drawn"]) + "\n")
    t.write(loi + svgText("  1.5", "-24  ", ft["approved"]) + "\n")
    t.write(loi + svgText("  1.5", "-11.5", ft["owner"]) + "\n")
    t.write(loi + svgText(" 13.5", "-32.5", ft["name"]) + "\n")
    t.write(loi + svgText(" 13.5", "-25.5", ft["name"]) + "\n")
    t.write(loi + svgText(" 13.5", "-18.5", ft["CAD_version"]) + "\n")
    t.write(loi + svgText(" 37.5", "-32.5", ft["date"]) + "\n")
    t.write(loi + svgText(" 37.5", "-25.5", ft["date"]) + "\n")
    t.write(loi + svgText(" 61.5", "-32.5", ft["title"]) + "\n")
    t.write(loi + svgText(" 61.5", "-11.5", ft["part_number"]) + "\n")
    t.write(loi + svgText("153.5", "-32.5", ft["scale"]) + "\n")
    t.write(loi + svgText("153.5", "-25.5", ft["material"]) + "\n")
    t.write(loi + svgText("153.5", "-18.5", ft["mass"]) + "\n")
    t.write(loi + svgText("153.5", "-11.5", ft["sheet_format"]) + "\n")
    t.write(loi + svgText("153.5", " -4.5", ft["sheet_count"]) + "\n")
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close
    logo_pos = (
        int(sheet_width) - offset_right - 176.5,
        int(sheet_height) - offset_bottom - 20
        )
    proj_pos = (
        int(sheet_width) - offset_right - 132,
        int(sheet_height) - offset_bottom - 17.5
        )
    return(logo_pos, proj_pos, tb_height)

def createEditableText(file_path, sheet_width, sheet_height, ink = "#000"):
    """
    Calls external methods to create editable texts
    """
    #- Set offsets between drawing area and page edges
    offset_right  = 10  # acc. to ISO 7200
    offset_bottom = 10  # acc. to ISO 7200
    #- Set title block width
    tb_width = 180  # 180 acc. to ISO 7200
    #- Offsets from page origin to title block origin to calculate absolute
    #- coordinates for editable texts.
    #  (adds to relative coordinates from title block origin)
    ed_x = int(sheet_width) - offset_right - tb_width
    ed_y = int(sheet_height) - offset_bottom

    t = open(file_path, "a", encoding = "utf-8")

    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"titleblock-editable-owner\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"font-size:2.5;text-anchor:start;fill:" + ink + ";\
font-family:osifont\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + ediText("Owner", str(ed_x + 16), str(ed_y - 11),
        "Owner") + "\n"
        )
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")

    t.write(loi + "<g id=\"titleblock-editable-address\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"font-size:1.8;text-anchor:start;fill:" + ink + ";\
font-family:osifont\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + ediText("Address-1", str(ed_x + 16), str(ed_y - 8),
        "Address1")+"\n"
        )
    t.write(loi + ediText("Address-2", str(ed_x + 16), str(ed_y - 5.5),
        "Address2")+"\n"
        )
    t.write(loi + ediText("MailTo",    str(ed_x + 16), str(ed_y - 1),
        "MailTo")+"\n"
        )
    t.write(loi + ediText("Copyright", str(ed_x + 63), str(ed_y - 15),
        "Copyright")+"\n"
        )
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")

    t.write(loi + "<g id=\"titleblock-editable-small\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"font-size:3.5;text-anchor:start;fill:" + ink + ";\
font-family:osifont\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + ediText("Author",    str(ed_x + 14),  str(ed_y - 29),
        "Author")+"\n"
        )
    t.write(loi + ediText("AuDate",    str(ed_x + 39),  str(ed_y - 29),
        "YY/MM/DD")+"\n"
        )
    t.write(loi + ediText("Supervisor",str(ed_x + 14),  str(ed_y - 22),
        "Supervisor")+"\n"
        )
    t.write(loi + ediText("SvDate",    str(ed_x + 39),  str(ed_y - 22),
        "YY/MM/DD")+"\n"
        )
    t.write(loi + ediText("CADVersion",str(ed_x + 14),  str(ed_y - 15),
        "FreeCAD 0.20")+"\n"
        )
    t.write(loi + ediText("Material",  str(ed_x + 162), str(ed_y - 22.5),
        "Mat.")+"\n"
        )
    t.write(loi + ediText("Mass",      str(ed_x + 162), str(ed_y - 15.5),
        "-,- g")+"\n"
        )
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")

    t.write(loi + "<g id=\"titleblock-editable-medium\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"font-size:5;text-anchor:start;fill:" + ink + ";\
font-family:osifont\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + ediText("Title",    str(ed_x + 63), str(ed_y - 27),
        "Part name")+"\n"
        )
    t.write(loi + ediText("SubTitle", str(ed_x + 63), str(ed_y - 20),
        "-")+"\n"
        )
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")

    t.write(loi + "<g id=\"titleblock-editable-centered\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"font-size:5;text-anchor:middle;fill:" + ink + ";\
font-family:osifont\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + ediText("Scale",  str(ed_x + 168), str(ed_y - 29),
        "1:1")+"\n"
        )
    t.write(loi + ediText("Format", str(ed_x + 168), str(ed_y - 8),
        "Format")+"\n"
        )
    t.write(loi + ediText("Sheets", str(ed_x + 168), str(ed_y - 1),
        "1 / 1")+"\n"
        )
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")

    t.write(loi + "<g id=\"titleblock-editable-Large\"\n")
    loi = levelOfIndentation(3)
    t.write(loi + "style=\"font-size:7;text-anchor:end;fill:" + ink + ";\
font-family:osifont\">\n")
    loi = levelOfIndentation(4)
    t.write(loi + ediText("PtNumber", str(ed_x + 147), str(ed_y - 2),
        "Part Number")+"\n"
        )
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n")
    t.close

def createBOMLines(file_path, sheet_width, sheet_height,bom_rows, ink = "#000"):
    """
    Calls external methods to create BOM lines
    """
    #- Set offsets between drawing area and page edges
    offset_right  = 10  # acc. to ISO 7200
    offset_bottom = 10  # acc. to ISO 7200
    #- Set title block width
    tb_width = 180  # 180 acc. to ISO 7200
    tb_height = 35  # matching the title block above

    if bom_rows == 0:
        return
    else:
        max_rows = (int(bom_rows) + 1)

    st_x = int(sheet_width) - offset_right - tb_width
    st_y = int(sheet_height) - offset_bottom - tb_height

    t = open(file_path,"a", encoding = "utf-8")
    loi = levelOfIndentation(2)
    t.write(loi + "<g id=\"bill-of-material\">\n")
    # BOM base line
    loi = levelOfIndentation(4)
    t.write(loi + "<g style=\"stroke:#000000;stroke-width:0.35;stroke-linecap:\
round\">\n")
    if sheet_width == "210": # format == "DIN-A4":
        loi = levelOfIndentation(6)
        t.write(loi + svgPath(str(st_x), str(st_y - 8), " 180", "  0 ") + "\n")
    else :
        t.write(loi + svgPath(str(st_x),str(st_y-8)," 180","  0 ")+"\n")
        t.write(loi + svgPath(str(st_x),str(st_y)  ,"   0"," -8 ")+"\n")
        loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    # Field separators
    t.write(loi + "<g style=\"stroke:#000000;stroke-width:0.18;stroke-linecap:\
round\">\n")
    loi = levelOfIndentation(6)
    t.write(loi + svgPath(str(st_x +  10), str(st_y), "v", "  -8") + "\n")
    t.write(loi + svgPath(str(st_x +  20), str(st_y), "v", "  -8") + "\n")
    t.write(loi + svgPath(str(st_x +  30), str(st_y), "v", "  -8") + "\n")
    t.write(loi + svgPath(str(st_x +  60), str(st_y), "v", "  -8") + "\n")
    t.write(loi + svgPath(str(st_x + 120), str(st_y), "v", "  -8") + "\n")
    t.write(loi + svgPath(str(st_x + 140), str(st_y), "v", "  -8") + "\n")
    t.write(loi + svgPath(str(st_x + 160), str(st_y), "v", "  -8") + "\n")
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    # Non-editable Texts
    t.write(loi + "<g id=\"BOM-h35-non-editable\"\n")
    loi = levelOfIndentation(5)
    t.write(loi + "style=\"font-family:osifont;font-size:3.5;text-anchor:\
middle;fill:#000000\">\n")
    loi = levelOfIndentation(6)
    bt = bom_texts()
    t.write(loi + svgText(str(st_x +   5), str(st_y - 4), bt["position"])
        + "\n"
        )
    t.write(loi + svgText(str(st_x +  15), str(st_y - 4), bt["amount"])
        + "\n"
        )
    t.write(loi + svgText(str(st_x +  25), str(st_y - 4), bt["unit"]) + "\n")
    t.write(loi + svgText(str(st_x +  45), str(st_y - 4), bt["title"]) + "\n")
    t.write(loi + svgText(str(st_x +  90), str(st_y - 4), bt["number"])
        + "\n"
        )
    t.write(loi + svgText(str(st_x + 130), str(st_y - 4), bt["material"])
        + "\n"
        )
    t.write(loi + svgText(str(st_x + 150), str(st_y - 4), bt["mass"]) + "\n")
    t.write(loi + svgText(str(st_x + 170), str(st_y - 4), bt["remark"])
        + "\n"
        )
    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    # Editable Lines
    t.write(loi + "<g id=\"BOM-Line\">\n")
    # st_x = int(sheet_width) - dAR - 180
    # st_y = int(sheet_height) - dAB - 43
    st_y -= 8

    for value in range(1,max_rows):
        loi = levelOfIndentation(6)
        t.write(loi + "<g style=\"stroke:#000000;stroke-width:0.35;\
stroke-linecap:round\">\n")
        loi = levelOfIndentation(8)
        if sheet_width == "210": # format == "DIN-A4":
            t.write(loi + svgPath(str(st_x), str(st_y - 6), " 180", "  0 ")
                + "\n"
                )
        else :
            t.write(loi + svgPath(str(st_x), str(st_y - 6), " 180", "  0 ")
                + "\n"
                )
            t.write(loi + svgPath(str(st_x), str(st_y)  , "   0", " -6 ")
                + "\n"
                )
        loi = levelOfIndentation(6)
        t.write(loi + "</g>\n")
        loi = levelOfIndentation(7)
        t.write(loi + "<g style=\"stroke:#000000;stroke-width:0.18;\
stroke-linecap:round\">\n")
        loi = levelOfIndentation(8)
        t.write(loi + svgPath(str(st_x +  10), str(st_y), "v", "  -6") + "\n")
        t.write(loi + svgPath(str(st_x +  20), str(st_y), "v", "  -6") + "\n")
        t.write(loi + svgPath(str(st_x +  30), str(st_y), "v", "  -6") + "\n")
        t.write(loi + svgPath(str(st_x +  60), str(st_y), "v", "  -6") + "\n")
        t.write(loi + svgPath(str(st_x + 120), str(st_y), "v", "  -6") + "\n")
        t.write(loi + svgPath(str(st_x + 140), str(st_y), "v", "  -6") + "\n")
        t.write(loi + svgPath(str(st_x + 160), str(st_y), "v", "  -6") + "\n")
        loi = levelOfIndentation(6)
        t.write(loi + "</g>\n")
        # Editable Texts
        t.write(loi + "<g id=\"BOM-editable-left-aligned\"\n")
        loi = levelOfIndentation(7)
        t.write(loi + "style=\"font-family:osifont;font-size:3.5;\
text-anchor:start;fill:" + ink + "\">\n")
        loi = levelOfIndentation(8)
        t.write(loi + ediText("Partname"   + str(value), str(st_x + 32),
            str(st_y - 2),"-") + "\n"
            )
        t.write(loi + ediText("PartNumber" + str(value), str(st_x + 62),
            str(st_y - 2),"-") + "\n"
            )
        t.write(loi + ediText("Material"   + str(value), str(st_x + 122),
            str(st_y - 2),"-") + "\n"
            )
        t.write(loi + ediText("Remark"     + str(value), str(st_x + 162),
            str(st_y -2 ),"-") + "\n"
            )
        loi = levelOfIndentation(6)
        t.write(loi + "</g>\n")
        t.write(loi + "<g id=\"BOM-editable-right-aligned\"\n")
        loi = levelOfIndentation(7)
        t.write(loi + "style=\"font-family:osifont;font-size:3.5;\
text-anchor:end;fill:" + ink + "\">\n")
        loi = levelOfIndentation(8)
        t.write(loi + ediText("Position" + str(value), str(st_x + 9),
            str(st_y - 2), str(value)) + "\n"
            )
        t.write(loi + ediText("Amount"   + str(value), str(st_x + 19),
            str(st_y - 2), "-") + "\n"
            )
        t.write(loi + ediText("Mass"     + str(value), str(st_x + 159),
            str(st_y - 2), "-") + "\n"
            )
        loi = levelOfIndentation(6)
        t.write(loi + "</g>\n")
        t.write(loi + "<g id=\"BOM-editable-centered\"\n")
        loi = levelOfIndentation(7)
        t.write(loi + "style=\"font-family:osifont;font-size:3.5;\
text-anchor:middle;fill:" + ink + "\">\n")
        loi = levelOfIndentation(8)
        t.write(loi + ediText("Unit" + str(value), str(st_x + 25),
            str(st_y - 2), "-") + "\n"
            )
        loi = levelOfIndentation(6)
        t.write(loi + "</g>\n")
        st_y = st_y-6

    loi = levelOfIndentation(4)
    t.write(loi + "</g>\n")
    loi = levelOfIndentation(2)
    t.write(loi + "</g>\n\n")
    t.close
