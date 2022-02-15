"""WORK IN PROGRESS.
The main hxc_designer.py module is currently under development.
Comments outline intended functionality.
Currently the heat_sink submodule is the most complete portion of this project.

Help on hxc_designer package:
Name
    hxc_designer

Description
    Heat sink design application
    =========================================
    hxc_designer is a Python module used for thermal calculations involving heatsinks.
    Its aim is to provide a basis for heat sink design optimization.

Usage
    Inputs:
        The application works similarily to NASTRAN cards.
        Inputs cards are used to feed parameters into the analysis.
        In this instance, the input cards consist of a range of heat 
        sink  and environmental parameters.
    Analysis:
        Heat seat objects are created in line with input parameters.
        Characteristics are calculated on creation of heat sink objects.
        If environmental conditions are applied, additional parameters will
        be run across these load conditions.
    Results:
        Results are aggregated across parameters and summarized.
        These are viewable via results output files and can be visualized
        using the provided dashboard.
    Arguments:
        Use the help function on this module for additional information.

Classes:
    WIP

Functions:
    WIP

Misc Variables:
    WIP
    
"""

# TODO
# Add argparse for launch options
# Run methods:
#   CLI: Use CLI interactions to run heat_sink calculations and save results
#       Inputs: Either pass an input card or create one
#           TODO Add input card creation method/module
#       Outputs: Pass export directory as argument or activate via CLI dialog
#   GUI: Launch Plotly Dash dashboard to manage program

import sys
from enum import Enum
import argparse
import os

sys.path.append("./heat_sink")
from heat_sink import heat_sink

class HeatSinkType(Enum):
    """Enumerator to track heat_sink object type."""

    Straight_Rectangular = 1
    Straight_Triangular = 2
    Straight_Parabolic = 3

class InputState(Enum):
    """Enumerator to track the status of input cards"""

    Pending = 0
    Invalid_Card = 1
    Invalid_Path = 2
    Valid_Card = 3
    Create_Card = 4


def __arg_setup():
    parser = argparse.ArgumentParser(description="Heat Sink Designer")
    parser.add_argument("--gui", dest="gui", action="store_true", help="Launches GUI.")
    parser.add_argument(
        "-i", "--input", dest="path_input", default="", help="File path to input card."
    )
    parser.add_argument(
        "-e",
        "--export",
        dest="path_export",
        default="",
        help="File path to export directory.",
    )
    args = parser.parse_args()
    return vars(args)


def import_card(fpath):
    """Not yet implemented.
    Imports an input card for the analysis.

    Parameters
    ----------
    fpath : str
        File path to the input card.

    Returns
    -------
    card : [type]
        [description]
    """
    # TODO Create card import and verification method.
    raise NotImplementedError("Card import method not yet implemented.")
    return None  # Placeholder


def create_card():
    """Method to create a new input card."""
    # TODO Create card generation method.
    raise NotImplementedError("Card creation method not yet implemented.")
    return None  # Placeholder


def check_card(card_obj):
    """Method to verify integrity of input card.

    Parameters
    ----------
    card_obj : obj
        Input card object.

    Returns
    -------
    is_valid : bool
        If True, the card is a valid input card.

    """
    # TODO Create card object check method.
    return False


if __name__ == "__main__":
    args = __arg_setup()
    if args["gui"]:  # GUI run method
        # TODO Add GUI.
        print("GUI not yet implemented.")

    else:  # CLI run method
        # Input Card Setup
        input_status = InputState.Pending
        while input_status not in (InputState.Valid_Card, InputState.Create_Card):
            if not os.path.exists(args["path_input"]):
                if args["path_input"]:
                    # Prints only if arg was entered and file path is not valid
                    print("Invalid input file path.")
                input_status = InputState.Invalid_Path
                print(
                    "Enter the file path to a valid input card or enter !N to create a new one"
                )
                args["path_input"] = input()
            else:
                try:
                    # Import card from file path if a new card wasn't created
                    if input_status != InputState.Create_Card:
                        card = import_card(args["path_input"])

                    if check_card(card):  # Verify whether new or imported card is valid
                        input_status = InputState.Valid_Card
                    else:
                        raise Exception()
                except:  # Card creation/import was unsuccessful, try again
                    input_status = InputState.Invalid_Card
                    print(
                        "Invalid input card.\n"
                        "Enter the file path to a valid input card or enter !N to create a new one"
                    )
                    args["path_input"] = input()
            if args["path_input"] == "!N":
                card = create_card()

        # Export Directory Setup
        while not os.path.exists(args["path_export"]):
            if args["path_export"]:
                # Prints only if arg was entered and directory is not valid
                print("Directory does not exist.")
            print("Enter a directory for results export.")
            args["path_export"] = input()

        # Analysis Run
        # TODO 
        # Add heat_sink object creation from input card
        # Add results export dialog
        # Add dashboard launch option