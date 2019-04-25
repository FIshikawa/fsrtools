import sys

if __name__ == '__main__':

    argv = sys.argv
    argc = len(argv)

    N_loop = int(argv[1])
    for i in range(N_loop):
        print('Hello World!')
