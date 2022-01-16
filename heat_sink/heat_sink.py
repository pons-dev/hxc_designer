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
    Abstract:
        HeatSink
            Primary parent object to major subtypes of heat sink classes.
        StraightHeatSink
            Primary subtype of heat sink. Parent to concrete heat sink classes. Subclass of HeatSink.
    Concrete:
        StrRectHeatSink
            Straight rectangular fin profile heat sink. Subclass of StraightHeatSink.
        StrTriHeatSink
            Straight triangular fin profile heat sink. Subclass of StraightHeatSink.
        StrParaHeatSink
            Straight parabolic fin profile heat sink. Subclass of StraightHeatSink.

Functions:
    suggest_fin_length(hx_coeff, fin_type, fin_thk, return_type='df', verbose=True)
        Calculate suggested fin lengths for a given material, fin type, and fin thickness.

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
from hx_equations.hx_equations import HeatTransferMixin
from hx_coefficients.hx_coefficients import HxCoefficient


#============================================================================================================
#WIP Notes: TODO: REMOVE BEFORE PROD
#============================================================================================================
"""
TODO:
    Implement common methods like __repr__
    Check that @property is applied to all properties that need it
        Includes any instance where we don't want the user to edit a base class
        Make sure derived parameters are coved by this
    Make sure _calc_derived_params() is called on ALL updates to base inputs
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
    Add documentation to function missing docstrings
    Double check the documentation
        Make sure that any copy/pasted ones to abstract classes have unnecessary components removed.

"""
#============================================================================================================
#Primary Abstract Base Class Definition:
#============================================================================================================
class HeatSink(ABC, HeatTransferMixin):
    def __init__(self, hx_coeff, n_fins, fin_len):
        """Abstract base class for heat sink classes.

        Assumptions:
            Heat Transfer:
                - Heat conduction is steady and one dimensional.
                - Radiative heat transfer is negligible.
                - The effect of heat transfer from the L/t plane faces is negligible.
                - Temperature across the base plate of the heat sink is uniform.
            Properties:
                - Thermal conducitivity coefficient k is uniform across the heat sink.
                - Convection coefficient h is uniform across the heat sink.
            Additional assumption vary depending on subclass definitions.

        Parameters
        ----------
        hx_coeff : hx_coefficients.HxCoefficient
            Heat transfer coefficient object containing h and k values.
        n_fins : int
            Number of fins. Minimum of 2
        fin_len : float
            Length of the fin.
            Normal to the base plate surface plane.
        """
        self.hx_coeff = hx_coeff # hx_coefficient.HeatTransfer object
        self.n_fins = n_fins # Number of fins
        self.fin_len = fin_len # Length of the fin

    #========================================================================================================
    #Abstract Properties
    #========================================================================================================
    @property
    @abstractmethod
    def fin_type(self):
        """Abstract property for subclasses of HeatSink.
        Fin type. Governs which equations are used. New fin types should be incorporated in a distinct subclass.
        """
        pass

    @property
    @abstractmethod
    def hx_coeff(self):
        """Abstract property for subclasses of HeatSink.
        HxCoefficient object. See hx_coefficient documentation on implementation.
        Any object with obj.h and obj.k attributes are acceptable as inputs.
        """
        pass

    #========================================================================================================
    #Abstract Private Methods
    #========================================================================================================
    @abstractmethod
    def _calc_derived_params(self):
        """Abstract method for subclasses of HeatSink.
        Calculates derived parameters based on the heat sink profile characteristics.
        Should be called on initialization of class.
        Should be calced when the user changes any input parameter that can alter derived parameters.
        """
        pass

    @abstractmethod
    def _calc_fin_efficiency(self):
        """Abstract method for subclasses of HeatSink.
        Calculates fin efficiency, aka nu_fin.
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
        """
        pass

    @abstractmethod
    def _calc_fin_effectiveness(self):
        """Abstract method for subclasses of HeatSink.
        Calculates fin effecitveness, aka epsilon_fin.
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
        """
        pass

    @abstractmethod
    def _calc_overall_fin_effectiveness(self):
        """Abstract method for subclasses of HeatSink.
        Calculates overall fin effectiveness, aka epsilon_fin_overall
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
        pass

    @abstractmethod
    def _calc_fin_area_single(self):
        """Abstract method for subclasses of HeatSink.
        Calculates the surface area of a single fin.

        Returns
        -------
        fin_area_single : float
            Fin surface area.
        """
        pass

    @abstractmethod
    def _calc_fin_area_total(self):
        """Abstract method for subclasses of HeatSink.
        Calculates total fin surface area.

        Returns
        -------
        fin_area_total : float
            Total fin surface area.
        """
        pass

    @abstractmethod
    def _calc_base_area_nonfin(self):
        """Abstract method for subclasses of HeatSink.
        Calculates exposed base area.

        Returns
        -------
        base_area_nonfin : float
            Base area exposed to environment.
        """
        pass

    #========================================================================================================
    #Inherited Properties w/ Input Validation
    #========================================================================================================
    @property
    def n_fins(self):
        """Number of fins.

        Returns
        -------
        n_fins : float
            [description]
        """
        return self._n_fins
    
    @n_fins.setter
    def n_fins(self, n_fins):
        if n_fins >= 2 and type(n_fins)==int:
            self._n_fins = n_fins
        else:
            if type(n_fins) != int:
                raise TypeError('Number of fins must be an integer.')
            else:
                raise ValueError('')

    @property
    def fin_len(self):
        """Fin length. Normal to the base plate surface plane.

        Returns
        -------
        fin_len : float
        """
        return self._fin_len

    @fin_len.setter
    def fin_len(self, fin_length):
        if fin_length > 0:
            self._fin_len = fin_length
        else:
            raise ValueError('Fin length must be greater than 0.')
    
    #========================================================================================================
    #Inherited Public Methods
    #========================================================================================================
    def hx(self, temp_base, temp_env, rtype=list):
        """Calculates heat transfer across the heat sink.

        Parameters
        ----------
        temp_base : float
            [description]
        temp_env : float
            [description]
        rtype : dtype, optional
            Format for data return, by default list
            Options: list, dict

        Returns
        -------
        q_values : list or dict
            Returns rate of heat transfer across the heat sink, 
            by default list [q_fin_single, q_fin_total, q_heat_sink]

        Raises
        ------
        ValueError
            Invalid rtype. See options for rtype.
        """
        #TODO: Add method that allows you to enter multiple temperatures for each and return an array of results
        #Heat transfer methods derived from HeatTransferMixin
        q_fin_single = self._calc_q_fin_single(self, temp_base, temp_env, self.hx_coeff, self.fin_efficiency, self.fin_area_single)
        q_fin_total = self._calc_q_fin_total(self, temp_base, temp_env, self.hx_coeff, self.fin_efficiency, self.fin_area_total)
        q_heat_sink = self._calc_q_heat_sink(self, temp_base, temp_env, self.hx_coeff, self.fin_efficiency, self.fin_area_total, self.base_area_nonfin)
        if rtype==list:
            return [q_fin_single, q_fin_total, q_heat_sink]
        elif rtype==dict:
            return {'q_fin_single':q_fin_single, 'q_fin_total':q_fin_total, 'q_heat_sink':q_heat_sink}
        else:
            raise ValueError('Invalid return type.')

#============================================================================================================
#Secondary Abstract Class Definitions - Heat Sink General Types - Parents class to individual heat sink types
#============================================================================================================
class StraightHeatSink(HeatSink):
    def __init__(self, hx_coeff, n_fins, fin_len, fin_wid, fin_thk, base_h):
        """Abstract parent class for fins with a straight profile.

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
        hx_coeff : hx_coefficients.HxCoefficient
            Heat transfer coefficient object containing h and k values.
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
        base_h : float
            Height of the base plate.
            Perpendicular to fin length and fin width vectors.
            Total base area assumed to be base_h * fin_wid.
            Parallel to fin thickness vector.
        """
        self._fin_type = ['Straight', '']
        super().__init__(hx_coeff, n_fins, fin_len)
        self.fin_wid = fin_wid # Width of the fin, 
        self.fin_thk = fin_thk # Thickness of the fin
        self.base_h = base_h # Height of the base plate

        self._MIN_GAP = 0.0001 #Minimum allowed gap between fins
        _total_fin_width = n_fins * fin_thk #Total fin width across full heat sink
        self.gap = ( base_h - _total_fin_width ) / (n_fins - 1) #Gap between each fin

    #========================================================================================================
    #Abstract Private Methods
    #========================================================================================================
    @abstractmethod
    def _calc_fin_efficiency(self):
        """Abstract method for subclasses of StraightHeatSink.
        Calculates fin efficiency, aka nu_fin.
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
        """
        pass

    @abstractmethod
    def _calc_fin_area_single(self):
        """Abstract method for subclasses of StraightHeatSink.
        Calculates the surface area of a single fin.
        Calculated along the L/w plane.
        Assumes L/t plane effects are negligible.

        Returns
        -------
        fin_area_single : float
            Fin surface area.
        """
        pass
    
    #========================================================================================================
    #Inherited Properties w/ Input Validation
    #========================================================================================================
    @property
    def fin_type(self):
        #Add this to docstring: Note: There is no setter function as this value is not to be adjusted
        return ' '.join(self._fin_type)

    @property
    def hx_coeff(self):
        return self._hx_coeff
    
    @hx_coeff.setter
    def hx_coeff(self, hx_coeff):
        #Check if object passed has heat transfer coefficient attributes
        attr_check = all([hasattr(hx_coeff, 'h'), hasattr(hx_coeff, 'k')])
        if attr_check: #If present, check that they are valid
            try:
                attr_val_check = all([hx_coeff.h > 0, hx_coeff.k > 0])
            except:
                attr_val_check = False #Catch invalid data types that fail on comparitor check
        else: #TypeError on invalid object attributes
            raise TypeError('The object hx_coeff must have values for heat transfer coefficients h and k.')
        if all(attr_check, attr_val_check): #Set if input conditions are met
            self._hx_coeff = hx_coeff
        else: #ValueError on invalid attribute values
            raise ValueError('The values of h and k in hx_coeff are invalid.')

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
    def base_h(self):
        return self._base_h

    @base_h.setter
    def base_h(self, base_height):
        if base_height > 0:
            self._base_h = base_height
        else:
            raise ValueError('Base height must be greater than 0.')
    
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
        elif gap_dist < self._MIN_GAP: #Catch  values that are less than minimum allowed gap size
            err_msg = f"""Base height incompatible with fin parameters.
            Current parameters:
                base_h: {self.base_h}
                n_fins: {self.n_fins}
                fin_t: {self.fin_thk}
            This produces a gap size of: {gap_dist:.5f}
            Minimum gap size is::        {self._MIN_GAP:.5f}"""
            raise ValueError(err_msg)
        else:
            self._gap = gap_dist
    
    #========================================================================================================
    #Inherited Private Methods
    #========================================================================================================
    def _calc_fin_param_m(self):
        """Calculate non-dimensional parameter m for Straight fins.
        Used for efficiency calculations.

        Returns
        -------
        param_m : float
            Non-dimensional parameter for efficiency calculations.
        """
        return sqrt( (2 * self.hx_coeff.h) / (self.hx_coeff.k * self.fin_thk) )

    def _calc_fin_area_total(self):
        """Calculates total fin surface area.
        Calculated along the L/w plane.
        Assumes L/t plane effects are negligible.

        Returns
        -------
        fin_area_total : float
            Total fin surface area.
        """
        return self.fin_area_single * self.n_fins

    def _calc_base_area_nonfin(self):
        """Calculates exposed base area.

        Returns
        -------
        base_area_nonfin : float
            Base area exposed to environment.
        """
        return self.base_area_tot - self.n_fins * self.fin_thk * self.fin_wid
    
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
        """
        # epsilon_fin = nu_fin * (A_fin / A_fin_base)
        area_fin_base = self.fin_wid * self.fin_thk
        return self.fin_efficiency * self.fin_area_total / area_fin_base

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


