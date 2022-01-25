"""Help on hxc_designer package:
Name
    hxc_designer

Description
    Heat sink design application
    =========================================
    hxc_designer is a Python module used for thermal calculations involving heatsinks.
    Its aim is to provide a basis for heat sink design optimization.

Classes:
    TBD

Functions:
    TBD

Misc Variables:
    TBD
    
"""
from heat_sink import heat_sink
from enum import Enum

class HeatSinkType(Enum):
    Straight_Rectangular = 1 
    Straight_Triangular = 2
    Straight_Parabolic = 3


