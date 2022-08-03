
#Author-Freeman Porten.
#Description- BOM


class BOM:

    # A list of the tags used in the BOM to group components under different types.
    # The first entry (key) is the group name and the second entry (value) is the type name.
    # In the code these are not case sensitive.
    typeTags = {
        "Hardware Grp" : "Hardware",
        "Machined Grp": "Machined",
        "Fasteners Grp": "Fasteners",
        "Electronics Grp": "Electronics",
        "Printed Grp":"Printed",
        "Subassemblies Grp": "Subassemblies",
        "Looms Grp": "Looms"
     }

    
    # The constructor for the bom object. Intialises the bom list.
    def __init__(self) -> None:
        # Setup root Bom component
        self.bomList = []
    
    # Takes an Input of the root component name and the root component part number and
    # adds these to the bom with the special formatting applied.
    def addRoot(self, rootComponentName:str, rootComponentPartNumber:str) -> None:
        rootComponentPartNumber = self.checkPartNumber(name=rootComponentName, partNumber=rootComponentPartNumber, compType="Root")
        rootComponentName = self.removeFusionVersionNumberAndPartNumber(name=rootComponentName, partNumber=rootComponentPartNumber)
        
        if not rootComponentPartNumber:
            rootComponentPartNumber = "No Part Number"
        rootComponentName = self.removeTags(textInput=rootComponentName,brackets="()")


        self.bomList.append({
        'partNumber': rootComponentPartNumber,
        'name': rootComponentName,
        'type':'Root',
        'instances': 1,
        'Per Subassembly instances': 1,
        'mass (grams)': '--Root--',
        'material': '--Root--',
        'colour': '--Root--',
        'parentName': '--Root--',
        'length (mm)': 0
        })

    # This functions adds the input part and info into the BOM.
    # depending on the sort of BOM you are generating some of the
    # entries may not be used, but they will still be populated in the entry.
    # Which outputs actually get shown in the Spreadsheet is controlled elsewhere.
    def addEntry(self, name:str, desc:str, partNumber:str, parentName:str,  parentDesc:str, parentPartNumber:str, instancesInSubassembly:int, instances:int, mass:float, material:str, color:str, length:float) -> None:
        
        # Get the component type and check the component part number
        compType = self.getCompType(name=name, desc=desc, parentName=parentName, parentDesc=parentDesc)
        partNumber = self.checkPartNumber(name=name, partNumber=partNumber, compType=compType)
        
        # Formats the Material and Color for when the component is a group and doesnt have a material or color.
        if "grp" in compType.lower() or "subassemblies" in compType.lower():
            material = "--" + compType + "--"
            color = "--" + compType + "--"
            mass = "--" + compType + "--"


        # stop errors with empty strings
        if name == "":
            name = " "

        # Remove the version number and part number from the name as well as removing any tags in the name.
        name = self.removeFusionVersionNumberAndPartNumber(name=name, partNumber=partNumber)
        name = self.removeTags( textInput = name, brackets = "()")

        # Remove the version number and part number from the Parent Name as well as removing any tags in the name.
        parentName = self.removeFusionVersionNumberAndPartNumber(name=parentName, partNumber=parentPartNumber)
        parentName = self.removeTags(textInput = parentName, brackets = "()")

        # Setup the entry to be appended to the bom. Note that just because something is
        # entered into the BOM does not mean that it gets shown in the spreadsheet. That is
        # controlled by the formatting into the spreadsheet.
        entry = {
                'partNumber': partNumber,
                'name': name,
                'type': compType,
                'instances': instances,
                'Per Subassembly instances': instancesInSubassembly,
                'mass (grams)': mass,
                'material': material,
                'colour': color,
                'parentName': parentName,
                'length (mm)': length
            }
        
        self.bomList.append(entry)
        
    
    # This functions checks that the part number is contained in the part name
    # and that the part number is a 9 digit number. It will also return the
    # formated group name if the part is a group.
    def checkPartNumber(self, name:str, partNumber:str, compType:str) -> str:
        # Check part could be a valid part number
        if (partNumber in name) and len(partNumber) == 9:
            # Check extra hard
            if (partNumber[0] == 'A' and
            partNumber[1].isnumeric() and
            partNumber[2].isnumeric() and
            partNumber[3] == '-' and
            partNumber[4].isnumeric() and
            partNumber[5].isnumeric() and
            partNumber[6].isnumeric() and
            partNumber[7].isnumeric() and
            partNumber[8].isnumeric()):
                return partNumber
                
        # Pre set to error and overwrite if not an error
        partNumber = "Invalid Part Number"

        # Check if the Part is a group and if so format the partnumber to the group name.
        for grp, type in self.typeTags.items():
            if grp == compType:
                partNumber = "--" + grp + "--"
        
        return partNumber

            
    
    # This functions removes text contained within an open and closed bracket
    # including the brackets.
    def removeTags(self, textInput:str, brackets:str="()") -> str:
        count = [0] * (len(brackets) // 2) # count open/close brackets
        saved_chars = []
        for character in textInput:
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

    # This function gets the component type of the input component. It returns the component Type as a string.
    # The typeTags dictionary can be edited to add additional types.
    def getCompType(self, name:str, desc:str, parentName:str, parentDesc:str) -> str:
        # Set the default comp type to error if no valid type found
        compType = "ERROR"

        # Strip the version Number from the component name and parent Name
        parentName = self.removeFusionVersionNumberAndPartNumber(parentName,"").lower()
        name = self.removeFusionVersionNumberAndPartNumber(name,"").lower()
        parentDesc = parentDesc.lower()

        # Loop through typeTags array
        for groupTag , typeTag in self.typeTags.items():
            # Check if parent component is a either a default group component or is tagged as a group component
            if ((parentName.lower() == typeTag.lower()) or ("("+ groupTag.lower() +")" in parentName.lower()) or ("("+ groupTag.lower() +")" in parentDesc.lower())):
                compType = typeTag

            # Overwrite type if specific component is tagged
            if (("("+ typeTag.lower() +")" in name.lower()) or ("("+ typeTag.lower() +")" in desc.lower())):
                compType = typeTag

            # Check if component is a group
            if (("("+ groupTag.lower() +")" in name.lower()) or ("("+ groupTag.lower() +")" in desc.lower()) or (typeTag.lower() == name.lower())):
                compType = groupTag

        return compType
    
    # This function strips out the fusion version number and the part number from the input component name.
    # passing False into the partNumber will prevent the part number from being removed.
    def removeFusionVersionNumberAndPartNumber(self, name:str, partNumber:str):

        # Split the string at the v to seperate the version number
        nameSplit = name[::-1].split("v",1)

        # check if FALSE has been passed in as the part number. If so do not remove the partNumber.
        if not partNumber:
            if nameSplit[0].isnumeric():
                return nameSplit[1][::-1]
            else:
                return name
        else:
            if nameSplit[0].isnumeric():
                return nameSplit[1][::-1].replace(" " + partNumber,"")
            else:
                return name.replace(" " + partNumber,"")

    # This function returns a count of the number of parts in the bom list that have the same name as the input.
    def getCountOfComp(self, name:str, partNumber:str)-> int:
        count = 0
        name = self.removeFusionVersionNumberAndPartNumber(name=name, partNumber=partNumber).lower()
        name = self.removeTags( textInput = name, brackets = "()").lower()

        for entry in self.bomList:
            if (entry['name'].lower() == name):
                count = count + 1
        return count
    
    # This function increments the instances value of the input component name in the bom list.
    # If a non zero length is given as an input the length of the part will be increased instead.
    def incrCountOfComp(self, name:str, partNumber:str, length:float = 0)-> None:
        name = self.removeFusionVersionNumberAndPartNumber(name=name, partNumber=partNumber).lower()
        name = self.removeTags( textInput = name, brackets = "()").lower()

        # If the part is a wire or something else with a length.
        if (length != 0):
            for entry in self.bomList:
                if (entry['name'].lower() == name):
                    entry['length (mm)'] = entry['length (mm)'] + length
                    return
        
        else:
            for entry in self.bomList:
                if (entry['name'].lower() == name):
                    entry['instances'] = entry['instances'] + 1
                    return
