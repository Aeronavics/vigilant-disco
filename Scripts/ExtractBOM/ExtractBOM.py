#Author-Freeman Porten.
#Description-Extract BOM information from active design.

from pickle import FALSE
import adsk.core, adsk.fusion, traceback
#import system modules
import os, sys

from pathlib import Path

#get the path of add-in
my_addin_path = os.path.dirname(os.path.realpath(__file__)) 
print(my_addin_path)
#add the path to the searchable path collection
if not my_addin_path in sys.path:
   sys.path.append(my_addin_path) 
from .openpyxl import load_workbook,Workbook, worksheet
import tkinter as tk
from tkinter import filedialog

from py.BomClass import BOM

# Row counter for Wiring Looms
loomRowStart = 1

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        if not design:
            ui.messageBox('No active design')
            return
        # Get all occurrences in the root component of the active design
        root = design.rootComponent

        wb=Workbook()
        ws1 =  wb.active
        ws1.title = "Structured BOM"
        ws2 =  wb.create_sheet("Unstructured BOM")
        ws3 =  wb.create_sheet("Looms BOM")
        
        
        # create bom list
        structuredBom = BOM()
        structuredBom.addRoot(rootComponentName=root.name, rootComponentPartNumber=root.partNumber)
        unstructuredBom = BOM()
        

        # bom1 contains info on components broken down by subassembly.
        recursiveCompInfoStruct(parentComponent=root, bom=structuredBom,multiplier=1)
        recursiveCompInfoAll(parentComponent=root, bom=unstructuredBom, loomSheet=ws3)

        # set the order of the columns for the spreadsheet
        structuredCols = [
            'partNumber',
            'name',
            'parentName',
            'type',
            'Per Subassembly instances',
            'instances',
            'material',
            'colour',
            'mass (grams)',
            'length (mm)'
            ]

        unstructuredCols = [
            'partNumber',
            'name',
            'type',
            'instances',
            'material',
            'colour',
            'mass (grams)',
            'length (mm)'
            ]
        
        loomCols = [
            'partNumber',
            'name',
            'type',
            'instances',
            'material',
            'colour',
            'mass (grams)',
            'length (mm)'
            ]


        ## Structured Bom
        ws1 = writeToSheet(sheet=ws1, colList=structuredCols, bom=structuredBom)
        ## Unstructured Bom
        ws2 = writeToSheet(sheet=ws2, colList=unstructuredCols, bom=unstructuredBom)
        ## Looms Bom
        # ws3 = writeToSheet(sheet=ws3, colList=loomCols, bom=loomsBom)
        
        tkRoot = tk.Tk()
        tkRoot.withdraw()

        # filename = filedialog.askopenfilename() # show an "Open" dialog box and return the path to the selected file
        filename = filedialog.asksaveasfilename(filetypes=(
                    ("Excel Workbook", "*.xlsx"),
                    ("All files", "*.*"),
                ),
                initialfile = root.name + ' BOM.xlsx'
            )
        wb.save(filename)

        ui.messageBox('file saved')
        os.startfile(filename)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def recursiveCompInfoStruct(parentComponent:adsk.fusion.Component, bom :BOM, multiplier:int):
    occrs = parentComponent.occurrences
    comps = []

    # Find all unique components in the assembly
    for occr in occrs:
        comps.append(occr.component)
    ucomps = []
    [ucomps.append(n) for n in comps if n not in ucomps]
    
    for ucomp in ucomps:
        # Ignore contruction components
        if ("(construction)" in ucomp.name.lower()) or ("(construction)" in ucomp.description.lower()):
            continue
        
        length = 0
        # Get information on length if the component has a length
        if "(length: " in ucomp.name.lower():
            length = float(find_between(s=ucomp.name.lower(), first="(length: ",last="mm)"))
        if "(length: " in ucomp.description.lower():
            length = float(find_between(s=ucomp.description.lower(), first="(length: ",last="mm)"))


        # Gather any BOM worthy values from the component
        mass = 0
        material = False
        color = False
        bodies = ucomp.bRepBodies
        for bodyK in bodies:
            if bodyK.isSolid:
                mass += bodyK.physicalProperties.mass*1000
                material = bodyK.material.name
                color = bodyK.appearance.name
        mass = round(mass,4)

        # Don't store groups that are empty
        if (not ucomp.occurrences) and (mass == 0):
            continue
        
        bom.addEntry(name=ucomp.name, desc=ucomp.description, partNumber=ucomp.partNumber, parentName=parentComponent.name,  parentDesc=parentComponent.description, parentPartNumber=parentComponent.partNumber, instancesInSubassembly=comps.count(ucomp), instances=multiplier*comps.count(ucomp), mass=mass, material = material, color= color, length=length)
        ucompType = bom.getCompType(name=ucomp.name, desc=ucomp.description, parentName=parentComponent.name, parentDesc=parentComponent.description)
        
        # If the component is a Loom don't store the components in this BOM.
        if ucompType == "Looms":
            continue
        recursiveCompInfoStruct(ucomp, bom, multiplier*comps.count(ucomp))
    return bom

