#Author-Freeman
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from . import Fusion360CommandBase

#import system modules
import os, sys 

#get the path of add-in
my_addin_path = os.path.dirname(os.path.realpath(__file__)) 
print(my_addin_path)

#add the path to the searchable path collection
if not my_addin_path in sys.path:
   sys.path.append(my_addin_path) 

import networkx as nx

class generateAssemblyCommand(Fusion360CommandBase.Fusion360CommandBase):
    def onPreview(self, command, inputs):
        pass
    def onDestroy(self, command, inputs, reason_):
        pass
    def onInputChanged(self, command, inputs, changedInput):
        pass
    def onExecute(self, command, inputs):
        def makeComponent(parent, name, partNumber, desc):
            occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            occ.component.name = name
            occ.component.partNumber = partNumber
            occ.component.description = desc
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
            makeComponent(comp, 'Machined', 'Machined','This subassembly stores all of the Machined components for the toplevel assembly. These are components that we have designed and either manufacture ourselves or contract an external company to manufacture exclusivly for us.')
            makeComponent(comp, 'Hardware', 'Hardware','This subassembly stores all of the Hardware for the toplevel assembly. This is primarily off the shelf components that we do not manufacture at Aeronavics.')
            makeComponent(comp, 'Electronics', 'Electronics','This subassembly stores all of Electronics for the toplevel assembly. This is generally where PCBs exported from Altium are located.')
            makeComponent(comp, 'Subassemblies', 'Subassemblies','This subassembly stores all of external included Subassembiles. When editing these Subassemblies avoid editing in context and remember that the Subassembly may be used on multiple Aircraft. Ensure changes made to Subassemblies do not break other Assemblies they are included in.')
            ui.messageBox('Assembly Tree Generated Successfully')
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


commandName1 = 'Generate Assembly Tree'
commandDescription1 = 'Generates an Assembly Tree in the active component'
commandResources1 = './resources'
cmdId1 = 'cmdID_generateAssembly'
myWorkspace1 = 'FusionSolidEnvironment'
myToolbarPanelID1 = 'SolidScriptsAddinsPanel'

debug = False

newCommand1 = generateAssemblyCommand(commandName1, commandDescription1, commandResources1, cmdId1, myWorkspace1, myToolbarPanelID1, debug)

def run(context):
    newCommand1.onRun()
def stop(context):
    newCommand1.onStop()

