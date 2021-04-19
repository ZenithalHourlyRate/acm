#!/usr/bin/env python
# coding: utf-8

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert txts to one txt in the format of ascii-telnet-server')
    parser.add_argument('-i', dest='input', type=str, help='input imgs', required=True)
    parser.add_argument('-o', dest='output', type=str, help='output file', required=True)
    args = parser.parse_args()

    o = open(args.output, 'w')

    count = 1 # assumption made by ffmpeg
    from os.path import isfile
    while isfile(args.input.format(count)):
        input_file = args.input.format(count)

        with open(input_file, 'r') as i:
            print('1', file=o) # frame duration
            print(i.read(), file=o, end='') # without newline, assumption made by img2ascii.py
        print(f'{count} finished')
        count += 1
