#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Tools
"""

from serial import Serial

# ......................................................................................................................
def main():
    ser = Serial('/dev/pts/0')
    print(ser.name)
    while 1:
        c=ser.read(1)
        print('<<',c)
        if c==b'W':
            b=b'\x021234\r'
        else:
            b=b'\x02?\x01\r'
        print('>>',b)
        ser.write(b)
    ser.close()  # close port
    pass


if __name__ == "__main__":
    main()
