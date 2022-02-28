"""WIP
"""
import unittest
import json
import sys, os
HEAT_SINK_DIR = os.path.join(os.path.dirname(__file__), '..', 'heat_sink')
# HX_COEFF_DIR = os.path.join(HEAT_SINK_DIR, 'hx_coefficients')
sys.path.append(HEAT_SINK_DIR)
# sys.path.append(HX_COEFF_DIR)
import heat_sink
from hx_coefficients.hx_coefficients import matl_prop, HxCoefficient

# from time import time
# def timer(fn):
#     def wrap_fn(*args, **kwargs):
#         t1=time()
#         fn_return = fn(*args, **kwargs)
#         t2 = time()
#         t_delta = t2-t1
#         return fn_return, t_delta
#     return wrap_fn


# Inputs: hx_coeff, n_fins, fin_len, fin_wid, fin_thk, base_h

class TestHeatSinkInit(unittest.TestCase):
    def setUp(self):
        with open('test_settings.json', 'r') as f:
            test_data = json.load(f)
        self.settings = test_data['settings'] # Test setting parameters
        self.temps = test_data['heat_sink_data']['temps'] # Base temperature
        self.matls = test_data['heat_sink_data']['matls'] # Materials
        self.k_values_ref = test_data['heat_sink_data']['k_values_ref'] # Reference k-values
        self.k_values_ref = {
            (key_m, float(key_t)):self.k_values_ref[key_m][ key_t] 
            for key_m in self.k_values_ref 
            for key_t in self.k_values_ref[key_m]
            } # Changes dict to (matl, temp) keys instead of nested dicts, changes temp from str to float
        self.h_values = test_data['heat_sink_data']
        self.heat_sink_params = test_data['heat_sink_data']['heat_sink_params']

    def calc_k_values(self):
        """Calculates k values for use in HxCoefficient objects.
        """
        self.k_values = {
            (matl, temp):matl_prop.k_val(matl, temp)
            for matl in self.matls
            for temp in self.temps
            }

    def create_hx_coeff_objects(self):
        """Create HxCoefficient objects as inputs for heat sink objects.
        """
        self.hx_coeffs = {}
        for key_k in self.k_values:
            k_val = self.k_values(key_k)
            for h_val in self.h_values:
                self.hx_coeffs[(*key_k, h_val)] = HxCoefficient(k_val, h_val)
    
    def create_heat_sink_inputs(self):
        self.hs_inputs = []
        for 


    def test_k_val(self):
        """Unit test for k value accuracy.
        """
        self.calc_k_values()
        for key in self.k_values:
            # Test k values against test_settings.json, with consistent units of precision
            k_actual = round(self.k_values[key], self.settings['precision'])
            k_reference = round(self.k_values_ref[key], self.settings['precision'])
            self.assertEqual(k_actual, k_reference)

    def test_ref(self):

        


if __name__ == '__main__':
    print(f'Testing: {heat_sink}')
    unittest.main()
    # temp_base = 100 #Celcius
    # k_values = [matl_prop.k_val(matl_name, temp_base) for matl_name in TEST_MATLS]
    # h_values = [25, 100, 250]

    # hx_coeff_objs = [] #Init HxCoefficient storage list
    # for k in k_values:
    #     for h in h_values:
    #         hx_coeff_objs.append(HxCoefficient(k, h))
    #         i = len(hx_coeff_objs)-1
    #         print(f'HxCoefficient created: k: {hx_coeff_objs[i].k:.3f}, h: {hx_coeff_objs[i].h}')
    
    # hs_objs = {} #Init heat sink object storage ligst
    # i = 1 #Init ID object
    # for arg_in in TEST_INPUTS:
    #     for coeff_obj in hx_coeff_objs:
    #         arg_in['hx_coeff'] = coeff_obj #Update input list with arguments
    #         hs_objs['rect_'+f'{i:02d}'] = heat_sink.StrRectHeatSink(**arg_in)
    #         hs_objs['tri_'+f'{i:02d}'] = heat_sink.StrTriHeatSink(**arg_in)
    #         hs_objs['para_'+f'{i:02d}'] = heat_sink.StrParaHeatSink(**arg_in)
    #         i+=1
    # print(hs_objs)