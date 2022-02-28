import unittest
import json
import os, sys
import time
import pandas as pd
from testing_utils import fn_timer
DIR_TEST = os.path.dirname(__file__)
DIR_HXCOEFF = os.path.join(os.path.dirname(__file__), 
                            '..', 
                            'heat_sink', 
                            'hx_coefficients'
                            )
sys.path.append(DIR_HXCOEFF)
import hx_coefficients as hx_coeff


# class TestHxCoefficients(unittest.TestCase):
#     def setUp(self):
#         pass

#     def test_k_val(self):
#         #TODO: 
#         fn_kval = hx_coeff.matl_prop.k_val
#         k_outputs = []
#         for mname in self.TEST_MATLS:
#             for temp in self.TEST_TEMPS:
#                 k = fn_kval(mname, temp)
#                 t_k_1 = time.time()
#                 t_delta_k = float(t_k_1 - t_k_0)
#                 print(f'   {temp: >5}   {k:>7.3f}{t_delta_k:>8.4f}')
#                 print(f't:{t_delta_k}')
#                 rows.append([mname, temp, k, t_delta_k])


#         k_references = [393.91339, 43.0, 239.14961]

#         self.k_values = [hx_coeff.matl_prop.k_val(matl_name, self.TEMP_BASE) for matl_name in self.TEST_MATLS]
#         k_actuals = [round(k, 5) for k in self.k_values]
#         for k, k_ref in zip(self.k_values, k_references):
#             self.assertEqual(round(k, 5), k_ref)

if __name__ == '__main__':
    # rows = []

    # print('-'*40)
    # print('Begin test: hx_coefficients')
    # for mname in hx_coeff.matl_prop.matl_names: print(mname)

    # t_full0 = time.time()
    # for mname in TEST_MATLS:
    #     t_matl0 = time.time()
    #     fn_kval = hx_coeff.matl_prop.k_val
    #     print('-'*40)
    #     print(f'Materail: {mname}')
    #     print('    T(°C)     k        t   ')
    #     for temp in TEST_TEMPS:
    #         t_k_0 = time.time()
    #         k = fn_kval(mname, temp)
    #         t_k_1 = time.time()
    #         t_delta_k = float(t_k_1 - t_k_0)
    #         print(f'   {temp: >5}   {k:>7.3f}{t_delta_k:>8.4f}')
    #         print(f't:{t_delta_k}')
    #         rows.append([mname, temp, k, t_delta_k])
            
    #     t_matl1 = time.time()
    #     t_delta_matl = t_matl1 - t_matl0
    #     print(f'Time: {t_delta_matl:.4f}')

    # print('-'*40)
    # print('End test.')
    # t_full1 = time.time()
    # t_delta_full = t_full1 - t_full0
    # print(f'Time: {t_delta_full:.4f}')
    # print('-'*40)

    # df = pd.DataFrame(rows, columns=['Material', 'Temp (°C)', 'k (W/mK)', 'Time'])
    # fpath = os.path.join(DIR_TEST, 'hx_coefficients_test_results.csv')
    # df.to_csv(fpath, index=False)
    # print(f'Results: {fpath}')
    pass