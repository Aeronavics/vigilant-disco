#Author-Freeman Porten.
#Description-Etract BOM information from active design.
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
        bom1 = []
        bom2 = []
        # add root comnponent info
        bom1 = getRootComponentInfo(root,bom1)
        bom2 = getRootComponentInfo(root,bom2)
        # bom1 contains info on components broken down by subassembly.
        bom1 = recursiveCompInfoStruct(root, bom1, 1)
        bom2 = recursiveCompInfoAll('root',root, bom2)
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
            'mass (grams)'
            ]

        bom2Cols = [
            'partNumber',
            'name',
            'type',
            'group',
            'instances',
            'material',
            'colour',
            'mass (grams)'
            ]
        
        for col, val in enumerate(bom1Cols, start=1):
            ws1.cell(row=1, column=col).value = val
        # Display the BOM
        for r, comp in enumerate(bom1, start=2):
            for col, key in enumerate(bom1Cols, start=1):
                ws1.cell(row=r, column=col).value = comp[key]

        for col, val in enumerate(bom2Cols, start=1):
            ws2.cell(row=1, column=col).value = val
        # Display the BOM
        for r, comp in enumerate(bom2, start=2):
            for col, key in enumerate(bom2Cols, start=1):
                ws2.cell(row=r, column=col).value = comp[key]
        
        # ws = createGroups(ws, 3, 3, len(bom)-2)
        tkRoot = tk.Tk()
        tkRoot.withdraw()
        filename = filedialog.askopenfilename() # show an "Open" dialog box and return the path to the selected file
        wb.save(filename)
        ui.messageBox('file saved')
        os.startfile(filename)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def getRootComponentInfo(rootComponent, bom):
    nameSplit = rootComponent.name[::-1].split("v",1)
    if nameSplit[0].isnumeric():
        name = nameSplit[1][::-1]
    else:
        name = rootComponent.name
    bom.append({
        'component': rootComponent,
        'partNumber': '--Root--',
        'name': rootComponent.name,
        'type':'Root',
        'Per Subassembly instances': 1,
        'instances': 1,
        'mass (grams)': '--Root--',
        'material': '--Root--',
        'colour': '--Root--',
        'parentAss': '--Root--',
        'parentName': '--Root--',
        'group': '--Root--'
    })
    return bom

