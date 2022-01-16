# Heat Transfer Coefficient Submodule
## Description
<p>Provides heat transfer coefficient object for use with heat sink objects</p>

## Objects
### matl_prop
<p>Object for finding thermal conductivity coefficient k for metals.<br>
Properties vary based on temperature</p>
#### Methods
```
k_val(self, matl, temp) : Calculates thermal conductivity coefficient k for a given material and temperature
```
#### Attributes
```
matl_names : Contains  available material properties
matl_df : Dict containing a DataFrame for each item in matl_names
matl_df_full : Full dataframe containing all material, temperature, and k-value data
```

### HxCoefficient
<p> Stores heat transfer coefficient values. </p>

#### Attributes
```
k : Thermal conducitivty coefficient k in W / m K
h : Heat transfer coefficient h in W / m^2 K
```
<p>
Note on heat transfer coefficient h:<br>
This parameter varies based on a significant number of parameters, such as flow characteristics, fluid properties, and surface characteristics. Calculation of this parameter involves complicated thermal/fluid analysis methods and is beyond the scope of this project. <br>
<br>
For the current available heat sink profiles, h values will not affect normalized results. <br>
Typical heat transfer coefficients: <br>
Free convection:    5 - 25<br>
Forced convection:  25 - 250<br>
</p>