#TODO: Add pin profile heat sink parent and child classes
# class PinHeatSink(HeatSink):
#     def __init__(self):
#         raise NotImplementedError()

#============================================================================================================
#Tertiary Class Definitions - Heat Sink Specific Types
#============================================================================================================
class StrRectHeatSink(StraightHeatSink):
    def __init__(self, hx_coeff, fin_type, n_fins, fin_len, fin_wid, fin_thk, base_h):
        """StrTriHeatSink object for heat transfer calculations.
        Heat Sink Type: Straight Rectangular Fin Profile

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
        hx_coeff : hx_coefficients.HxCoefficient
            Heat transfer coefficient object containing h and k values.
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
        base_h : float
            Height of the base plate.
            Perpendicular to fin length and fin width vectors.
            Total base area assumed to be base_h * fin_wid.
            Parallel to fin thickness vector.
        """
        super().__init__(hx_coeff, fin_type, n_fins, fin_len, fin_wid, fin_thk, base_h)
        self._fin_type[1] = 'Rectangular Fin' #Definition for subtype of StraightHeatSink
        self._calc_derived_params() #Calculated derived properties

    #========================================================================================================
    #Properties
    #========================================================================================================

    #========================================================================================================
    #Private Methods
    #========================================================================================================
    def _calc_derived_params(self):
        """Calculates derived parameters based on the heat sink profile characteristics.
        """
        self.fin_len_char = self._calc_fin_characteristic_length() #Calculate characteristic length
        self.fin_param_m = self._calc_fin_param_m() #Non-dimensional parameter used in fin calculations
        self.fin_efficiency = self._calc_fin_efficiency() #Fin efficiency (aka Nu)
        self.fin_area_single = self._calc_fin_area_single() #Fin surface area for a single fin (along the length/width plane)
        self.fin_area_total = self._calc_fin_area_total() #Total fin surface area (along the length/width plane)
        self.base_area_tot = self._calc_base_area_tot() #Total base cross-sectional area, disregarding fins
        self.base_area_nonfin = self._calc_base_area_nonfin #Exposed base area, excluding area taken up by fins
        self.fin_effectiveness = self._calc_fin_effectiveness() #Fin effectiveness (aka epsilon_fin)
        self.overall_fin_effectiveness = self._calc_overall_fin_effectiveness() #Overall effectiveness (aka epsilon_fin_overall)

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
        return self.fin_len + self.fin_thk/2

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
        """
        # nu_fin = tanh(m * L_c) / (m * L_c)
        return tanh(self.fin_param_m * self.fin_len_char) / (self.fin_param_m * self.fin_len_char)

    def _calc_fin_area_single(self):
        """Calculates the surface area of a single fin.
        Calculated along the L/w plane.
        Assumes L/t plane effects are negligible.

        Returns
        -------
        fin_area_single : float
            Fin surface area.
        """
        # A_fin = 2*w*L_c
        return 2 * self.fin_wid * self.fin_len_char

    #========================================================================================================
    #Public Methods
    #========================================================================================================

class StrTriHeatSink(StraightHeatSink):
    def __init__(self, hx_coeff, n_fins, fin_len, fin_wid, fin_thk, base_h):
        """StrTriHeatSink object for heat transfer calculations.
        Heat Sink Type: Straight Triangular Fin Profile

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
        hx_coeff : hx_coefficients.HxCoefficient
            Heat transfer coefficient object containing h and k values.
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
        base_h : float
            Height of the base plate.
            Perpendicular to fin length and fin width vectors.
            Total base area assumed to be base_h * fin_wid.
            Parallel to fin thickness vector.
        """
        super().__init__(hx_coeff, n_fins, fin_len, fin_wid, fin_thk, base_h)
        self._fin_type[1] = 'Triangular Fin' #Definition for subtype of StraightHeatSink
        self._profile_formula = 'y = (fin_thk/2)*(1 - x/fin_len)' #Formula for profile contour
        self._calc_derived_params() #Calculated derived properties
        
    #========================================================================================================
    #Properties
    #========================================================================================================
    @property
    def profile_formula(self):
        """Formula that defines the y profile of the heat sink.
        x-axis is along the fin_len vector.
        y-axis is along the fin_thk vector.
        Read-only attribute.

        Returns
        -------
        profile_formula : str
        """
        return self._profile_formula

    #========================================================================================================
    #Private Methods
    #========================================================================================================
    def _calc_derived_params(self):
        """Calculates derived parameters based on the heat sink profile characteristics.
        """
        self.fin_param_m = self._calc_fin_param_m() #Non-dimensional parameter used in fin calculations
        self.fin_efficiency = self._calc_fin_efficiency() #Fin efficiency (aka Nu)
        self.fin_area_single = self._calc_fin_area_single() #Fin surface area for a single fin (along the length/width plane)
        self.fin_area_total = self._calc_fin_area_total() #Total fin surface area (along the length/width plane)
        self.base_area_tot = self._calc_base_area_tot() #Total base cross-sectional area, disregarding fins
        self.base_area_nonfin = self._calc_base_area_nonfin #Exposed base area, excluding area taken up by fins
        self.fin_effectiveness = self._calc_fin_effectiveness() #Fin effectiveness (aka epsilon_fin)
        self.overall_fin_effectiveness = self._calc_overall_fin_effectiveness() #Overall effectiveness (aka epsilon_fin_overall)

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
        """
        # nu_fin = (1/(m*L))*(I_1(2*m*L)/I_0(2*m*L))
        #Calls a Bessel function. Verify that this is the correct implementation
        return (1 / (self.fin_param_m * self.fin_len) ) * (iv(1, 2*self.fin_param_m*self.fin_len)/iv(0, 2*self.fin_param_m*self.fin_len))

    def _calc_fin_area_single(self):
        """Calculates the surface area of a single fin.
        Calculated along the L/w plane.
        Assumes L/t plane effects are negligible.

        Returns
        -------
        fin_area_single : float
            Fin surface area.
        """
        # A_fin = 2 * w * sqrt(L^2 + (t/2)^2)
        return 2 * self.fin_wid * sqrt( self.fin_len**2 + ( self.fin_thk / 2 )**2 )

