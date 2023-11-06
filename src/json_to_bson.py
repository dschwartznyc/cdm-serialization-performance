import json
import pymongo
import os
from bson import BSON
from dict_comp import dict_comp
import timeit
import inspect

json_file_in  = 'LargeCDM.json'
bson_file_in  = 'large_cdm.bson'
json_file_out = 'json_out.json'
bson_file_out = 'bson_out.bson'
json_dict     = {}

def write_json_file():
    with open(json_file_out, 'w') as w:
        w.write (json.dumps (json_dict))

def write_bson_file():
    with open(bson_file_out, 'wb') as w:
        w.write (BSON.encode (json_dict))

def read_json_file_in():
    with open(json_file_in,'r') as r:
        json_str = r.read()
        return json.loads (json_str)

def read_bson_file_in():
    with open(bson_file_in, 'rb') as r:
        bson_str = r.read()
        return BSON.decode (bson_str)


def create_bson_file_in (in_file_name, out_file_name):
    json_dict = read_json_file_in (in_file_name)
    bson_str = BSON.encode (json_dict)
    with open(out_file_name,'wb') as w:
        w.write(bson_str)

if __name__ == "__main__":
    json_dict        = read_json_file_in ()
    bson_dict        = read_bson_file_in ()
    print('dicts match') if dict_comp (json_dict, bson_dict) else print('dicts are different')
    json_size        = os.path.getsize (json_file_in)
    bson_size        = os.path.getsize (bson_file_in)
    number_of_tests  = 1000000
    repeat           = 10
    timings          = timeit.repeat(inspect.getsource(read_json_file_in), number=number_of_tests, repeat=repeat)
    json_avg_read    = sum(timings) / len(timings)
    timings          = timeit.repeat(inspect.getsource(read_bson_file_in), number=number_of_tests, repeat=repeat)
    bson_avg_read    = sum(timings) / len(timings)
    timings          = timeit.repeat(inspect.getsource(write_json_file), number=number_of_tests, repeat=repeat)
    json_avg_write   = sum(timings) / len(timings)
    timings          = timeit.repeat(inspect.getsource(write_bson_file), number=number_of_tests, repeat=repeat)
    bson_avg_write   = sum(timings) / len(timings)
    
    print('read test run: %6d times and repeated: %d.  file compression: %2.2f' % (number_of_tests, repeat, (1-bson_size/json_size)*100.0))
    print('json... size: %10d avg read timing: %2.5f avg write timing: %2.5f' % (json_size, json_avg_read, json_avg_write))
    print('json... size: %10d avg read timing: %2.5f avg write timing: %2.5f' % (bson_size, bson_avg_read, bson_avg_write))
