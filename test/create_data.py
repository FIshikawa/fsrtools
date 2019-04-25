import sys
import os

if __name__ == '__main__':

    argv = sys.argv
    argc = len(argv)

    result_directory = './'
    N_x = 10
    N_y = 10
    if(argc > 1):
        result_directory = str(argv[1])
    if(argc > 2):
        N_x = int(argv[2])
    if(argc > 3 ):
        N_y = int(argv[3])


    correlation_file = os.path.join(result_directory,'result_correlation.dat')
    normal_file = os.path.join(result_directory,'result.dat')
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




