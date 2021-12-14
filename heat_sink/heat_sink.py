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
import numpy as np
import pandas as pd

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
        self.fin_efficiency = self.__calc_fin_efficiency() #Fin efficiency (aka Nu)
        self.fin_area_single = self.__calc_fin_area_single() #Fin surface area for a single fin (along the length/width plane)
        self.fin_area_total = self.__calc_fin_area_total() #Total fin surface area (along the length/width plane)
        self.base_area_tot = self.__calc_base_area_tot() #Total base cross-sectional area, disregarding fins
        self.base_area_nonfin = self.__calc_base_area_nonfin #Exposed base area, excluding area taken up by fins
        self.fin_effectiveness = self.__calc_fin_effectiveness() #Fin effectiveness (aka epsilon_fin)
        self.overall_fin_effectiveness = self.__calc_overall_fin_effectiveness() #Overall effectiveness (aka epsilon_fin_overall)
    #========================================================================================================
    #Fin characteristic calculations
    #========================================================================================================
    def __calc_fin_characteristic_length(self):
        """Calculates fin characteristic length.
        Applicable only to fin where there is surface area at the tip of the fin.

        Returns
        -------
        length_characeteristic : float
            Characteristic length used to account for heat transfer via the tip of the fin.

        Raises
        ------
        ValueError
            If fin_type is not an allowed value.
        """
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
        """Calculate non-dimensional parameter m.
        Used for efficiency calculations.

        Returns
        -------
        param_m : float
            Non-dimensional parameter for efficiency calculations.

        Raises
        ------
        ValueError
            If fin_type is not an allowed value.
        """
        fins_rect = ['straight rectangular fin', 'straight triangular fin', 'straight parabolic fin']
        if self.fin_type in fins_rect:
            param_m = sqrt( (2 * self.matl.coeff_h) / (self.matl.coeff_k * self.fin_thk) )
        else: #Catch invalid fin types
            raise ValueError('Parameter m not calculated for fin type.')
        return param_m

    def __calc_param_c(self):
        """Calculate non-dimensional parameter C.
        Used for curved fin profiles calculations.

        Returns
        -------
        param_c1 : float
            Non-dimensional parameter C

        Raises
        ------
        ValueError
            If fin_type is not an allowed value.
        """
        if self.fin_type == 'straight rectangular fin':
            param_c1 = None
        elif self.fin_type == 'straight triangular fin':
            param_c1 = None
        elif self.fin_type == 'straight parabolic fin':
            param_c1 = sqrt(1 + ( self.fin_thk / self.fin_len )**2)
        else: #Catch invalid fin types
            raise ValueError('Parameter C1 not calculated for fin type.')

        return param_c1

    def __calc_fin_efficiency(self):
        """Calculates fin efficiency, aka nu_fin.
        nu_fin = Q_fin / Q_fin_max.
        Q_fin_actual : Actual fin heat transfer rate.
        Q_fin_ideal : Ideal, maximum heat transfer rate assuming the
                entire fin temperature matches that of the base.

        Theory:
        The actual temperature of the fin at given point along its length
        will be lower than the temperature of the base. Heat transfer
        will be greater when the delta temperature between the fin and the
        surrounding environment is greater. Thus fin efficiency compares
        the actual heat transfer rate (Q_fin_actual), where temperature is not uniform,
        to an ideal heat transfer rate (Q_fin_ideal), where temperature is
        uniform and maximum. Fin efficiency varies only as a function of fin
        geometry. Thus this parameter allows us to evaluate heat transfer rate
        efficiency based on the fin profile.

        Returns
        -------
        fin_efficiency : float
            Fin efficiency value Q_fin_actual / Q_fin_ideal.

        Raises
        ------
        ValueError
            If fin_type is not an allowed value.
        """
        if self.fin_type == 'straight rectangular fin':
            # nu_fin = tanh(m * L_c) / (m * L_c)
            fin_efficiency = tanh(self.fin_param_m * self.fin_len_char) / (self.fin_param_m * self.fin_len_char)
        elif self.fin_type == 'straight triangular fin':
            # nu_fin = (1/(m*L))*(I_1(2*m*L)/I_0(2*m*L))
            #Calls a Bessel function. Verify that this is the correct implementation
            fin_efficiency = (1 / (self.fin_param_m * self.fin_len) ) * (iv(1, 2*self.fin_param_m*self.fin_len)/iv(0, 2*self.fin_param_m*self.fin_len))
        elif self.fin_type == 'straight parabolic fin':
            # nu_fin = 2 / ( 1 + sqrt( (2*m*L)^2 + 1 ) )
            fin_efficiency = 2 / ( 1 + sqrt( ( 2 * self.fin_param_m * self.fin_len ) + 1) )
        else: #Catch invalid fin types
            raise ValueError('Fin efficiency not calculated for fin type.')
        return fin_efficiency

    def __calc_fin_area_single(self):
        """Calculates the surface area of a single fin.
        Calculated along the L/w plane.
        Assumes L/t plane effects are negligible.

        Returns
        -------
        fin_area_single : float
            Fin surface area.

        Raises
        ------
        ValueError
            If fin_type is not an allowed value.
        """
        if self.fin_type == 'straight rectangular fin':
            # A_fin = 2*w*L_c
            fin_area_single = 2 * self.fin_wid * self.fin_len_char
        elif self.fin_type == 'straight triangular fin':
            # A_fin = 2 * w * sqrt(L^2 + (t/2)^2)
            fin_area_single = 2 * self.fin_wid * sqrt( self.fin_len**2 + ( self.fin_thk / 2 )**2 )
        elif self.fin_type == 'straight parabolic fin':
            #Note: math.log() is the natural logarithm (aka ln), hence renaming on import
            # A_fin = w*L * [ C_1 + (L/t)*ln( t/L + C_1) ]
           fin_area_single = self.fin_wid * self.fin_len * (self.param_c + \
               ( self.fin_len / self.fin_thk ) * ln( self.fin_thk / self.fin_len + self.param_c ) )
        else: #Catch invalid fin types
            raise ValueError('Fin efficiency not calculated for fin type.')
        return fin_area_single
    
    def __calc_fin_area_total(self):
        """Calculates total fin surface area.
        Calculated along the L/w plane.
        Assumes L/t plane effects are negligible.

        Returns
        -------
        fin_area_total : float
            Total fin surface area.
        """
        fin_area_total = self.fin_area_single * self.n_fins
        return fin_area_total

    def __calc_base_area_tot(self):
        """Calculates total base area.
        Assumes fin width expands entire base length.

        Returns
        -------
        base_area_total : float
            Total base area.
        """
        base_area_total = self.base_h * self.fin_wid #Fin assumed to span entire base length
        return base_area_total
    
    def __calc_base_area_nonfin(self):
        """Calculates exposed base area.

        Returns
        -------
        base_area_nonfin : float
            Base area exposed to environment.

        Raises
        ------
        ValueError
            If fin_type is not an allowed value.
        """
        #Fins with rectangular bases
        fins_rect = ['straight rectangular fin', 'straight triangular fin', 'straight parabolic fin']
        if self.fin_type in fins_rect:
            base_area_nonfin = self.base_area_tot - self.n_fins * self.fin_thk * self.fin_wid
        else: #Catch invavlid fin types
            raise ValueError('Base area calculations only valid for supported rectangular fin types.')
        return base_area_nonfin
    
    def __calc_fin_effectiveness(self):
        """Calculates fin effecitveness, aka epsilon_fin.
        epsilon_fin = Q_fin / Q_nofin
        Q_fin : Heat transfer rate of the fins.
        Q_nofin : Heat transfer rate of the base area, assuming no fins present.
        This value compares the heat transfer rate of the fins to the
        heat transfer rate if no fins were present.

        Returns
        -------
        fin_effectiveness
            Ratio of heat transfer rate of heat sink relative to if no fins were present.
            Q_fin / Q_nofin

        Raises
        ------
        ValueError
            If fin_type is not an allowed value.
        """

        fins_rect = ['straight rectangular fin', 'straight triangular fin', 'straight parabolic fin']
        if self.fin_type in fins_rect:
            # epsilon_fin = nu_fin * (A_fin / A_fin_base)
            area_fin_base = self.fin_wid * self.fin_thk
            fin_effectiveness = self.fin_efficiency * self.fin_area_total / area_fin_base
        else: #Catch invavlid fin types
            raise ValueError('Base area calculations only valid for supported rectangular fin types.')
        return fin_effectiveness
        
    def __calc_overall_fin_effectiveness(self):
        """Calculates overall fin effectiveness, aka epsilon_fin_overall
        Accounts for exposed base area in fin effectiveness calculations.
        epsilon_fin_overall = Q_fin_total / Q_nofin
        Q_fin_total : Total heat transfer rate of fin surface area and exposed base surface area.

        Reduced equation:
        Q_nofin : Heat transfer rate of the base area, assuming no fins present.
        epsilon_fin_overall = ( A_base_nonfin + nu_fin * A_fin ) / A_base_tot
        A_base_nonfin : Exposed base surface area.
        nu_fin : Fin efficiency.
        A_fin : Fin surface area.
        A_base_total : Total base surface area if no fins were present.

        Returns
        -------
        overall_fin_effectiveness : float
            Ratio of heat transfer rate of the heat sink over the heat transfer rate of the
            base surface with no fins.
        """

        # epsilon_fin_overall = ( A_base_nonfin + nu_fin * A_fin ) / A_base_tot
        overall_fin_effectiveness = ( self.base_area_nonfin + self.fin_efficiency * self.fin_area_total ) / self.base_area_tot
        return overall_fin_effectiveness

    #========================================================================================================
    #Optimization utilities
    #========================================================================================================
    def suggest_fin_length(matl_name, fin_type, fin_thk,
                            return_type='df', verbose=True):
        """Calculate suggested fin lengths for a given material, fin type, and fin thickness.
        For most uses, mL = 1.0 to 1.5 should be appropriate. Values exceeding mL = 5.0 result
        in negligible performance increase. The corresponding length should be considered the max.

        Theory:
        As length increases, the ratio between heat transfer of the fin and that of an infinitely
        long fin approaches 1 (Q_fin / Q_fin_inf = tanh(m*L)). Since this is a function of
        hyperbolic tangent, the function rapidly approaches 1 when the value of m*L approach 5.0.
        Thus 5.0 should be considered the maximum allowed length of a fin.
            mL     Q Ratio
            1.0    0.762
            1.5    0.905
            2.0    0.964
            2.5    0.987
            3.0    0.995
            4.0    0.999
            5.0    1.000

        Parameters
        ----------
        matl_name : str
            Material name.
            Allowed inputs:
                a
                b
        fin_type : str
            Fin types.
            Allowed inputs:
                'straight rectangular fin',
                'straight triangular fin',
                'straight parabolic fin'
        fin_thk : float
            Fin thickness.
        return_type : str, optional
            Data type of the return, by default 'df'.
            Allowed inputs:
                'pd': Returns a pandas DataFrame
                'np': Returns a numpy array
                'l' : Returns a list
        verbose : bool, optional
            Prints results, by default True

        Returns
        -------
        pd.Dataframe or np.array or list
            Array-like type that depends on return_type input.
            Columns:
                Fin Length : Length of the fin perpendicular to its base.
                Q Ratio : Heat transfer ratio Q_fin / Q_fin_inf,
                            where Q_fin_inf has the same fin profile, but infinite length.
                mL : Value of parameter m * fin length. Q Ratio = tanh(m*L).

        Raises
        ------
        ValueError
            Invalid input parameter values. Check allowed input values in docstring.
        """
        matl = Material(matl_name) #Material object for material coefficients

        #Calculate param_m
        if fin_type == 'straight rectangular fin':
            param_m = sqrt( (2 * matl.coeff_h) / (matl.coeff_k * fin_thk) )
        elif fin_type == 'straight triangular fin':
            param_m = sqrt( (2 * matl.coeff_h) / (matl.coeff_k * fin_thk) )
        elif fin_type == 'straight parabolic fin':
            param_m = sqrt( (2 * matl.coeff_h) / (matl.coeff_k * fin_thk) )
        else: #Catch invalid fin types
            raise ValueError('Parameter m not calculated for fin type.')
        
        length_suggestions = [] #Initialize list for length data
        coeffs = [0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0] #m*L values
        for coeff in coeffs:
            fin_len = param_m / coeff
            hx_ratio = tanh(param_m * fin_len)
            length_suggestions.append([fin_len, hx_ratio, coeff])

        if verbose or return_type.lower() in ['df', 'pd', 'dataframe', 'pandas']:
            #Create dataframe for either verbose mode or dataframe return
            df = pd.DataFrame(length_suggestions,
                                columns=[
                                    'Fin Length',
                                    'Q Ratio',
                                    'mL'
                                    ]
                                )
            if verbose: 
                print(f'Suggested fin lengths:\n{df}') #Print out calculations in verbose mode (Default)
            if return_type.lower() in ['df', 'pd', 'dataframe', 'pandas']:
                return df #Return pd.DataFrame for specified return_type values (Default)
        elif return_type.lower() in ['arr', 'np', 'array', 'numpy']:
            arr = np.array(length_suggestions) #Return np.array for specificied return_type values
        elif return_type.lower() in ['l', 'list']:
            return length_suggestions #Return list for specified return_type values
        elif not return_type:
            pass
        else:
            raise ValueError('Invalid entry for return_type.')


    #========================================================================================================
    #Heat transfer calculations
    #========================================================================================================
    def calc_q_fin_single(self, temp_base, temp_env):
        """Calculate heat transfer rate for a single fin.
        Q_fin = nu_fin * h * A_fin * (temp_base - temp_env)
        Q_fin : Heat transfer rate of a single fin.
        nu_fin : Fin efficiency.
        A_fin : Surface area of a single fin.
        temp_base : Temperature of the base.
        temp_env : Temperature of the environment.

        Parameters
        ----------
        temp_base : int or float
            Temperature of the base.
        temp_env : int or float
            Temperature of the environment.

        Returns
        -------
        q_fin : float
            Heat transfer rate of a single fin.
        """
        #Q_fin = nu_fin * h * A_fin * (T_base - T_inf)
        delta_t = temp_base - temp_env
        q_fin = self.fin_efficiency * self.matl.coeff_h * self.fin_area_single * delta_t
        return q_fin

    def calc_q_fin_total(self, temp_base, temp_env):
        """Calculate heat transfer rate of all fin area.
        Q_fin = nu_fin * h * A_fin * (temp_base - temp_env)
        Q_fin : Heat transfer rate of all fin area.
        nu_fin : Fin efficiency.
        A_fin : Surface area of all fins.
        temp_base : Temperature of the base.
        temp_env : Temperature of the environment.

        Parameters
        ----------
        temp_base : int or float
            Temperature of the base.
        temp_env : int or float
            Temperature of the environment.

        Returns
        -------
        q_fin : float
            Heat transfer rate of all fin area.
        """
        #Q_fin = nu_fin * h * A_fin * (T_base - T_inf)
        delta_t = temp_base - temp_env
        q_fin = self.fin_efficiency * self.matl.coeff_h * self.fin_area_total * delta_t
        return q_fin

    def calc_q_heat_sink(self, temp_base, temp_env):
        """Calculate heat transfer rate of the heat sink.
        Q_heat_sink = h * (A_nonfin + nu_fin * A_fin) * (temp_base - temp_env)
        Q_heat_sink : Heat transfer rate of heat sink.
        A_nonfin : Exposed surface area of the base.
        nu_fin : Fin efficiency.
        A_fin : Surface area of all fins.
        temp_base : Temperature of the base.
        temp_env : Temperature of the environment.

        Parameters
        ----------
        temp_base : int or float
            Temperature of the base.
        temp_env : int or float
            Temperature of the environment.

        Returns
        -------
        q_heat_sink : float
            Heat transfer rate of all fin area.
        """
        #Q_fin = h * (A_nonfin + nu_fin * A_fin) * (T_base - T_inf)
        delta_t = temp_base - temp_env
        area_effective = self.base_area_nonfin + self.fin_efficiency * self.fin_area_total #Effective surface area
        q_heat_sink = self.matl.coeff_h * area_effective * delta_t
        return q_heat_sink

if __name__ == '__main__':
    print('Test')
