#!/usr/bin/env python

import logging
import time

import parser


if __name__ == "__main__":
    errcnt = 0

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    t0 = time.time()
    for df in parser.parse('test_leaks', '*.txt'):
        print(df)
    t1 = time.time()
    logging.info("processed everything in %f [sec]" % (t1 - t0))
