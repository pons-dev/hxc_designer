"""Help on heat_sink package:
Name
    heat_sink

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


References:
    Cengel, Y.A. & Ghajar, A.J., (2015).
        Heat and Mass Transfer: Fundamentals & Applications, 5th Ed.
        McGraw Hill-Education, New York, NY.
    
"""
from math import log as ln, sqrt as sqrt, tanh as tanh
from scipy.special import iv #Modified Bessel function
import numpy as np
import pandas as pd

from abc import ABC, abstractmethod
from hx_equations import HeatTransfer
from hx_coefficients import HxCoefficient


#============================================================================================================
#Class Definitions (Parents):
#============================================================================================================

"""
TODO:
Implement a main class that is inhereted by the subclasses
Create:
    __HeatSinkBase parent
        Abstract base class of primary heat sink equations
            Purpose: Make it so that it's easy to create new child classes for new heat sink types
        Note: Current derived parameter definitions come from the __init__ method
            Determine the optimimum way do this
            This might involve abstract class methods
            See: 
                https://stackoverflow.com/questions/25062114/calling-child-class-method-from-parent-class-file-in-python
                https://docs.python.org/2/library/abc.html
            Check whether this is a good way to implement this, it might be overly convoluted
            Also, consider what methods are actually required for each calculation
                Some may be unique to certain types of heat sink
                Thus you may not want to implement the same initialization calculation methods
            Actually, great idea here:
                Abstract method for "__calc_derived_params"
                This will contain all calculation equations required for EACH heat sink type
                Allows certain equations to be included/excluded (e.g. characteristic length)
                I like this idea, go with this
        Internal?: Yes
        Used
    HeatTransferEq parent
        Shared heat transfer equations
        Internal?
    Optimization parent
        Shared optimization parent
        Internal?
Then:
    Create a Child class for each type of class
    Basically, copy and paste the current HeatSink() three times
    Remove if/else statements and shared class parameters
"""

#========================================================================================================
#Heat transfer calculations
#========================================================================================================


#Example of abstract class
#This results in isinstance(___, Container) to be true if it has a __contains method
#Use something similar
#Just list all required subclass method that allow it to be true
#Should look into if there are attributes techniques as well
# class Container(metaclass=ABCMeta):
#     __slots__ = ()

#     @abstractmethod
#     def __contains__(self, x):
#         return False

#     @classmethod
#     def __subclasshook__(cls, C):
#         if cls is Container:
#             if any("__contains__" in B.__dict__ for B in C.__mro__):
#                 return True
#         return NotImplemented

#Also, use common methods like __repr__

#Another idea: getter/setters
#Use this only on something like fin_type
#to prevent users from swapping the type without changing the child class
#Note: make sure to call the calc_dervied function after all setters are called
# class Protective(object):
#     """protected property demo"""
#     #
#     def __init__(self, start_protected_value=0):
#         self.protected_value = start_protected_value
#     # 
#     @property
#     def protected_value(self):
#         return self._protected_value
#     #
#     @protected_value.setter
#     def protected_value(self, value):
#         if value != int(value):
#             raise TypeError("protected_value must be an integer")
#         if 0 <= value <= 100:
#             self._protected_value = int(value)
#         else:
#             raise ValueError("protected_value must be " +
#                              "between 0 and 100 inclusive")
#     #
#     @protected_value.deleter
#     def protected_value(self):
#         raise AttributeError("do not delete, protected_value can be set to 0")



# Example using abstract method on properties
# class Animal(ABC):
#     @property                 
#     def food_eaten(self):     
#         return self._food

#     @food_eaten.setter
#     def food_eaten(self, food):
#         if food in self.diet:
#             self._food = food
#         else:
#             raise ValueError(f"You can't feed this animal with {food}.")

#     @property
#     @abstractmethod
#     def diet(self):
#         pass

#     @abstractmethod 
#     def feed(self, time):
#         pass

# class Lion(Animal):
#     @property                 
#     def diet(self):     
#         return ["antelope", "cheetah", "buffaloe"]

#     def feed(self, time):
#         print(f"Feeding a lion with {self._food} meat! At {time}") 

# class Snake(Animal):
#     @property                 
#     def diet(self):     
#         return ["frog", "rabbit"]

#     def feed(self, time): 
#         print(f"Feeding a snake with {self._food} meat! At {time}") 

"""
BIG NOTE:
Currently, you can't call _calc_derived_params() in the setter
This will cause failures and increased run times on initialization
TODO: Figure out an alternate method.
Options
    1) Unify setter methods
        I'm not a big fan of this option.
    2) Initialize all objects as 0
        In this method, _calc_derived_params() would check for 0s and not run if present
        Potentially creates issues with new derived classes
        No values should be zero though, so this might work
    3) Use a bool to determine if init is running
        Set this before initial objects
        _calc_derived_params() checks for it
        Once input objects are set, flip the value and run _calc_derived_params()
        Currently, this is my favorite method

ANOTHER BIG NOTE:
Some of the fin parameters below belong only to rectangular fin types
Move those to "RectangularHeatSink" subclass,
then put the three equations in another sublcass of that one.
These would be w, t. Maybe base_h too. L can stay in HeatSink
"""

