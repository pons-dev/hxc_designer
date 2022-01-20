"""WIP
"""
from time import time
import sys, os
HEAT_SINK_DIR = os.path.join(os.path.dirname(__file__), '..', 'heat_sink')
# HX_COEFF_DIR = os.path.join(HEAT_SINK_DIR, 'hx_coefficients')
sys.path.append(HEAT_SINK_DIR)
# sys.path.append(HX_COEFF_DIR)
import heat_sink
from hx_coefficients.hx_coefficients import matl_prop, HxCoefficient

def timer(fn):
    def wrap_fn(*args, **kwargs):
        t1=time()
        fn_return = fn(*args, **kwargs)
        t2 = time()
        t_delta = t2-t1
        return fn_return, t_delta
    return wrap_fn

TEST_MATLS = ['Copper',
                'Steel - Carbon, 1% C',
                'Aluminum'
                ]

TEST_INPUTS = [
                {'n_fins':6, 
                'fin_len':.025, 
                'fin_wid':.05, 
                'fin_thk':.005, 
                'base_h':.02},
                {'n_fins':50, 
                'fin_len':.010, 
                'fin_wid':.020, 
                'fin_thk':.001, 
                'base_h':.030},
                {'n_fins':20, 
                'fin_len':.050, 
                'fin_wid':.200, 
                'fin_thk':.010, 
                'base_h':.200},
                ]
# Inputs: hx_coeff, n_fins, fin_len, fin_wid, fin_thk, base_h


if __name__ == '__main__':
    print(f'Testing: {heat_sink}')

    temp_base = 100 #Celcius
    k_values = [matl_prop.k_val(matl_name, temp_base) for matl_name in TEST_MATLS]
    h_values = [25, 100, 250]

    hx_coeff_objs = [] #Init HxCoefficient storage list
    for k in k_values:
        for h in h_values:
            hx_coeff_objs.append(HxCoefficient(k, h))
            i = len(hx_coeff_objs)-1
            print(f'HxCoefficient created: k: {hx_coeff_objs[i].k:.3f}, h: {hx_coeff_objs[i].h}')
    
    hs_objs = {} #Init heat sink object storage ligst
    i = 1 #Init ID object
    for arg_in in TEST_INPUTS:
        for coeff_obj in hx_coeff_objs:
            arg_in['hx_coeff'] = coeff_obj #Update input list with arguments
            hs_objs['rect_'+f'{i:02d}'] = heat_sink.StrRectHeatSink(**arg_in)
            hs_objs['tri_'+f'{i:02d}'] = heat_sink.StrTriHeatSink(**arg_in)
            hs_objs['para_'+f'{i:02d}'] = heat_sink.StrParaHeatSink(**arg_in)
            i+=1
    print(hs_objs)