#!/usr/bin/env python

import uuid
import zipfile
import random
import string
from lxml import etree
from lxml.builder import E

MAX_LEVEL = 100
MIN_LEVEL = 1

MAX_OBJECTS_NUMBER = 10

NUMBER_FILES_IN_ZIP = 100
NUMBER_ZIP_FILES = 50

ZIP_COMPRESSION = zipfile.ZIP_DEFLATED

def get_random_string(minlen=10, maxlen=50):
    length = random.randint(minlen, maxlen)
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(length))

def get_xml_string():
    xml = E.root(
        E.var(name="id", value=uuid.uuid4().hex),
        E.var(name="level", value=str(random.randint(MIN_LEVEL, MAX_LEVEL))),
        E.objects(
            *[E.object(name=get_random_string()) for i in range(random.randint(1, MAX_OBJECTS_NUMBER))]
        )
    )
    return etree.tostring(xml, pretty_print=True)


def create_zip_file(filename):
    zf = zipfile.ZipFile(filename, mode="w", compression=ZIP_COMPRESSION)
    for i in range(NUMBER_FILES_IN_ZIP):
        zf.writestr('{:02d}-{}.xml'.format(i,get_random_string(5,5)), get_xml_string() )
    zf.close()

for i in range(NUMBER_ZIP_FILES):
    create_zip_file("zips/{:03d}.zip".format(i))

