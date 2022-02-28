"""Help on hx_coefficients package:
Name
    materials

Description
    Heat Transfer Coefficients module for thermal applications
    ===========================================================
    hx_coefficients is a Python module used for thermal calculations.
    Its aim is to provide a shared object containing heat transfer
    coefficients for use in iterative thermal design calculators.
    In an iterative calculator, this allows coefficient properties
    to be easily shared across a range of design objects.
    Additionally, it provides resources for coefficient determination
    It is a part of the heat_sink submodule of the hxc_designer module.

Classes:
    HxCoefficients

Functions:
    functions_example(input1, input2)

Misc Variables:
    __version__
    matl_prop
        Contains temperature-based material properties for various materials.

References:
    Cengel, Y.A. & Ghajar, A.J., (2015).
        Heat and Mass Transfer: Fundamentals & Applications, 5th Ed.
        McGraw Hill-Education, New York, NY.
    Engineering ToolBox, (2005). 
        Metals, Metallic Elements and Alloys - Thermal Conductivities. [online] 
        Available at: https://www.engineeringtoolbox.com/thermal-conductivity-metals-d_858.html 
        [Accessed 21 Dec 2021].

"""
import os
import pandas as pd
from scipy.interpolate.interpolate import interp1d

class __MaterialProperties:
    def __init__(self):
        """
        Temperature-based material properties for metals.
        Used to find thermal conductivity coefficient k values.

        Parameters
        ----------
        None.

        Attributes
        ----------
        matl_names : list
            List containing strings.
            Contains options for available material properties.
        matl_df : dict
            Dict containing a DataFrame for each item in matl_names
        matl_df_full : DataFrame
            Full dataframe containing all material, temperature, and k-value data.
        """
        # Import ./data/k_values_common.csv as a DataFrame
        __fpath_csv = os.path.join(
            os.path.join(os.path.split(__file__)[0], "data"), "k_values_common.csv"
        )
        _matl_df_full = pd.read_csv(__fpath_csv, index_col=0)
        _matl_names = _matl_df_full.index.unique()  # Unique material names

        # Create a df for each unique material
        _matl_df = {}
        for __matl in _matl_names:
            _matl_df[__matl] = _matl_df_full.loc[__matl, :].copy()
            # if len(_matl_df[__matl]) == 1: # Removed method for handling materials with one entry
            #     _matl_df[__matl].loc['interp_placeholder', 'T'] = _matl_df[__matl].loc[__matl, 'T'] + 0.1
            #     _matl_df[__matl].loc['interp_placeholder', 'k'] = _matl_df[__matl].loc[__matl, 'k']

        # Assign variables as class attributes
        self._matl_df_full = _matl_df_full
        self._matl_names = _matl_names
        self._matl_df = _matl_df

    # Property definitions to force variables into a read-only state
    @property
    def matl_names(self):
        return self._matl_names

    @property
    def matl_df(self):
        return self._matl_df

    @property
    def matl_df_full(self):
        return self._matl_df_full

    def k_val(self, matl, temp):
        """
        Calculates thermal conductivity coefficient k for given material and temperature.

        Parameters
        ----------
        matl : str
            Material name. Must belong to matl_names.
        temp : float
            Temperature, in Celcius

        Returns
        -------
        k_val
            Thermal conductivity coefficient k.
        """
        # Condition for when only a single entry exists for the material type
        if self._matl_df[matl].shape == (
            2,
        ):  # Property has no data on temperature variable
            k_val = self._matl_df[matl]["k"]
        else:  # Interpolate based on temperature
            x = self._matl_df[matl]["T"]
            y = self._matl_df[matl]["k"]
            k_interp = interp1d(x, y, bounds_error=False, fill_value="extrapolate")
            k_val = float(k_interp(temp))
        return k_val

matl_prop = (
    __MaterialProperties()
)  # Object used to extract material property information
# matl_prop._matl_names to retrieve available material names
# matl_prop.k_val(matl, temp) to retrieve k value based on temperature
# matl_prop._matl_df_full to retrieve a full dataframe of material k values at various temperatures
# matl_prop._matl_df to retrieve a dict containing a DataFrame for each _matl_names entry

class HxCoefficient:
    def __init__(self, k=0, h=0, matl=None, temp=None):
        """Heat transfer coefficient object.
        This object is used to store coefficient values for heat transfer calculations.
        This class was designed for use in iterative design calculators.
        All iterations of the design objects should contain a reference to a single
        HxCoefficient object for ease of use.

        Note on instance creation:
            HxCoefficients can be created via the following methods:
                (A): k, h inputs
                    Values for k and h are directly set on instance creation.
                    If matl and temp inputs are provided, these will be for reference only.
                    Otherwise matl and temp will default to none.
                (B): h, matl, temp inputs
                    Value for h is directly set on instance creation.
                    k value is calculated based on material data for matl at temperature temp.

        Parameters
        ----------
        k : float
            Thermal conducitivty coefficient k.
            Units: W / m K
            Default is 0, the following methods can be used to set k:
                (A) k is set to a positive number.
                (B) matl and temp are defined.
            This parameter is a material property and varies with temperature.
        h : float
            Heat transfer coefficient h.
            Units: W / m^2 K
            Default is 0 and must be overriden.
            This parameter varies based on a significant number of parameters, such as:
                Flow characteristics
                Fluid properties
                Surface characteristics
            Calculation of this parameter involves complicated thermal/fluid analysis methods
            and is beyond the scope of this project. For the current available heat sink profiles,
            h values will not affect normalized results.
            Typical heat transfer coefficients:
                Free convection:    5 - 25
                Forced convection:  25 - 250
        matl : str
            Definition for the material.
            Default is None.
            Used as reference for input method (A), used to calculate k for input method (B).
            Use HxCoefficient.get_matl_names() for available materials.
        temp : float
            Temperature of the material for the given k value, in Celcius
            Default is None.
            Used as reference for input method (A), used to calculate k for input method (B).

            Ref:
                Cengel, Y.A. & Ghajar, A.J., (2015).
                Heat and Mass Transfer: Fundamentals & Applications, 5th Ed.
                McGraw Hill-Education, New York, NY.

        """
        # Input validation: Type check on numeric inputs
        try:
            if k: k = float(k)
            if h: h = float(h)
            if temp: temp = float(temp)
        except:
            raise TypeError('Invalid input parameter types. Must be numeric for k, h, and temp')

        # Input validation: k value
        if k <= 0:
            if matl and temp: # If matl and temp are provided without k, calculate them
                self.k = self._get_matl_prop(matl, temp)
            elif not matl or not temp: # Not enough inputs
                raise ValueError('Value must be entered for k or matl and temp.')
            else: # Bad k input
                raise ValueError('k must be a positive non-zero number.')
        elif k > 0: # Correct k input
            self.k = k
        
        # Input validation: h value
        if h <= 0:
            raise ValueError('h must be a positive non-zero number.')
        else:
            self.h = h

        self.matl = matl
        self.temp = temp
    
    def _get_matl_prop(self, matl, temp):
        """Calculates k values from material and temperature.

        Parameters
        ----------
        matl : str
            Material name.
        temp : float
            Temperature, in Celcius.

        Returns
        -------
        k_val : float
            k value for the given material and temperature
        """
        return matl_prop.k_val(matl, temp)

    def get_matl_names(self):
        """Returns valid material names for k-value calculations.
        For use when creating HxCoefficient objects from matl and temp inputs.

        Returns
        -------
        _type_
            _description_
        """
        return matl_prop._matl_names

if __name__ == "__main__":
    print("Test run of heat_sink.py")
    print()
