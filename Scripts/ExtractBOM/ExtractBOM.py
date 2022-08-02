#Author-Freeman Porten.
#Description-Extract BOM information from active design.

from pickle import FALSE
import adsk.core, adsk.fusion, traceback
#import system modules
import os, sys 
#get the path of add-in
my_addin_path = os.path.dirname(os.path.realpath(__file__)) 
print(my_addin_path)
#add the path to the searchable path collection
if not my_addin_path in sys.path:
   sys.path.append(my_addin_path) 
from .openpyxl import load_workbook,Workbook
import tkinter as tk
from tkinter import filedialog
import re

from py.BomClass import BOM

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
        title = 'Extract BOM'
        
        
        # create bom list
        bom1 = BOM()
        bom1.addRoot(rootComponentName=root.name, rootComponentPartNumber=root.partNumber)
        bom2 = BOM()

        # bom1 contains info on components broken down by subassembly.
        recursiveCompInfoStruct(parentComponent=root, bom=bom1,multiplier=1)
        recursiveCompInfoAll(parentComponent=root, bom=bom2)

        # set the order of the columns for the spreadsheet
        bom1Cols = [
            'partNumber',
            'name',
            'parentName',
            'type',
            'Per Subassembly instances',
            'instances',
            'material',
            'colour',
            'mass (grams)',
            'length'
            ]

        bom2Cols = [
            'partNumber',
            'name',
            'type',
            'instances',
            'material',
            'colour',
            'mass (grams)',
            'length'
            ]
        
        # Setup column names for the spreadsheet
        for col, val in enumerate(bom1Cols, start=1):
            ws1.cell(row=1, column=col).value = val
        # Display the BOM
        for r, comp in enumerate(bom1.bomList, start=2):
            for col, key in enumerate(bom1Cols, start=1):
                ws1.cell(row=r, column=col).value = comp[key]

        # Setup column names for the spreadsheet
        for col, val in enumerate(bom2Cols, start=1):
            ws2.cell(row=1, column=col).value = val

        # Display the BOM
        for r, comp in enumerate(bom2.bomList, start=2):
            for col, key in enumerate(bom2Cols, start=1):
                ws2.cell(row=r, column=col).value = comp[key]
        

        tkRoot = tk.Tk()
        tkRoot.withdraw()
        filename = filedialog.askopenfilename() # show an "Open" dialog box and return the path to the selected file
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
        recursiveCompInfoStruct(ucomp, bom, multiplier*comps.count(ucomp))
    return bom

def recursiveCompInfoAll(parentComponent:adsk.fusion.Component, bom : BOM):
    
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
            
        recursiveCompInfoAll(comp, bom)
    return

def find_between( s:str, first:str, last:str):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""