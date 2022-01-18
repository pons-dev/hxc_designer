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

TEST_MATLS = ('Aluminum', 
                'Aluminum bronze', 
                'Copper',
                'Copper - Bronze (75% Cu, 25% Sn)',
                'Gold',
                'Iron',
                'Iron - Wrought',
                'Platinum',
                'Silver',
                'Steel - Carbon, 1% C',
                'Steel - Hastelloy C',
                'Titanium',
                'Tungsten'
                )
TEST_TEMPS = (-40,
                0,
                20,
                100,
                200,
                500
                )

if __name__ == '__main__':
    rows = []

    print('-'*40)
    print('Begin test: hx_coefficients')
    for mname in hx_coeff.matl_prop.matl_names: print(mname)

    t_full0 = time.time()
    for mname in TEST_MATLS:
        t_matl0 = time.time()
        fn_kval = hx_coeff.matl_prop.k_val
        print('-'*40)
        print(f'Materail: {mname}')
        print('    T(°C)     k        t   ')
        for temp in TEST_TEMPS:
            t_k_0 = time.time()
            k = fn_kval(mname, temp)
            t_k_1 = time.time()
            t_delta_k = float(t_k_1 - t_k_0)
            print(f'   {temp: >5}   {k:>7.3f}{t_delta_k:>8.4f}')
            print(f't:{t_delta_k}')
            rows.append([mname, temp, k, t_delta_k])
            
        t_matl1 = time.time()
        t_delta_matl = t_matl1 - t_matl0
        print(f'Time: {t_delta_matl:.4f}')

    print('-'*40)
    print('End test.')
    t_full1 = time.time()
    t_delta_full = t_full1 - t_full0
    print(f'Time: {t_delta_full:.4f}')
    print('-'*40)

    df = pd.DataFrame(rows, columns=['Material', 'Temp (°C)', 'k (W/mK)', 'Time'])
    fpath = os.path.join(DIR_TEST, 'hx_coefficients_test_results.csv')
    df.to_csv(fpath, index=False)
    print(f'Results: {fpath}')