#Author-Freeman
#Description-

import adsk.core, adsk.fusion, traceback
import adsk.drawing
import time

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
handlers = []

_exportPDFFolder = 'C:/Users/scott/Downloads'

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        docs = _app.documents
        # get f2d datafile
        datafile = None
        for df in docs:
            if df.dataFile.fileExtension == 'f2d':
                datafile = df.dataFile

        # check datafile
        if not datafile:
            _ui.messageBox('Abort because the "f2d" file cannot be found in the open documents.')
            return

        # open doc
        drawDoc :adsk.drawing.DrawingDocument = docs.open(datafile)

        # Tasks to be checked.
        targetTasks = [
            'DocumentFullyOpenedTask',
            'Nu::AnalyticsTask',
            'CheckValidationTask',
            'InvalidateCommandsTask'
        ]

        # check start task
        if not targetTasks[0] in getTaskList():
            _ui.messageBox('Task not found : {}'.format(targetTasks[0]))
            return

        # Check the task and determine if the Document is Open.
        for targetTask in targetTasks:
            while True:
                time.sleep(0.1)
                if not targetTask in getTaskList():
                    break

        # export PDF
        expPDFpath = _exportPDFFolder + drawDoc.name + '.pdf'

        draw :adsk.drawing.Drawing = drawDoc.drawing
        pdfExpMgr :adsk.drawing.DrawingExportManager = draw.exportManager

        pdfExpOpt :adsk.drawing.DrawingExportOptions = pdfExpMgr.createPDFExportOptions(expPDFpath)
        pdfExpOpt.openPDF = True
        pdfExpOpt.useLineWeights = True

        pdfExpMgr.execute(pdfExpOpt)

        # close doc
        drawDoc.close(False)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def getTaskList():
    adsk.doEvents()
    tasks = _app.executeTextCommand(u'Application.ListIdleTasks').split('\n')
    return [s.strip() for s in tasks[2:-1]]