class HeatSink(ABC):
    def __init__(self, hx_coeff, fin_type, base_h, n_fins, fin_len, fin_wid, fin_thk):
        
        self.hx_coeff = hx_coeff # hx_coefficient.HeatTransfer object
        self.fin_type = fin_type # Type of fin, governs derived parameter equations/functions
        self.base_h = base_h # Height of the base plate
        self.n_fins = n_fins # Number of fins
        self.fin_len = fin_len # Length of the fin
        self.fin_wid = fin_wid # Width of the fin, 
        self.fin_thk = fin_thk # Thickness of the fin

        _min_gap = 0.0001
        _total_fin_width = n_fins * fin_thk
        self.gap = ( base_h - _total_fin_width ) / (n_fins - 1) #Gap between each fin
    #========================================================================================================
    #Abstract Properties
    #========================================================================================================
    @property
    @abstractmethod
    def fin_type(self):
        """Fin type. Governs which equations are used. New fin types should be incorporated in a subclass.
        Note: Inherited classes should prevent deletion of this property using @fin_type.deleter
        """
        pass

    @property
    @abstractmethod
    def hx_coeff(self):
        """HxCoefficient object. See hx_coefficient documentation on implementation.
        Any object with obj.h and obj.k attributes are acceptable as inputs.
        """
        pass

    #========================================================================================================
    #Abstract Methods
    #========================================================================================================
    @abstractmethod
    def _calc_derived_params():
        """General function to run calculations on all derived parameters.
        Should be called on initialization of class.
        Should be calced when the user changes any input parameter.
        """
        pass

    @abstractmethod
    def _calc_fin_efficiency(self):
        pass

    @abstractmethod
    def _calc_fin_effectiveness(self):
        pass

    @abstractmethod
    def _calc_overall_fin_effectiveness(self):
        pass

    @abstractmethod
    def _calc_fin_area_single(self):
        pass

    @abstractmethod
    def _calc_fin_area_total(self):
        pass

    @abstractmethod
    def _calc_base_area_nonfin(self):
        pass

    #========================================================================================================
    #Inherited Properties w/ Input Validation
    #========================================================================================================
    @property
    def base_h(self):
        return self._base_h

    @base_h.setter
    def base_h(self, base_height):
        if base_height > 0:
            self._base_h = base_height
        else:
            raise ValueError('Base height must be greater than 0.')

    @property
    def n_fins(self):
        return self._n_fins
    
    @n_fins.setter
    def n_fins(self, n_fins)
        if n_fins >= 2 and type(n_fins)==int:
            self._n_fins = n_fins
        else:
            if type(n_fins) != int:
                raise TypeError('Number of fins must be an integer.')
            else:
                raise ValueError('')

    @property
    def fin_len(self):
        return self._fin_len

    @fin_len.setter
    def fin_len(self, fin_length):
        if fin_len > 0:
            self._fin_len = fin_length
        else:
            raise ValueError('Fin length must be greater than 0.')

    @property
    def fin_wid(self):
        return self._fin_wid
    
    @fin_wid.setter
    def fin_wid(self, fin_width):
        if fin_width > 0:
            self._fin_wid = fin_width
        else:
            raise ValueError('Fin width must be greater than 0')

    @property
    def fin_thk(self):
        return self._fin_thk
    
    @fin_thk.setter
    def fin_thk(self, fin_thickness):
        if fin_thickness > 0:
            self._fin_thk = fin_thickness
        else:
            raise ValueError('Fin thickness must be greater than 0')
    
    @property
    def gap(self):
        return self._gap

    @gap.setter
    def gap(self, gap_dist):
        if gap_dist <= 0: #Catch value combinations that produce a negative fin gap size
            err_msg = f"""Base height incompatible with fin parameters.
            Zero or negative gap size produced.
            Current parameters:
                base_h: {self.base_h}
                n_fins: {self.n_fins}
                fin_t: {self.fin_thk}
            This produces a gap size of: {gap_dist:.5f}"""
        elif gap < self._min_gap: #Catch  values that are less than minimum allowed gap size
            err_msg = f"""Base height incompatible with fin parameters.
            Current parameters:
                base_h: {self.base_h}
                n_fins: {self.n_fins}
                fin_t: {self.fin_thk}
            This produces a gap size of: {gap_dist:.5f}
            Minimum gap size is::        {self._min_gap:.5f}"""
            raise ValueError(err_msg)
        else:
            self._gap = gap_dist