class StrParaHeatSink(StraightHeatSink):
    def __init__(self, hx_coeff, n_fins, fin_len, fin_wid, fin_thk, base_h):
        """StrTriHeatSink object for heat transfer calculations.
        Heat Sink Type: Straight Parabolic Fin Profile

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
        hx_coeff : hx_coefficients.HxCoefficient
            Heat transfer coefficient object containing h and k values.
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
        base_h : float
            Height of the base plate.
            Perpendicular to fin length and fin width vectors.
            Total base area assumed to be base_h * fin_wid.
            Parallel to fin thickness vector.
        """
        super().__init__(hx_coeff, n_fins, fin_len, fin_wid, fin_thk, base_h)
        self._fin_type[1] = 'Parabolic Fin' #Definition for subtype of StraightHeatSink
        self._profile_formula = '(fin_thk/2)*(1-x/fin_len)^2' #Formula for profile contour
        self._calc_derived_params() #Calculated derived properties

    #========================================================================================================
    #Properties
    #========================================================================================================
    @property
    def profile_formula(self):
        """Formula that defines the y profile of the heat sink.
        x-axis is along the fin_len vector.
        y-axis is along the fin_thk vector.
        Read-only attribute.

        Returns
        -------
        profile_formula : str
        """
        return self._profile_formula
    
    #========================================================================================================
    #Private Methods
    #========================================================================================================
    def _calc_derived_params(self):
        """Calculates derived parameters based on the heat sink profile characteristics.
        """
        self.fin_param_m = self._calc_fin_param_m() #Non-dimensional parameter used in fin calculations
        self.param_c = self._calc_param_c() #Non-dimensional parameter for curved fins
        self.fin_efficiency = self._calc_fin_efficiency() #Fin efficiency (aka Nu)
        self.fin_area_single = self._calc_fin_area_single() #Fin surface area for a single fin (along the length/width plane)
        self.fin_area_total = self._calc_fin_area_total() #Total fin surface area (along the length/width plane)
        self.base_area_tot = self._calc_base_area_tot() #Total base cross-sectional area, disregarding fins
        self.base_area_nonfin = self._calc_base_area_nonfin #Exposed base area, excluding area taken up by fins
        self.fin_effectiveness = self._calc_fin_effectiveness() #Fin effectiveness (aka epsilon_fin)
        self.overall_fin_effectiveness = self._calc_overall_fin_effectiveness() #Overall effectiveness (aka epsilon_fin_overall)
    
    def _calc_param_c(self):
        """Calculate non-dimensional parameter C.
        Used for curved fin profiles calculations.

        Returns
        -------
        param_c1 : float
            Non-dimensional parameter C
        """
        return sqrt(1 + ( self.fin_thk / self.fin_len )**2)

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
        """
        # nu_fin = 2 / ( 1 + sqrt( (2*m*L)^2 + 1 ) )
        return 2 / ( 1 + sqrt( ( 2 * self.fin_param_m * self.fin_len ) + 1) )

    def _calc_fin_area_single(self):
        """Calculates the surface area of a single fin.
        Calculated along the L/w plane.
        Assumes L/t plane effects are negligible.

        Returns
        -------
        fin_area_single : float
            Fin surface area.
        """
        #Note: math.log() is the natural logarithm (aka ln), hence renaming on import
        # A_fin = w*L * [ C_1 + (L/t)*ln( t/L + C_1) ]
        return self.fin_wid * self.fin_len * (self.param_c + \
            ( self.fin_len / self.fin_thk ) * ln( self.fin_thk / self.fin_len + self.param_c ) )
    
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
    if fin_type.lower() in ['straight rectangular', 'straight triangular', 'straight parabolic']:
        param_m = sqrt( (2 * hx_coeff.h) / (hx_coeff.k * fin_thk) )
    else: #Catch invalid fin types
        raise NotImplementedError(f'{fin_type} has not been implemented.')
    
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
