import json
import os
from bson import BSON
import zlib
import lz4.frame
import timeit
from timeit import default_timer
from prettytable import PrettyTable 
from statistics import mean, stdev
import argparse
import sys

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
brute_force     = True

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

def get_brute_force_results (function_name):
    timings = [0] * repeat
    for i in range (repeat):
        start = default_timer()
        function_name()
        end   = default_timer()
        timings[i] = (end-start)
    return timings
    
def get_results (type, size, read_function, write_function, json_results = None):
    print ('running for tpye:', type, '... repeating ', repeat, 'times ... processing reads ... ', end='', flush=True)
    results                = {}
    timings                = get_brute_force_results(read_function) if brute_force else timeit.repeat(read_function, number=number_of_tests, repeat=repeat)
    results['type']        = type
    results['size']        = size
    results['compression'] = None if json_results == None else (size/json_results['size'] - 1) * 100
    results['avg_read']    = mean(timings)
    results['sd_read']     = stdev(timings)
    results['min_read']    = min(timings)
    results['max_read']    = max(timings)
    results['read_delta']  = None if json_results == None else ((results['avg_read']/json_results['avg_read'] - 1) * 100)
    print ('processing writes ... ', end='', flush=True)
    timings                = get_brute_force_results(write_function) if brute_force else timeit.repeat(write_function, number=number_of_tests, repeat=repeat)
    results['avg_write']   = mean(timings)
    results['sd_write']    = stdev(timings)
    results['min_write']   = min(timings)
    results['max_write']   = max(timings)
    results['write_delta'] = None if json_results == None else ((results['avg_write']/json_results['avg_write'] - 1) * 100)
    print ('done')
    return results

def run_repeat ():
    json_results    = get_results('json', os.path.getsize (json_file_in), read_json_file, write_json_file)
    bson_results    = get_results('bson', os.path.getsize (bson_file_in), read_bson_file, write_bson_file, json_results)
    lz4_results     = get_results('lz4',  os.path.getsize (lz4_file_in), read_lz4_file, write_lz4_file, json_results)
    zlib_results    = get_results('zlib', os.path.getsize (zlib_file_in), read_zlib_file, write_zlib_file, json_results)
    print ('ran tests ... repeating:', repeat, 'times', end='')
    print (' using', 'brute force' if brute_force else 'tineit.repeat')
    results         = PrettyTable (['', 'json', 'bson', 'lz4', 'zlib'])
    results.add_row (['file size', 
                      '{:,}'.format(json_results['size']),
                      '{:,}'.format(bson_results['size']),
                      '{:,}'.format(lz4_results['size']),
                      '{:,}'.format(zlib_results['size'])])
    results.add_row (['compression',
                      '',
                      '{0:,.1f}'.format(bson_results['compression']) + '%',
                      '{0:,.1f}'.format(lz4_results['compression']) +' %', 
                      '{0:,.1f}'.format(zlib_results['compression']) + '%'])
    print (results)
    results         = PrettyTable (['read', 'json', 'bson', 'lz4', 'zlib'])
    results.add_row (['avg read',
                      '{:,.5f}'.format(json_results['avg_read']), 
                      '{:,.5f}'.format(bson_results['avg_read']), 
                      '{:,.5f}'.format(lz4_results['avg_read']), 
                      '{:,.5f}'.format(zlib_results['avg_read'])])
    results.add_row (['delta read',
                      '',
                      '{0:,.1f}'.format(bson_results['read_delta']) + '%', 
                      '{0:,.1f}'.format(lz4_results['read_delta']) + '%', 
                      '{0:,.1f}'.format(zlib_results['read_delta'])+ '%'])
    results.add_row (['std dev read',
                      '{:,.5f}'.format(json_results['sd_read']),
                      '{:,.5f}'.format(bson_results['sd_read']),
                      '{:,.5f}'.format(lz4_results['sd_read']),
                      '{:,.5f}'.format(zlib_results['sd_read'])])
    results.add_row (['min read',
                      '{:,.5f}'.format(json_results['min_read']),
                      '{:,.5f}'.format(bson_results['min_read']),
                      '{:,.5f}'.format(lz4_results['min_read']),
                      '{:,.5f}'.format(zlib_results['min_read'])])
    results.add_row (['max read',
                      '{:,.5f}'.format(json_results['max_read']),
                      '{:,.5f}'.format(bson_results['max_read']),
                      '{:,.5f}'.format(lz4_results['max_read']),
                      '{:,.5f}'.format(zlib_results['max_read'])])
    print (results)
    results         = PrettyTable (['write', 'json', 'bson', 'lz4', 'zlib'])
    results.add_row (['avg write',
                      '{:,.5f}'.format(json_results['avg_write']), 
                      '{:,.5f}'.format(bson_results['avg_write']), 
                      '{:,.5f}'.format(lz4_results['avg_write']), 
                      '{:,.5f}'.format(zlib_results['avg_write'])])
    results.add_row (['delta write',
                      '',
                      '{0:,.1f}'.format(bson_results['write_delta']) + '%', 
                      '{0:,.1f}'.format(lz4_results['write_delta']) + '%', 
                      '{0:,.1f}'.format(zlib_results['write_delta'])+ '%'])
    results.add_row (['std dev write',
                      '{:,.5f}'.format(json_results['sd_write']),
                      '{:,.5f}'.format(bson_results['sd_write']),
                      '{:,.5f}'.format(lz4_results['sd_write']),
                      '{:,.5f}'.format(zlib_results['sd_write'])])
    results.add_row (['min write',
                      '{:,.5f}'.format(json_results['min_write']),
                      '{:,.5f}'.format(bson_results['min_write']),
                      '{:,.5f}'.format(lz4_results['min_write']),
                      '{:,.5f}'.format(zlib_results['min_write'])])
    results.add_row (['max write',
                      '{:,.5f}'.format(json_results['max_write']),
                      '{:,.5f}'.format(bson_results['max_write']),
                      '{:,.5f}'.format(lz4_results['max_write']),
                      '{:,.5f}'.format(zlib_results['max_write'])])
    print (results)

if __name__ == "__main__":
    # Instantiate the parser    


    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description='Coompare file size and read and write times using JSON, BSON, lz4 and zlib')
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 0.0.1"
    )
    # Required positional argument
    parser.add_argument('-r', 
                        '--runs', 
                        type=lambda x: (int(x) > 1) and int(x) or sys.exit("Number of runs must be greater than 1"),
                        required=False, 
                        default=1000, 
                        help='override number of runs (must be > 1 and default = 1000)')
    parser.add_argument('-t', 
                        '--timeit', 
                        action='store_false')
    args        = parser.parse_args()
    repeat      = args.runs
    brute_force = args.timeit
    json_dict   = read_json_file ()
    if(not os.path.isfile(bson_file_in)):
        write_bson_file()
    if(not os.path.isfile(lz4_file_in)):
        write_lz4_file()
        os.rename(lz4_file_out, lz4_file_in)
    lz4_dict  = read_lz4_file ()
    if(not os.path.isfile(zlib_file_in)):
        write_zlib_file()
        os.rename(zlib_file_out, zlib_file_in)
    zlib_dict = read_zlib_file ()
    run_repeat ()    
