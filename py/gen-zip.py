#!/usr/bin/env python

import uuid
import zipfile
import random
import string

xml_tpl='''<root>
    <var name="id" value="{guid}"/>
    <var name="level" value="{level}"/>
    <objects>
        {objects}
    </objects>
</root>
'''
xml_object_tpl = '<object name="{}"/>'

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
    tpl_data={
        "guid": uuid.uuid4().hex,
        "level": random.randint(MIN_LEVEL, MAX_LEVEL),
        "objects": '\n        '.join(xml_object_tpl.format(get_random_string()) for i in range(random.randint(1, MAX_OBJECTS_NUMBER)))
    }
    return xml_tpl.format(**tpl_data)


def create_zip_file(filename):
    zf = zipfile.ZipFile(filename, mode="w", compression=ZIP_COMPRESSION)
    for i in range(NUMBER_FILES_IN_ZIP):
        zf.writestr('{:02d}-{}.xml'.format(i,get_random_string(5,5)), get_xml_string() )
    zf.close()

for i in range(NUMBER_ZIP_FILES):
    create_zip_file("zips/{:03d}.zip".format(i))

