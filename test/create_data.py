import sys
import os
import numpy as np
from scipy.stats import norm

if __name__ == '__main__':

    argv = sys.argv
    argc = len(argv)

    result_directory = './'
    N_x = 100
    N_y = 10
    if(argc > 1):
        result_directory = str(argv[1])
    if(argc > 2):
        N_x = int(argv[2])
    if(argc > 3 ):
        N_y = int(argv[3])


    hist_file = os.path.join(result_directory,'result_hist.dat')
    correlation_file = os.path.join(result_directory,'result_correlation.dat')
    normal_file = os.path.join(result_directory,'result.dat')

    result_hist = open(hist_file,'w') 
    result_correlation = open(correlation_file,'w') 
    result_normal = open(normal_file,'w') 

    result_normal.write('#output_form x y\n')
    for i in range(N_x):
        result_normal.write('{:e} {:e} \n'.format(i, i*i))
    result_normal.close()

    result_correlation.write('#domain_form y ')
    for i in range(N_y):
        result_correlation.write('{:e} '.format(i))
    result_correlation.write('\n')
    result_correlation.write('#output_form x ')
    for i in range(N_y):
        result_correlation.write('z ')
    result_correlation.write('\n')
    for i in range(N_x):
        result_correlation.write('{:e} '.format(i))
        for j in range(N_y):
            result_correlation.write('{:e} '.format(i*i*j))
        result_correlation.write('\n')
    result_correlation.close()

    result_hist.write('#domain_form y ')
    for i in range(N_y):
        result_hist.write('{:e} '.format(i))
    result_hist.write('\n')
    result_hist.write('#output_form ')
    for i in range(N_y):
        result_hist.write('hist_Gauss range_Gauss ')
    result_hist.write('\n')
    x_data = np.linspace(-1.0,1.0,N_x)
    gaussian_pdf = {}
    for i in range(N_y):
        gaussian_pdf[i] = norm.pdf(x_data,loc=0.0,scale=1.0 / N_y * (i+1)) * 5
    for i in range(N_x):
        for j in range(N_y):
            result_hist.write('{:e} {:e} '.format(gaussian_pdf[j][i],x_data[i]))
        result_hist.write('\n')
    result_hist.close()



