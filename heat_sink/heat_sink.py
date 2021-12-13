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
from materials.materials import Material
from math import log as ln, sqrt as sqrt, tanh as tanh
from scipy.special import iv #Modified Bessel function

class HeatSink():
    def __init__(self, matl_name, base_h, 
        fin_type, n_fins, fin_len, fin_wid, fin_thk):
        
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
        __total_fin_width = n_fins * fin_thk
        gap = ( base_h - __total_fin_width ) / (n_fins -1) #Gap between each fin
        if gap <= 0: #Catch value combinations that produce a negative fin gap size
            err_msg = f"""Base height incompatible with fin parameters.
            Zero or negative gap size produced.
            Current parameters:
                base_h: {base_h}
                n_fins: {n_fins}
                fin_t: {fin_thk}
            This produces a gap size of: {gap:.5f}"""
        elif gap < __min_gap: #Catch  values that are less than minimum allowed gap size
            err_msg = f"""Base height incompatible with fin parameters.
            Current parameters:
                base_h: {base_h}
                n_fins: {n_fins}
                fin_t: {fin_thk}
            This produces a gap size of: {gap:.5f}
            Minimum gap size is::        {__min_gap:.5f}"""
            raise ValueError(err_msg)

        #====================================================================================================
        #Class variable assignment:
        #====================================================================================================
        #Input parameters
        self.matl = Material(matl_name) #Material
        self.base_h = base_h #Height of the heat sinks base
        self.fin_type = fin_type.lower() #Type of fin
        self.n_fins = n_fins #Number of fins
        self.fin_len = fin_len #Length of heat sink fin extending perpendicular to its base 
        self.fin_wid = fin_wid #Width of heat sink fin extending parallel to its base
        self.fin_thk = fin_thk #Thickness of heat sink fin
        self.gap = gap #Gap size between fins. Assumes fins are located at ends of base and that gaps are equal

        #Derived parameters
        self.fin_len_char = self.__calc_fin_characteristic_length() #Calculate characteristic length
        self.fin_param_m = self.__calc_fin_param_m() #Non-dimensional parameter used in fin calculations
        self.param_c = self.__calc_param_c() #Non-dimensional parameter for curved fins
        self.fin_eff = self.__calc_fin_efficiency() #Fin efficiency (aka Nu)
        self.fin_area = self.__calc_fin_area() #Fin surface area (along the length/width plane)

    #========================================================================================================
    #Fin characteristic calculations
    #========================================================================================================
    def __calc_fin_characteristic_length(self):
        if self.fin_type == 'straight rectangular fin':
            length_characteristic = self.fin_len + self.fin_thk/2
        elif self.fin_type == 'straight triangular fin':
            length_characteristic = None #Not applicable to this fin type
        elif self.fin_type == 'straight parabolic fin':
            length_characteristic = None #Not applicable to this fin type
        else: #Catch invalid fin types
            raise ValueError('Characteristic length not established for fin type.')
        return length_characteristic
    
    def __calc_fin_param_m(self):
        if self.fin_type == 'straight rectangular fin':
            param_m = sqrt( (2 * self.matl.coeff_h) / (self.matl.coeff_k * self.thk) )
        elif self.fin_type == 'straight triangular fin':
            param_m = sqrt( (2 * self.matl.coeff_h) / (self.matl.coeff_k * self.thk) )
        elif self.fin_type == 'straight parabolic fin':
            param_m = sqrt( (2 * self.matl.coeff_h) / (self.matl.coeff_k * self.thk) )
        else: #Catch invalid fin types
            raise ValueError('Parameter m not calculated for fin type.')
        return param_m

    def __calc_param_c(self):
        if self.fin_type == 'straight rectangular fin':
            param_c1 = None
        elif self.fin_type == 'straight triangular fin':
            param_c1 = None
        elif self.fin_type == 'straight parabolic fin':
            param_c1 = sqrt(1 + ( self.fin_thk / self.fin_len )**2)
            fin_eff = 2 / ( 1 + sqrt( ( 2 * self.fin_param_m * self.fin_len ) + 1) )
        else: #Catch invalid fin types
            raise ValueError('Parameter C1 not calculated for fin type.')

        return param_c1

    def __calc_fin_efficiency(self):
        if self.fin_type == 'straight rectangular fin':
            #fin_eff = tanh(m * L_c) / (m * L_c)
            fin_eff = tanh(self.fin_param_m * self.fin_len_char) / (self.fin_param_m * self.fin_len_char)
        elif self.fin_type == 'straight triangular fin':
            # nu_fin = (1/(m*L))*(I_1(2*m*L)/I_0(2*m*L))
            #Calls a Bessel function. Verify that this is the correct implementation
            fin_eff = (1 / (self.fin_param_m * self.fin_len) ) * (iv(1, 2*self.fin_param_m*self.fin_len)/iv(0, 2*self.fin_param_m*self.fin_len))
        elif self.fin_type == 'straight parabolic fin':
            fin_eff = 2 / ( 1 + sqrt( ( 2 * self.fin_param_m * self.fin_len ) + 1) )
        else: #Catch invalid fin types
            raise ValueError('Fin efficiency not calculated for fin type.')
        return fin_eff

    def __calc_fin_area(self):
        if self.fin_type == 'straight rectangular fin':
            # A_fin = 2*w*L_c
            fin_area = 2 * self.fin_wid * self.fin_len_char
        elif self.fin_type == 'straight triangular fin':
            # A_fin = 2 * w * sqrt(L^2 + (t/2)^2)
            fin_area = 2 * self.fin_wid * sqrt( self.fin_len**2 + ( self.fin_thk / 2 )**2 )
        elif self.fin_type == 'straight parabolic fin':
            #Note: math.log() is the natural logarithm (aka ln), hence renaming on import
            # A_fin = w*L * [ C_1 + (L/t)*ln( t/L + C_1) ]
           fin_area = self.fin_wid * self.fin_len * (self.param_c + \
               ( self.fin_len / self.fin_thk ) * ln( self.fin_thk / self.fin_len + self.param_c ) )
        else: #Catch invalid fin types
            raise ValueError('Fin efficiency not calculated for fin type.')
        return fin_area
    
    #========================================================================================================
    #Heat transfer calculations
    #========================================================================================================


if __name__ == '__main__':
    print('Test')