def recursiveCompInfoStruct(parentComponent, bom, multiplier):
    occrs = parentComponent.occurrences
    comps = []
    for occr in occrs:
        comps.append(occr.component)
    ucomps = []
    [ucomps.append(n) for n in comps if n not in ucomps]
    
    for ucomp in ucomps:
        # Ignore contruction components
        if "(construction)" in ucomp.name.lower():
            continue
        # Gather any BOM worthy values from the component
        mass = 0
        bodies = ucomp.bRepBodies
        for bodyK in bodies:
            if bodyK.isSolid:
                mass += bodyK.physicalProperties.mass*1000
                material = bodyK.material.name
                colour = bodyK.appearance.name
        if (((ucomp.partNumber not in ucomp.name) and ucomp.partNumber != "" and ucomp.partNumber != ucomp.partNumber)):
            partNumber = "Invalid Part Number"
        else:
            partNumber = ucomp.partNumber
        if mass == 0:
            if (ucomp.partNumber.lower() == "hardware" or ("(hardware grp)" in ucomp.name.lower())):
                massS = "--Hardware--"
                partNumber = "--Hardware--"
                colour = "--Hardware--"
                material = "--Hardware--"
                compType = "Hardware Group"
            elif (ucomp.partNumber.lower() == "machined" or ("(machined grp)" in ucomp.name.lower())):
                massS = "--Machined--"
                partNumber = "--Machined--"
                colour = "--Machined--"
                material = "--Machined--"
                compType = "Machined Group"
            elif (ucomp.partNumber.lower() == "fasteners" or ("(fasteners grp)" in ucomp.name.lower())):
                massS = "--Fasteners--"
                partNumber = "--Fasteners--"
                colour = "--Fasteners--"
                material = "--Fasteners--"
                compType = "Fasteners Group"
            elif (ucomp.partNumber.lower() == "electronics" or ("(electronics grp)" in ucomp.name.lower())):
                massS = "--Electronics--"
                partNumber = "--Electronics--"
                colour = "--Electronics--"
                material = "--Electronics--"
                compType = "Electronics Group"
            elif (ucomp.partNumber.lower() == "printed" or ("(printed grp)" in ucomp.name.lower())):
                massS = "--Printed--"
                partNumber = "--Printed--"
                colour = "--Printed--"
                material = "--Printed--"
                compType = "Printed Group"
            elif (ucomp.partNumber.lower() == "subassemblies" or ("(subassemblies grp)" in ucomp.name.lower())):
                massS = "--Subassembly--"
                partNumber = "--Subassembly--"
                colour = "--Subassembly--"
                material = "--Subassembly--"
                compType = "Subassembly Group"
            elif (parentComponent.partNumber.lower() == "subassemblies" or ("(subassemblies grp)" in parentComponent.name.lower())):
                massS = "--Subassembly--"
                colour = "--Subassembly--"
                material = "--Subassembly--"
                compType = "Subassembly Group"
            else:
                massS = "Error part has Zero Mass and is not a group"
                partNumber = "Error part has Zero Mass and is not a group"
                colour = "Error part has Zero Mass and is not a group"
                material = "Error part has Zero Mass and is not a group"
                compType = "Error part has Zero Mass and is not a group"
        else:
            # Set the type of the component based off the tags of the parent assembly
            if (parentComponent.partNumber.lower() == "hardware" or ("(hardware grp)" in parentComponent.name.lower()) ):
                compType = "Hardware"
            elif (parentComponent.partNumber.lower() == "machined" or ("(machined grp)" in parentComponent.name.lower())):
                compType = "Machined"
            elif (parentComponent.partNumber.lower() == "fasteners" or ("(fasteners grp)" in parentComponent.name.lower())):
                compType = "Fasteners"
            elif (parentComponent.partNumber.lower() == "electronics" or ("(electronics grp)" in parentComponent.name.lower())):
                compType = "Electronics"
            elif (parentComponent.partNumber.lower() == "printed" or ("(printed grp)" in parentComponent.name.lower())):
                compType = "Printed"
            elif (parentComponent.partNumber.lower() == "subassemblies" or ("(subassemblies grp)" in parentComponent.name.lower())):
                compType = "SubAssembly"
            else:
                compType = "ERROR"
            # Overwrite type if specific component is tagged
            if ("(hardware)" in ucomp.name.lower()):
                compType = "Hardware"
            elif ("(machined)" in ucomp.name.lower()):
                compType = "Machined"
            elif ("(fasteners)" in ucomp.name.lower()):
                compType = "Fasteners"
            elif ("(electronics)" in ucomp.name.lower()):
                compType = "Electronics"
            elif ("(printed)" in ucomp.name.lower()):
                compType = "Printed"
            elif ("(subassembly)" in ucomp.name.lower()):
                compType = "SubAssembly"
            
            massS = round(mass,4)
        # Remove fusion version number from name
        nameSplit = ucomp.name[::-1].split("v",1)
        if nameSplit[0].isnumeric():
            name = nameSplit[1][::-1].replace(" " + partNumber,"")
        else:
            name = ucomp.name.replace(" " + partNumber,"")
        nameSplit = parentComponent.name[::-1].split("v",1)
        if nameSplit[0].isnumeric():
            prName = nameSplit[1][::-1].replace(" " + partNumber,"")
        else:
            prName = parentComponent.name.replace(" " + partNumber,"")

        
        
        bom.append({
            'component': ucomp,
            'partNumber': partNumber,
            'name': remove_text_inside_brackets(name),
            'type': compType,
            'Per Subassembly instances': comps.count(ucomp),
            'instances': multiplier*comps.count(ucomp),
            'mass (grams)': massS,
            'material': material,
            'colour': colour,
            'parentAss': parentComponent,
            'parentName': remove_text_inside_brackets(prName),
        })
        bom = recursiveCompInfoStruct(ucomp, bom, multiplier*comps.count(ucomp))
    return bom

