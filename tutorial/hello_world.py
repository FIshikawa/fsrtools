import sys

if __name__ == '__main__':

    argv = sys.argv
    argc = len(argv)

    if argc > 1:
        N_loop = int(argv[1])
    else:
        N_loop = 1
    for i in range(N_loop):
        print('Hello World!')
