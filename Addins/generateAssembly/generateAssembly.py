#Author-Freeman
#Description-This script generates the Subassembly component structure in the currently active component

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
        makeComponent(comp, 'Fasteners', 'Fasteners','This subassembly stores all of the fasteners for the toplevel assembly. This mainly includes nuts and bolts.')
        makeComponent(comp, 'Printed', 'Printed','This subassembly stores all of the Printed components for the toplevel assembly.')
        makeComponent(comp, 'Machined', 'Machined','This subassembly stores all of the Machined components for the toplevel assembly. These are components that we have designed and either manufacture ourselves or contract an external company to manufacture exclusivly for us.')
        makeComponent(comp, 'Hardware', 'Hardware','This subassembly stores all of the Hardware for the toplevel assembly. This is primarily off the shelf components that we do not manufacture at Aeronavics.')
        makeComponent(comp, 'Electronics', 'Electronics','This subassembly stores all of Electronics for the toplevel assembly. This is generally where PCBs exported from Altium are located.')
        makeComponent(comp, 'Subassemblies', 'Subassemblies','This subassembly stores all of external included Subassembiles. When editing these Subassemblies avoid editing in context and remember that the Subassembly may be used on multiple Aircraft. Ensure changes made to Subassemblies do not break other Assemblies they are included in.')
        ui.messageBox('Assembly Tree Generated Successfully')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def makeComponent(parent, name, partNumber, desc):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    occ.component.partNumber = partNumber
    occ.component.description = desc