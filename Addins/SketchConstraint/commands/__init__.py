# Here you define the commands that will be added to your add-in
# If you want to add an additional command, duplicate one of the existing directories and import it here.
# You need to use aliases (import "entry" as "my_module") assuming you have the default module named "entry"
from .SketchConstraints import entry as Sketch_Constraints


# This Template will automatically call the start() and stop() functions.
# By default the order you add the commands to this list will be the order they appear in the UI
commands = [
    Sketch_Constraints,
]


# Assumes you defined a "start" function in each of your modules.
# These functions will be run when the add-in is stopped.
def start():
    for command in commands:
        command.start()


# Assumes you defined a "start" function in each of your modules.
# These functions will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()
