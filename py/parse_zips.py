#!/usr/bin/env python

import zipfile
from io import StringIO
from xml.etree import cElementTree as etree
import os
import time

import multiprocessing as mp

CSV_COLUMN_SEPARATOR = ","
CSV_LINE_SEPARATOR = "\n"

def parse_one_zip(zipfilename):
    zf = zipfile.ZipFile(zipfilename)
    csv1=[]
    csv2=[]
    for xmlname in zf.namelist():
        xml_content = zf.read(xmlname).decode('utf8')
        root = etree.parse(StringIO(xml_content))
        parse_one_xml(root, csv1, csv2)
    zf.close()
    return CSV_LINE_SEPARATOR.join(csv1), CSV_LINE_SEPARATOR.join(csv2)

def parse_one_xml(root, csv1, csv2):
    csv1_item  = { vr.get('name'): vr.get('value') for vr in root.findall('var') }
    for vr in root.findall('objects/object'):
        csv2.append("{}{}{}".format(csv1_item["id"], CSV_COLUMN_SEPARATOR, vr.get('name')))

    csv1.append(CSV_COLUMN_SEPARATOR.join(csv1_item[col] for col in ('id','level')))

# Если нужна скорость - то обычно это достигается за счет использования памяти, в данном случае результирующие csv файлы до последнего "собираются" в памяти, а потом просто сохраняются.
# Если нужно сохранять результаты в процессе обработки (не накапливая в памяти), то можно сжелать очередь и пару рабочих-писателей которые будут писать в csv файлы, а основнные процессы - просто через очереди передавать что им нужно писать.
# Данная задача не была поставлена в рамках тестового задания, но при обсуждении реальных задач такой вопрос возник бы.

def parse_zips(folder=".", mapfn=map):
    csvs = mapfn(parse_one_zip, [os.path.join(folder,fname) for fname in os.listdir(folder) if fname.endswith('.zip') ])
    f_csv1 =  open('csv1.csv','w')
    f_csv2 =  open('csv2.csv','w')
    for csv1, csv2 in csvs:
        f_csv1.write(csv1)
        f_csv1.write(CSV_LINE_SEPARATOR)

        f_csv2.write(csv2)
        f_csv2.write(CSV_LINE_SEPARATOR)
    f_csv1.close()
    f_csv2.close()

# Проще всего будет распараллелить именно разбор всего zip файла, поскольку достаточно просто передать его имя, иначе пришлось бы передавать больше данных между процессами

def parse_zips_mp(np=3):
    with mp.Pool(np) as pool:
        parse_zips('zips', pool.map)

if __name__ == '__main__':
    c1 = time.clock()
    parse_zips('zips')
    c2 = time.clock()
    print(c2-c1)

    c1 = time.clock()
    parse_zips_mp()
    c2 = time.clock()
    print(c2-c1)

    c1 = time.clock()
    parse_zips_mp(6)
    c2 = time.clock()
    print(c2-c1)

    c1 = time.clock()
    parse_zips_mp(8)
    c2 = time.clock()
    print(c2-c1)