def recursiveCompInfoAll(group, parentComponent, bom):
    occrs = parentComponent.occurrences
    for occr in occrs:
        comp = occr.component
        jj = 0
        for bomI in bom:
            if bomI['component'] == comp:
                # Increment the instance count of the existing row.
                bomI['instances'] += 1
                break
            jj += 1
        if jj == len(bom):
            # Ignore contruction components
            if "(construction)" in comp.name:
                continue
            # Gather any BOM worthy values from the component
            mass = 0
            bodies = comp.bRepBodies
            for bodyK in bodies:
                if bodyK.isSolid:
                    mass += bodyK.physicalProperties.mass*1000
                    material = bodyK.material.name
                    colour = bodyK.appearance.name
            if (comp.partNumber == comp.name) or (comp.partNumber == "") or (len(comp.partNumber) > 9):
                partNumber = "Invalid Part Number"
            else:
                partNumber = comp.partNumber
            # Remove fusion version number from name
            nameSplit = comp.name[::-1].split("v",1)
            if nameSplit[0].isnumeric():
                name = nameSplit[1][::-1].replace(" " + partNumber,"")
            else:
                name = comp.name.replace(" " + partNumber,"")
            nameSplit = parentComponent.name[::-1].split("v",1)
            if nameSplit[0].isnumeric():
                prName = nameSplit[1][::-1].replace(" " + partNumber,"")
            else:
                prName = parentComponent.name.replace(" " + partNumber,"")
            if mass == 0:
                if (any(tag in comp.name.lower() for tag in {"(hardware grp)","(machined grp)","(fasteners grp)","(electronics grp)","(printed grp)","(subassemblies grp)"}) or not any(cat in comp.name.lower() for cat in {"hardware","machined","fasteners","electronics","printed","subassemblies"})):
                    bom = recursiveCompInfoAll(remove_text_inside_brackets(name), comp, bom)
                else:
                    bom = recursiveCompInfoAll(group, comp, bom)
                continue
            else:
                if (parentComponent.partNumber.lower() == "hardware" or ("(hardware grp)" in parentComponent.name.lower()) ):
                    compType = "Hardware"
                elif (parentComponent.partNumber.lower() == "machined" or ("(machined grp)" in parentComponent.name.lower())):
                    compType = "Machined"
                elif (parentComponent.partNumber.lower() == "fasteners" or ("(fasteners grp)" in parentComponent.name.lower())):
                    compType = "Fasteners"
                elif (parentComponent.partNumber.lower() == "electronics" or ("(electronics grp)" in parentComponent.name.lower())):
                    compType = "Electronics"
                elif (parentComponent.partNumber.lower() == "printed" or ("(printed grp)" in parentComponent.name.lower())):
                    compType = "Printed"
                elif (parentComponent.partNumber.lower() == "subassemblies" or ("(subassemblies grp)" in parentComponent.name.lower())):
                    compType = "SubAssembly"
                else:
                    compType = "ERROR"
            # Overwrite type if specific component is tagged
                if ("(hardware)" in comp.name.lower()):
                    compType = "Hardware"
                elif ("(machined)" in comp.name.lower()):
                    compType = "Machined"
                elif ("(fasteners)" in comp.name.lower()):
                    compType = "Fasteners"
                elif ("(electronics)" in comp.name.lower()):
                    compType = "Electronics"
                elif ("(printed)" in comp.name.lower()):
                    compType = "Printed"
                elif ("(subassembly)" in comp.name.lower()):
                    compType = "SubAssembly"
                massS = round(mass,4)
            bom.append({
                'component': comp,
                'partNumber': partNumber,
                'name': remove_text_inside_brackets(name),
                'type': compType,
                'instances': 1,
                'mass (grams)': massS,
                'material': material,
                'colour': colour,
                'parentAss': prName,
                'group': group
            })
        bom = recursiveCompInfoAll(group, comp, bom)
    return bom


def remove_text_inside_brackets(text, brackets="()"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else: # character is not a [balanced] bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)