#============================================================================================================
#Class Definitions (Children):
#============================================================================================================
class HeatSink():
    def __init__(self, hx_coeff, base_h, fin_type, n_fins, fin_len, fin_wid, fin_thk):
        """HeatSink object for heat transfer calculations.
        Assumptions:
            Geometry:
                - Fins extend from end-to-end of the base plate.
                    - Total base area = base height * fin width
                - Fins are located on either end of base plate. (minimum 2 fins)
            Heat Transfer:
                - Heat conduction is steady and one dimensional.
                - Radiative heat transfer is negligible.
                - The effect of heat transfer from the L/t plane faces is negligible.
                - Temperature across the base plate of the heat sink is uniform.
            Properties:
                - Thermal conducitivity coefficient k is uniform across the heat sink.
                - Convection coefficient h is uniform across the heat sink.

        Parameters
        ----------
        hx_coeff : HxCoefficient object
            Heat transfer coefficient object containing h and k values.
        base_h : float
            Height of the base plate.
            Perpendicular to fin length and fin width vectors.
            Total base area assumed to be base_h * fin_wid.
            Parallel to fin thickness vector.
        fin_type : str
            Profile category of the fin
            Allowable inputs:
                'straight rectangular fin'
                'straight triangular fin'
                'straight parabolic fin'
        n_fins : int
            Number of fins. Minimum of 2
        fin_len : float
            Length of the fin.
            Normal to the base plate surface plane.
        fin_wid : float
            Width of the fin.
            Perpendicular to base height and fin length vectors.
            Assumed to span end-to-end of the base plate.
        fin_thk : float
            Thickness of the fin.
            Perpendicular to the fin width and length vectors.

        Raises
        ------
        ValueError
            Input values do not match allowed values.
        TypeError
            Input values have an incorrect type.
        """
        #====================================================================================================
        #Input Checks
        #====================================================================================================
        #Internal paraments for fin type checking:
        self.__allowed_fin_types = [
            'straight rectangular fin',
            'straight triangular fin',
            'straight parabolic fin'
        ] #Used for error checking

        self.__rectangular_base_fin_types = [
            'straight rectangular fin',
            'straight triangular fin',
            'straight parabolic fin'
        ] #Used for formula selection

        #Check fin_types input:
        if fin_type.lower() not in self.__allowed_fin_types: #Check for correct fin type input
            err_msg = 'Invalid fin_type. \nAllowed types:\n{}'.format("\n".join(self.__allowed_fin_types))
            raise ValueError(err_msg)

        #Check n_fins input:
        if n_fins < 2:
            raise ValueError('n_fins must be a minimum of 2')
        elif type(n_fins) != int:
            raise TypeError('n_fins must be an integer')
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
        self.hx_coeff = hx_coeff #HxCoefficient object for k and h values
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
    def _calc_fin_characteristic_length(self):
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
    
    def _calc_fin_param_m(self):
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
        if self.fin_type in self.__rectangular_base_fin_types:
            param_m = sqrt( (2 * self.hx_coeff.h) / (self.hx_coeff.k * self.fin_thk) )
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

    def _calc_fin_efficiency(self):
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

    def _calc_fin_area_single(self):
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
    
    def _calc_fin_area_total(self):
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

    def _calc_base_area_tot(self):
        """Calculates total base area.
        Assumes fin width expands entire base length.

        Returns
        -------
        base_area_total : float
            Total base area.
        """
        base_area_total = self.base_h * self.fin_wid #Fin assumed to span entire base length
        return base_area_total
    
    def _calc_base_area_nonfin(self):
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
        if self.fin_type in self.__rectangular_base_fin_types:
            base_area_nonfin = self.base_area_tot - self.n_fins * self.fin_thk * self.fin_wid
        else: #Catch invavlid fin types
            raise ValueError('Base area calculations only valid for supported rectangular fin types.')
        return base_area_nonfin
    
    def _calc_fin_effectiveness(self):
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
        if self.fin_type in self.__rectangular_base_fin_types:
            # epsilon_fin = nu_fin * (A_fin / A_fin_base)
            area_fin_base = self.fin_wid * self.fin_thk
            fin_effectiveness = self.fin_efficiency * self.fin_area_total / area_fin_base
        else: #Catch invavlid fin types
            raise ValueError('Base area calculations only valid for supported rectangular fin types.')
        return fin_effectiveness
        
    def _calc_overall_fin_effectiveness(self):
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
def suggest_fin_length(hx_coeff, fin_type, fin_thk,
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
    hx_coeff : HxCoefficient object
        Heat transfer coefficient object from hx_coefficients
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
    #Calculate param_m
    if fin_type == 'straight rectangular fin':
        param_m = sqrt( (2 * hx_coeff.h) / (hx_coeff.k * fin_thk) )
    elif fin_type == 'straight triangular fin':
        param_m = sqrt( (2 * hx_coeff.h) / (hx_coeff.k * fin_thk) )
    elif fin_type == 'straight parabolic fin':
        param_m = sqrt( (2 * hx_coeff.h) / (hx_coeff.k * fin_thk) )
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

if __name__ == '__main__':
    print('Test run of heat_sink.py')