def recursiveCompInfoAll(parentComponent:adsk.fusion.Component, bom : BOM, loomSheet):
    
    occrs = parentComponent.occurrences
    for occr in occrs:
        comp = occr.component
        
        # Get information on length if the component has a length
        length = 0
        if "(length: " in comp.name.lower():
            length = float(find_between(s=comp.name.lower(), first="(length: ",last="mm)"))
        if "(length: " in comp.description.lower():
            length = float(find_between(s=comp.description.lower(), first="(length: ",last="mm)"))

        bom.incrCountOfComp(name=comp.name,partNumber=comp.partNumber,length=length)
        if bom.getCountOfComp(name=comp.name, partNumber=comp.partNumber) == 0:
            # Ignore contruction components
            if "(construction)" in comp.name:
                continue
            
            # Gather any BOM worthy values from the component
            mass = 0
            material = False
            color = False
            bodies = comp.bRepBodies
            for bodyK in bodies:
                if bodyK.isSolid:
                    mass += bodyK.physicalProperties.mass*1000
                    material = bodyK.material.name
                    color = bodyK.appearance.name
            
            mass = round(mass,4)

            # If the component has a mass then we add it to the BOM
            if (not mass == 0):
                bom.addEntry(name=comp.name, desc=comp.description, partNumber=comp.partNumber, parentName=parentComponent.name,  parentDesc=parentComponent.description, parentPartNumber=parentComponent.partNumber, instancesInSubassembly=1, instances=1, mass=mass, material = material, color= color, length=length)
            
            compType = bom.getCompType(name=comp.name, desc=comp.description, parentName=parentComponent.name, parentDesc=parentComponent.description)
            # If the component is a Loom don't store the sub components in this BOM. Instead store it in the Looms BOM
            if compType == "Looms":
                bom.addEntry(name=comp.name, desc=comp.description, partNumber=comp.partNumber, parentName=parentComponent.name,  parentDesc=parentComponent.description, parentPartNumber=parentComponent.partNumber, instancesInSubassembly=1, instances=1, mass=mass, material = "Loom", color= "Loom", length="See Loom Bom")
                addLoom(loomSheet, comp)
                continue
        
        # If the component is a Loom don't store the sub components in this BOM.
        compType = bom.getCompType(name=comp.name, desc=comp.description, parentName=parentComponent.name, parentDesc=parentComponent.description)
        if compType == "Looms":
            continue
        recursiveCompInfoAll(comp, bom, loomSheet)
    return

