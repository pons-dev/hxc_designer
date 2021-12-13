"""Help on heatsink package:
Name
    heatsink

Description
    Heat sink module for thermal applications
    =========================================
    heatsink is a Python module used for thermal calculations involving heatsinks.
    Its aim is to provide a basis for heat sink design optimization.
    It is a part of the hxc_designer module.

Classes:
    HeatSink

Functions:
    functions_example(input1, input2)

Misc Variables:
    __version__
    var1
"""

class HeatSink():
    def __init__(self, matl, base_h, 
        fin_type, n_fins, fin_l, fin_w, fin_t):
        
        #====================================================================================================
        #Input Checks
        #====================================================================================================
        #Check fin_types input:
        __allowed_fin_types = [
            'straight rectangular fin',
            'straight triangular fin',
            'straight parabolic fin'
        ]
        if fin_type.lower() not in __allowed_fin_types: #Check for correct fin type input
            err_msg = 'Invalid fin_type. \nAllowed types:\n{}'.format("\n".join(__allowed_fin_types))
            raise ValueError(err_msg)

        #Check inputs to determine whether gap size is acceptable:
        __min_gap = 0.0001
        __total_fin_width = n_fins * fin_t
        gap = ( base_h - __total_fin_width ) / (n_fins -1) #Gap between each fin
        if gap <= 0: #Catch value combinations that produce a negative fin gap size
            err_msg = f"""Base height incompatible with fin parameters.
            Zero or negative gap size produced.
            Current parameters:
                base_h: {base_h}
                n_fins: {n_fins}
                fin_t: {fin_t}
            This produces a gap size of: {gap:.5f}"""
        elif gap < __min_gap: #Catch  values that are less than minimum allowed gap size
            err_msg = f"""Base height incompatible with fin parameters.
            Current parameters:
                base_h: {base_h}
                n_fins: {n_fins}
                fin_t: {fin_t}
            This produces a gap size of: {gap:.5f}
            Minimum gap size is::        {__min_gap:.5f}"""
            raise ValueError(err_msg)

        #====================================================================================================
        #Class variable assignment:
        #====================================================================================================
        self.matl = matl #Material
        self.base_h = base_h #Height of the heat sinks base
        self.fin_type = fin_type.lower() #Type of fin
        self.n_fins = n_fins #Number of fins
        self.fin_l = fin_l #Length of heat sink fin extending perpendicular to its base 
        self.fin_w = fin_w #Width of heat sink fin extending parallel to its base
        self.fin_t = fin_t #Thickness of heat sink fin
        self.gap = gap #Gap size between fins. Assumes fins are located at ends of base and that gaps are equal



