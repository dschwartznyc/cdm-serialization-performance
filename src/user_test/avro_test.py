import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import json
import bson
import os

schema = avro.schema.parse(open("user.avsc", "rb").read())

writer = DataFileWriter(open("users.avro", "wb"), DatumWriter(), schema)
alyssa = {"name": "Alyssa", "favorite_number": 256}
ben    = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
writer.append(alyssa)
writer.append(ben)
writer.close()

f = open("users.txt", "w")
f.write(json.dumps (alyssa))
f.write(json.dumps (ben))
f.close()

b = open("users.bson", "wb")
b.write(bson.dumps (alyssa))
b.write(bson.dumps (ben))
b.close()

reader = DataFileReader(open("users.avro", "rb"), DatumReader())
for user in reader:
    print (user)
reader.close()

print('size of txt:  %3d size of avro: %3d size of bson: %3d' % 
      (os.path.getsize("users.txt"), 
       os.path.getsize("users.avro"),
       os.path.getsize("users.bson")))