def addLoom(sheet, LoomComp:adsk.fusion.Component):
    global loomRowStart
    startRow = loomRowStart
    loomTags = [
        LoomComp.partNumber,
        BOM.removeFusionVersionNumberAndPartNumber(name=LoomComp.name, partNumber=LoomComp.partNumber),
        LoomComp.description
    ]

    occrs = LoomComp.occurrences
    for occr in occrs:
        comp = occr.component
        if comp.name.lower() == "wires":
            wireTags = getWireTags(comp.description)
            for wireTag in wireTags:
                for wireOccr in comp.occurrences:
                    wireComp = wireOccr.component
                    if wireTag["Wire Part Number"] == wireComp.partNumber:
                        material = "Error Material not found"
                        color = "Error Color not found"
                        for bodyK in wireComp.bRepBodies:
                            if bodyK.isSolid:
                                material = bodyK.material.name
                                color = bodyK.appearance.name
                        wireTag["Wire Name"] = BOM.removeFusionVersionNumberAndPartNumber(name=wireComp.name,partNumber=wireComp.partNumber)
                        wireTag["Material"] = material
                        wireTag["Color"] = color
        if comp.name.lower() == "plugs":
            plugTags = getPlugTags(comp.description)
            for Tag in plugTags:
                for tagOccr in comp.occurrences:
                    tagComp = tagOccr.component
                    if Tag["Plug Part Number"] == tagComp.partNumber:
                        Tag["Plug Name"] = BOM.removeFusionVersionNumberAndPartNumber(name=tagComp.name,partNumber=tagComp.partNumber)
        if comp.name.lower() == "crimps":
            crimpTags = getCrimpTags(comp.description)
            for Tag in crimpTags:
                for tagOccr in comp.occurrences:
                    tagComp = tagOccr.component
                    if Tag["Crimp Part Number"] == tagComp.partNumber:
                        Tag["Crimp Name"] = BOM.removeFusionVersionNumberAndPartNumber(name=tagComp.name,partNumber=tagComp.partNumber)
        if comp.name.lower() == "loom electronics":
            loomElectronicsTags = getLoomElectronicsTags(comp.description)
            for Tag in loomElectronicsTags:
                for tagOccr in comp.occurrences:
                    tagComp = tagOccr.component
                    if Tag["Electronics Part Number"] == tagComp.partNumber:
                        Tag["Electronics Name"] = BOM.removeFusionVersionNumberAndPartNumber(name=tagComp.name,partNumber=tagComp.partNumber)
        if comp.name.lower() == "consumables":
            consumablesTags = getConsumablesTags(comp.description)
            for Tag in consumablesTags:
                for tagOccr in comp.occurrences:
                    tagComp = tagOccr.component
                    if Tag["Consumables Part Number"] == tagComp.partNumber:
                        Tag["Consumables Name"] = BOM.removeFusionVersionNumberAndPartNumber(name=tagComp.name,partNumber=tagComp.partNumber)

    LoomHeader = [
        'Loom Part Number',
        'Loom Name',
        'Notes'
    ]

    PlugHeader = [
        'Plug Part Number',
        'Plug Name',
        'Connector ID'
    ]

    LoomElectronicsHeader = [
        'Loom Electronics Part Number',
        'Loom Electronics Name',
        'Connector ID'
    ]

    WireHeader = [
        'Wire Part Number',
        'Wire Name',
        'Material',
        'Color',
        'Length (mm)',
        'Twisted Pair',
        'Connector ID 1',
        'Pin 1',
        'Method 1',
        'Connector ID 2',
        'Pin 2',
        'Method 2'
    ]

    CrimpHeader = [
        'Crimp Part Number',
        'Crimp Name',
        'Crimp Type ID',
        'Instances'
    ]
    
    ConsumablesHeader = [
        'Consumables Part Number',
        'Consumables Name',
        'Instances',
        'Length (mm)',
        'Mass (g)'

    ]

    # Loom Header
    rowOffset = 0
    for col, val in enumerate(LoomHeader, start=1):
        sheet.cell(row=startRow+rowOffset, column=col).value = val
    rowOffset = rowOffset+1
    # Display the Loom root 
    for col, val in enumerate(loomTags, start=1):
        sheet.cell(row=startRow+rowOffset, column=col).value = val
    rowOffset = rowOffset+1
    # Plug Header
    for col, val in enumerate(PlugHeader, start=1):
        sheet.cell(row=startRow+rowOffset, column=col).value = val
    rowOffset = rowOffset+1
    # Display the Plugs
    for r, comp in enumerate(plugTags, start=startRow+rowOffset):
        for col, key in enumerate(PlugHeader, start=1):
            sheet.cell(row=r, column=col).value = comp[key]
        rowOffset = rowOffset+1
    # Crimp Header
    for col, val in enumerate(CrimpHeader, start=1):
        sheet.cell(row=startRow+rowOffset, column=col).value = val
    rowOffset = rowOffset+1
    # Display the Crimps
    for r, comp in enumerate(crimpTags, start=startRow+rowOffset):
        for col, key in enumerate(CrimpHeader, start=1):
            sheet.cell(row=r, column=col).value = comp[key]
        rowOffset = rowOffset+1
    # Loom Electronics Header
    for col, val in enumerate(LoomElectronicsHeader, start=1):
        sheet.cell(row=startRow+rowOffset, column=col).value = val
    rowOffset = rowOffset+1
    # Display the Loom Electronics
    for r, comp in enumerate(loomElectronicsTags, start=startRow+rowOffset):
        for col, key in enumerate(LoomElectronicsHeader, start=1):
            sheet.cell(row=r, column=col).value = comp[key]
        rowOffset = rowOffset+1
    # Wire Header
    for col, val in enumerate(WireHeader, start=1):
        sheet.cell(row=startRow+rowOffset, column=col).value = val
    rowOffset = rowOffset+1
    # Display the Wire
    for r, comp in enumerate(wireTags, start=startRow+rowOffset):
        for col, key in enumerate(WireHeader, start=1):
            sheet.cell(row=r, column=col).value = comp[key]
        rowOffset = rowOffset+1
    # Consumables Header
    for col, val in enumerate(ConsumablesHeader, start=1):
        sheet.cell(row=startRow+rowOffset, column=col).value = val
    rowOffset = rowOffset+1
    # Display the Consumables
    for r, comp in enumerate(consumablesTags, start=startRow+rowOffset):
        for col, key in enumerate(ConsumablesHeader, start=1):
            sheet.cell(row=r, column=col).value = comp[key]
        rowOffset = rowOffset+1
    
    loomRowStart = startRow + rowOffset + 1


