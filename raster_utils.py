#!/usr/bin/env python

import os, re, time
import linuxcnc

LOCKFILE = '/home/pktck/linuxcnc_raster.lock'

emc_ini = None

def open_raster_fifo(mode):
    global emc_ini
    if emc_ini is None:
        emc_ini = linuxcnc.ini('2x_laser.ini')
    pipefile = emc_ini.find('RASTER', 'PIPE_FILE')

    if pipefile is None:
        pipefile = '/tmp/emc2_raster_fifo';

    try:
        return open(pipefile, mode)
    except IOError:
        os.mkfifo(pipefile)
    return open(pipefile, mode)

def send_params(p, q):
    fp = open_raster_fifo('w')
    fp.write('%g %g' % (p, q))
    fp.close()

def recv_params():
    fp = open_raster_fifo('r')
    params = fp.readline().strip()
    fp.close()
    return map(float, params.split())


def get_comment(file, lineno):
    fp = open(file, 'r')
    lineno = lineno - 1
    for i, line in enumerate(fp):
        if lineno == i:
            break
    m = re.search('\(([^)]+)\)', line)
    if m is not None:
        return m.group(1).strip()
    return ''


def set_lock():
    open(LOCKFILE, 'a').close()

def release_lock():
    try:
        os.remove(LOCKFILE)
    except os.error:
        pass

def wait_for_lock():
    while os.path.isfile(LOCKFILE):
        time.sleep(1)
