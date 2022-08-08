#Author-Freeman
#Description-This script generates the Loom component structure in the currently active component

import adsk.core, adsk.fusion, adsk.cam, traceback

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

        comp = design.activeComponent
        makeComponent(comp, 'Wires', 'Wires','(Part Number:length:Twisted Pair:Connector ID 1:Pin 1:Method 1:Connector ID 2:Pin 2:Method 2)')
        makeComponent(comp, 'Plugs','Plugs','(Part Number:Connector ID)')
        makeComponent(comp, 'Crimps','Crimps','(Part Number:Crimp Type ID:Instances)')
        makeComponent(comp, 'Loom Electronics','Loom Electronics','(Part Number:Connector ID)')
        makeComponent(comp, 'Consumables','Consumables','(Part Number:Instances:Length:Mass)')
        ui.messageBox('Loom Generated Successfully')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def makeComponent(parent, name, partNumber, desc):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    occ.component.partNumber = partNumber
    occ.component.description = desc