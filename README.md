# vigilant-disco
A collection of useful scripts and addins for Fusion 360.
## Getting Started

### Dependencies
For the Scripts and Addins in this Repo the dependencies are included in the package. However ExtractBOM and related tools require Microsoft Excel to be installed for saving the BOM.

### Installing
Fusion 360 has scripts and addins. Scripts are designed to run once and addins are designed to continue running in the background. Some Addins are just a collection of scripts with the addin giving you the functionality of shortcut buttons. To install a Script or an Addin it must be placed in the relevent folder for fusion to detect. For Scripts this is under AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Scripts. For Addins this is under AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Addins.

If you want to make your life a bit easier you can create links to the script and addin folders in your repository rather than copying the folders across. This has the advantage of automatically updating the scripts and addins when you update the repository. A batch file for windows (CreateLinks.bat) has been supplied to do this automatically assuming your Fusion API folder is in the default location. This file must be run as an administrator by right clicking and selecting the Run As Administrator option.

### Starting Addins and running Scripts
The Scripts and Add-ins manager can be found in Fusion by opening a new design (not a drawing) and going to the utilities tab and selecting Scripts and Add-ins. Here you can run a Script by selecting it from the list and clicking run. Addins can be started and stopped via the Add-Ins tab and be configured to run on startup. By rightclicking a Script or Addin you can open the file location which can be helpful if you can't find where your Scripts and Addins are saved by default.

## Help
More detailed instructions on how a Script or Addin functions can be found in the README of the specific Script or Addin.