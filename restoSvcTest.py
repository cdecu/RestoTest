#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Tools
"""

import argparse
import socket
import threading
import requests
import sys
import time
from src.utils import decode, TestError
from src.telemaxUtils import BuildTelemax, ParseTelemaxAnswer

__author__ = 'cdc'
__email__ = 'cdc@restomax.com'
__version__ = '0.0.1'


# ......................................................................................................................
class RestoSvcTestClass(object):
    """
    Class to ...
    """

    def __init__(self,
                 loops: int = 5,
                 threads: int = 5,
                 telemaxHost: str = '192.168.100.223',
                 telemaxPort: int = 8145
                 ):
        self.loops = loops if loops else 5
        self.threads = threads if threads else 5
        self.telemaxHost = telemaxHost if telemaxHost else '192.168.100.223'
        self.telemaxPort = telemaxPort if telemaxPort else 8145
        self.errors = []
        self.success = 0
        self.runs = 0

    # ..................................................................................................................
    def ResetCounters(self) -> None:
        self.errors = []
        self.success = 0
        self.runs = 0

    # ..................................................................................................................
    def ShowResults(self) -> None:
        print('\nResults\n-------')
        if self.errors:
            print('%d Errors' % (len(self.errors)))
            for e in self.errors:
                print('\t' + decode(str(e)))
            print('\n')
        print('%d on %d Success' % (self.success, self.runs))

    # ..................................................................................................................
    def TestWebSocket(self) -> None:
        threads = []
        self.ResetCounters()
        for i in range(self.threads):
            threads.append(threading.Thread(target=self.InternalTestWebSocket, args=(i, self.loops,)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.ShowResults()

    # ..................................................................................................................
    @staticmethod
    def InternalTestWebSocket(i: int, c: int) -> None:
        url = 'http://192.168.100.223:8787/RPC:Resto:SetPointage'
        payload1 = '{Action:C,Staff:{Pwd:www},Tbl:{Tbl:5,Consos:[{PLU:1001},{PLU:1002,TotalBase:25.12,Quantity:12}]},Station:{Num:1}}'
        payload2 = '{Action:C,Staff:{Pwd:www},Tbl:{Tbl:5,Consos:[{PLU:1001},{PLU:1002,TotalBase:25.12,Quantity:12}]},Station:{Num:1}}'

        for k in range(c):
            print('%d : %d : %s' % (i, k, url))
            r = requests.get(url, params=payload1)
            print('%d : %d : %s' % (i, k, r.status_code))
            print(r.text)
        r = requests.get(url, params=payload2)
        print('%d : %d : %s' % (i, 0, r.status_code))
        print(r.text)
        pass

    # ..................................................................................................................
    def TestTelemax(self) -> None:
        threads = []
        self.ResetCounters()
        for i in range(self.threads):
            threads.append(threading.Thread(target=self.InternalTestTelemax, args=(i, self.loops,)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.ShowResults()

    # ..................................................................................................................
    def InternalTestTelemax(self, i: int, c: int) -> None:

        for k in range(c):
            print('%d : %d : Test %s:%s' % (i, k, self.telemaxHost, self.telemaxPort))
            s = False
            try:
                self.runs += 1
                print('%d : %d : Connect' % (i, k))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.telemaxHost, self.telemaxPort))
                s.settimeout(10)
                # read the server Banner
                data = s.recv(8).decode('cp850').strip('\r\n')
                if data != '100 OK':
                    raise ValueError(data)
                print('%d : %d : Banner:' % (i, k), data)
                # send pointage
                time.sleep(0.1)
                msg = BuildTelemax(i, k)
                print('%d : %d : Pointage:' % (i, k), msg.strip('\r\n'))
                s.sendall(msg.encode('cp850'))
                # read answer
                data = s.recv(1024)
                s.sendall('OK\r\n'.encode('cp850'))

                msg = data.decode('cp850')
                (err, msg) = ParseTelemaxAnswer(msg)
                if err:
                    print('%d : %d : Answer:' % (i, k), msg)
                    self.success += 1
                else:
                    print('%d : %d : Error:' % (i, k), msg)
                    self.errors.append(TestError(msg))

                print('%d : %d : Close' % (i, k))
                s.close()

            except BaseException as e:
                print('%d : %d : Unexpected error:' % (i, k), sys.exc_info()[0])
                self.errors.append(TestError(e))
                if s:
                    s.close()
                pass


# ......................................................................................................................
def main():
    parser = argparse.ArgumentParser(
        prog="restoSvcTest.py",
        description=__doc__,
        epilog="\nbe careful and good lock !\n",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=35)
    )
    parser.add_argument('-x', '--threads', dest='threads', type=int, default=1, help='set threads count')
    parser.add_argument('-c', '--loops', dest='loops', type=int, default=1, help='set loops count')
    parser.add_argument('-m', '--mode', dest='mode', type=str, default='Telemax', help='Telemax,WebSocket Test')
    parser.add_argument('--TelemaxHost', dest='TelemaxHost', type=str, default='192.168.100.223', help='Telemax Host Addr')
    parser.add_argument('--TelemaxPort', dest='TelemaxPort', type=int, default='8145', help='Telemax Port')
    args = parser.parse_args()

    test = RestoSvcTestClass(
        loops=args.loops,
        threads=args.threads,
        telemaxHost=args.TelemaxHost,
        telemaxPort=args.TelemaxPort
    )
    if args.mode == 'Telemax':
        test.TestTelemax()
    else:
        test.TestWebSocket()


if __name__ == "__main__":
    main()
