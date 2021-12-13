"""Help on materials package:
Name
    materials

Description
    Material properties module for thermal applications
    =========================================
    materials is a Python module used for thermal calculations.
    Its aim is to provide thermal material properties.
    It is a part of the hxc_designer module.

Classes:
    Material

Functions:
    functions_example(input1, input2)

Misc Variables:
    __version__
    var1
"""

class Material():
    def __init__(self, material_name):
        __allowed_material_names=[
            'example'
        ]
        if material_name.lower() not in __allowed_fin_types: #Check for correct fin type input
            err_msg = 'Invalid material_name. \nAllowed materials:\n{}'.format("\n".join(__allowed_fin_types))
            raise ValueError(err_msg)
        self.material_name = material_name.lower()
        self.coeff_h = self.__get_convection_coefficient(self.material_name)
        self.coeff_k = self.__get_conduction_coefficient(self.material_name)

    def __get_convection_coefficient(matl_name):
        if matl_name == 'test1':
            coeff_h = 0.001
        elif matl_name == 'test2':
            coeff_h = 0.002
        else:
            raise ValueError('Invalid material name.')
        return coeff_h
    
    def __get_conduction_coefficient(matl_name):
        if matl_name == 'test1':
            coeff_k = 0.001
        elif matl_name == 'test2':
            coeff_k = 0.002
        else:
            raise ValueError('Invalid material name.')
        return coeff_k