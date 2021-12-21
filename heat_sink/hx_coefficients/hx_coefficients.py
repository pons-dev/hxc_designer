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
    var1

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

#============================================================================================================
#Class Definitions:
#============================================================================================================
class __MaterialProperties():
    def __init__(self):
        #Import ./data/k_values_common.csv as a DataFrame
        __fpath_csv = os.path.join(
                os.path.join(
                    os.path.split(__file__)[0], 
                    'data'
                    ),
                'k_values_common.csv')
        matl_df_full = pd.read_csv(__fpath_csv, index_col=0)
        matl_names = matl_df_full.index.unique() #Unique material names

        #Create a df for each unique material
        __matl_dfs = {}
        for __matl in matl_names:
            __matl_dfs[__matl] = matl_df_full.loc[__matl, :].copy()
            if len(__matl_dfs[__matl]) == 1:
                __matl_dfs[__matl].loc['interp_placeholder', 'T'] = __matl_dfs[__matl].loc[__matl, 'T'] + 0.1
                __matl_dfs[__matl].loc['interp_placeholder', 'k'] = __matl_dfs[__matl].loc[__matl, 'k']
        
        #Assign variables as class attributes
        self.matl_df_full = matl_df_full
        self.matl_names = matl_names
        self.matl_dfs = __matl_dfs
    
    def k_val(self, matl, temp):
        x = self.matl_dfs[matl]['T']
        y = self.matl_dfs[matl]['k']
        k_interp = interp1d(x, y, bounds_error=False, fill_value='extrapolate')
        return k_interp(temp)

class HxCoefficient():
    def __init__(self, k, h):
        """Heat transfer coefficient object.
        This object is used to store coefficient values for heat transfer calculations.
        This class was designed for use in iterative design calculators.
        All iterations of the design objects should contain a reference to a single
        HxCoefficient object for ease of use.
        
        Parameters
        ----------
        k : float
            Thermal conducitivty coefficient k.
            Units: W / m K
            This parameter is a material property and varies with temperature.
            Use material_k_val() function for common material k values.
        h : float
            Heat transfer coefficient h.
            Units: W / m^2 K
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

            Ref: 
                Cengel, Y.A. & Ghajar, A.J., (2015).
                Heat and Mass Transfer: Fundamentals & Applications, 5th Ed.
                McGraw Hill-Education, New York, NY.

        """

        self.k = k
        self.h = h

#============================================================================================================
#Object Definitions:
#============================================================================================================
matl_prop = __MaterialProperties() #Object used to extract material property information
#matl_prop.matl_names to retrieve available material names
#matl_prop.k_val(matl, temp) to retrieve k value based on temperature
#matl_prop.matl_df_full to retrieve a full dataframe of material k values at various temperatures
#matl_prop.matl_dfs to retrieve a dict containing a DataFrame for each matl_names entry



if __name__ == "__main__":
    print('Test run of heat_sink.py')
    print()

