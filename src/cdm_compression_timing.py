import json
import os
from bson import BSON
import zlib
import lz4.frame
import timeit
from timeit import default_timer
from prettytable import PrettyTable 
from statistics import mean, stdev

number_of_tests = 1
repeat          = 5000
json_file_in    = 'LargeCDM.json'
bson_file_in    = 'large_cdm.bson'
json_file_out   = 'json_out.json'
bson_file_out   = 'bson_out.bson'
lz4_file_in     = 'large_cdm.lz4'
lz4_file_out    = 'lz4_out.lz4'
zlib_file_in    = 'large_cdm.zlib'
zlib_file_out   = 'zlib_out.zlib'
json_dict       = {}
stupid_flag     = True

def read_json_file():
    with open(json_file_in,'r') as r:
        json_str = r.read()
        return json.loads (json_str)

def write_json_file():
    with open(json_file_out, 'w') as w:
        w.write (json.dumps (json_dict))

def read_bson_file():
    with open(bson_file_in, 'rb') as r:
        bson_str = r.read()
        return BSON.decode (bson_str)

def write_bson_file():
    with open(bson_file_out, 'wb') as w:
        w.write (BSON.encode (json_dict))

def read_zlib_file():
    with open(zlib_file_in, 'rb') as r:
        zlib_byte = r.read()
        return(json.loads(zlib.decompress (zlib_byte).decode()))
    
def write_zlib_file():
    with open(zlib_file_out, 'wb') as w:
        w.write (zlib.compress(json.dumps(json_dict).encode(), 6))

def read_lz4_file():
    with open(lz4_file_in, 'rb') as r:
        lz4_byte = r.read()
        return(json.loads(lz4.frame.decompress (lz4_byte).decode()))

def write_lz4_file():
    with open(lz4_file_out, 'wb') as w:
        w.write (lz4.frame.compress(json.dumps(json_dict).encode()))

def format_results(result):
    return [
        result[0],
        '{:,}'.format(result[1]),
        result[2],
        '{:,.5f}'.format(result[3]),
        result[4],
        '{:,.5f}'.format(result[5]),
        result[6]]

def format_stats(result):
    return [
        result[0],
        '{:,.5f}'.format(result[7]),
        '{:,.5f}'.format(result[8]),
        '{:,.5f}'.format(result[9]),
        '{:,.5f}'.format(result[10]),
        '{:,.5f}'.format(result[11]),
        '{:,.5f}'.format(result[12])]
    
def get_stupid_results (function_name):
    timings = [0] * repeat
    for i in range (repeat):
        start = default_timer()
        function_name()
        end   = default_timer()
        timings[i] = (end-start)
    return timings
    
def get_results (type, size, read_function, write_function, json_results = None):
    print ('tests: ', type)
    timings     = get_stupid_results(read_function) if stupid_flag else timeit.repeat(read_function, number=number_of_tests, repeat=repeat)
    avg_read    = mean(timings)
    sd_read     = stdev(timings)
    min_read    = min(timings)
    max_read    = max(timings)
    timings     = get_stupid_results(write_function) if stupid_flag else timeit.repeat(write_function, number=number_of_tests, repeat=repeat)
    avg_write   = mean(timings)
    sd_write    = stdev(timings)
    min_write   = min(timings)
    max_write   = max(timings)
    
    compression = '' if json_results == None else "{0:,.1f}".format((size/json_results[1] - 1) * 100) + '%'
    read_delta  = '' if json_results == None else "{0:,.1f}".format((avg_read/json_results[3] - 1) * 100) + '%'
    write_delta = '' if json_results == None else "{0:,.1f}".format((avg_write/json_results[5] - 1) * 100) + '%'
    return [type, 
            size, 
            compression, 
            avg_read,
            read_delta,
            avg_write,
            write_delta,
            sd_read,
            min_read,
            max_read,
            sd_write,
            min_write,
            max_write]

def run_repeat ():
    json_results    = get_results('json', os.path.getsize (json_file_in), read_json_file, write_json_file)
    bson_results    = get_results('bson', os.path.getsize (bson_file_in), read_bson_file, write_bson_file, json_results)
    lz4_results     = get_results('lz4',  os.path.getsize (lz4_file_in), read_lz4_file, write_lz4_file, json_results)
    zlib_results    = get_results('zlib', os.path.getsize (zlib_file_in), read_zlib_file, write_zlib_file, json_results)
    print ('using stupid') if (stupid_flag) else print ('using timeit.repeat')
    print ('test run ', repeat, ' times')
    results         = PrettyTable(['type', 'file size', 'compression', 'read time', 'read %', 'write time', 'write %']) 
    results.add_row (format_results(json_results))
    results.add_row (format_results(bson_results))
    results.add_row (format_results(lz4_results))
    results.add_row (format_results(zlib_results))
    print (results)
    results         = PrettyTable(['type', 'read sd', 'read min', 'read max', 'write sd', 'write min', 'write max']) 
    results.add_row (format_stats(json_results))
    results.add_row (format_stats(bson_results))
    results.add_row (format_stats(lz4_results))
    results.add_row (format_stats(zlib_results))
    print (results)

if __name__ == "__main__":
    json_dict        = read_json_file ()
    if(not os.path.isfile(bson_file_in)):
        write_bson_file()
    if(not os.path.isfile(lz4_file_in)):
        write_lz4_file()
        os.rename(lz4_file_out, lz4_file_in)
    lz4_dict        = read_lz4_file ()
    if(not os.path.isfile(zlib_file_in)):
        write_zlib_file()
        os.rename(zlib_file_out, zlib_file_in)
    zlib_dict       = read_zlib_file ()
    run_repeat ()
    stupid_flag     = True
    run_repeat ()
    
