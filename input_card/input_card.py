"""WORK IN PROGRESS.
The main hxc_designer.py module is currently under development.
Comments outline intended functionality.
Currently the heat_sink submodule is the most complete portion of this project.

Help on hxc_designer package:
Name
    hxc_designer

Description
    Heat sink designer input cards
    =========================================
    Input card object and creation tools

Classes:
    card

Functions:
    WIP

Misc Variables:
    WIP
    
"""
import sys
sys.path.append('..')
from hxc_designer import HeatSinkType

class Card():

    # TODO Determine class structure
    # Store all load inputs in this object
    # Create a card import and export method
    # Note that the entire program flow will be derived from this
    # Create a few maps of process before coding

    def __init__(self):
        pass
    
    def __repr__(self):
        # TODO Create a better repr
        print('Heat sink designer input card.')
    
    def import_card(self):
        pass

    def export_card(self):
        pass

def create_card():
    # TODO Create card creation method
    # Determine whether card creation dialog should be here or another function
    pass

if __name__ == "__main__":
    # TODO Determine if any functionality should be here.
    c = Card()
    pass