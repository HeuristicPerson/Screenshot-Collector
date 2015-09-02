#!/usr/local/bin/python
# -*- coding: utf8 -*-

import datetime
import os

import cons


class Log:
    def __init__(self, u_file):
        if os.path.isfile(u_file):
            self.o_file = open(u_file, 'a')
        else:
            self.o_file = open(u_file, 'w')

    def log(self, u_text):
        o_time = datetime.datetime.now()
        u_entry = u'%s  %s\n' % (o_time.strftime(u'%d-%m-%Y %H:%M:%S'), u_text)
        self.o_file.write(u_entry.encode('utf8', 'strict'))

    def close(self):
        self.o_file.close()