def getWireTags(desc:str) -> list:
    desc = desc.replace("\n","")
    tagList = []
    # We remove the first tag as it is the definition.
    tags = find_between(desc,"(",")")
    desc = desc.replace("("+tags+")","")
    while desc != "":
        tags = find_between(desc,"(",")")
        desc = desc.replace("("+tags+")","")
        splitTags = tags.split(":")
        tagList.append({
            "Wire Part Number":splitTags[0],
            "Wire Name":"Error wire not found",
            "Material":"Error wire not found",
            "Color":"Error wire not found",
            "Length (mm)":int(splitTags[1]),
            "Twisted Pair":splitTags[2],
            "Connector ID 1":splitTags[3],
            "Pin 1":splitTags[4],
            "Method 1":splitTags[5],
            "Connector ID 2":splitTags[6],
            "Pin 2":splitTags[7],
            "Method 2":splitTags[8]
        })
    return tagList

def getPlugTags(desc:str) -> list:
    desc = desc.replace("\n","")
    tagList = []
    # We remove the first tag as it is the definition.
    tags = find_between(desc,"(",")")
    desc = desc.replace("("+tags+")","")
    while desc != "":
        tags = find_between(desc,"(",")")
        desc = desc.replace("("+tags+")","")
        splitTags = tags.split(":")
        tagList.append({
            "Plug Part Number":splitTags[0],
            "Plug Name": "Error Plug Not Found",
            "Connector ID":splitTags[1]
        })
    return tagList

def getCrimpTags(desc:str) -> list:
    desc = desc.replace("\n","")
    tagList = []
    # We remove the first tag as it is the definition.
    tags = find_between(desc,"(",")")
    desc = desc.replace("("+tags+")","")
    while desc != "":
        tags = find_between(desc,"(",")")
        desc = desc.replace("("+tags+")","")
        splitTags = tags.split(":")
        tagList.append({
            "Crimp Part Number":splitTags[0],
            "Crimp Name": "Error Crimp Not Found",
            "Crimp Type ID":splitTags[1],
            "Instances":int(splitTags[2])
        })
    return tagList

def getLoomElectronicsTags(desc:str) -> list:
    desc = desc.replace("\n","")
    tagList = []
    # We remove the first tag as it is the definition.
    tags = find_between(desc,"(",")")
    desc = desc.replace("("+tags+")","")
    while desc != "":
        tags = find_between(desc,"(",")")
        desc = desc.replace("("+tags+")","")
        splitTags = tags.split(":")
        tagList.append({
            "Electronics Part Number":splitTags[0],
            "Electronics Name": "Error Electronics Not Found",
            "Connector ID":splitTags[1]
        })
    return tagList

def getConsumablesTags(desc:str) -> list:
    desc = desc.replace("\n","")
    tagList = []
    # We remove the first tag as it is the definition.
    tags = find_between(desc,"(",")")
    desc = desc.replace("("+tags+")","")
    while desc != "":
        tags = find_between(desc,"(",")")
        desc = desc.replace("("+tags+")","")
        splitTags = tags.split(":")
        tagList.append({
            "Consumables Part Number":splitTags[0],
            "Instances":int(splitTags[1]),
            "Length (mm)":float(splitTags[2]),
            "Mass (g)":float(splitTags[3])
        })       
    return tagList

def writeToSheet(sheet:worksheet, colList:list, bom:BOM):
    # Setup column names for the spreadsheet
    for col, val in enumerate(colList, start=1):
        sheet.cell(row=1, column=col).value = val
    # Display the BOM
    for r, comp in enumerate(bom.bomList, start=2):
        for col, key in enumerate(colList, start=1):
            sheet.cell(row=r, column=col).value = comp[key]
    return sheet

def find_between( s:str, first:str, last:str):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

