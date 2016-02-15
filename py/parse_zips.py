#!/usr/bin/env python

import zipfile
from io import StringIO
from xml.etree import cElementTree as etree
import os
import time

import multiprocessing as mp
import logging
logger = logging.getLogger(__name__)

XML_WORKERS_COUNT = mp.cpu_count()
ZIP_WORKERS_COUNT = mp.cpu_count()
CSV_WORKERS_COUNT = 1

QUEUE_MAX_SIZE_ZIP = 50
QUEUE_MAX_SIZE_XML = 150
QUEUE_MAX_SIZE_CSV = 150


CSV_COLUMN_SEPARATOR = ","
CSV_LINE_SEPARATOR = "\n"

def csv_append(csvs):

    csv1, csv2 = csvs

    f_csv1 =  open('csv1.csv','a')
    f_csv2 =  open('csv2.csv','a')

    f_csv1.write(csv1)
    f_csv1.write(CSV_LINE_SEPARATOR)

    f_csv2.write(csv2)
    f_csv2.write(CSV_LINE_SEPARATOR)

    f_csv1.close()
    f_csv2.close()

def csv_writer(qu, lock=None):
    '''
    CSV write worker: read queue and write readed data to the file
    if it is only one process - don't need any locks
    '''
    logger.debug('Start CSV writer')
    while True:
        csvs = qu.get()
        if csvs:
            if lock:
                lock.acquire()
            csv_append(csvs)
            if lock:
                lock.release()
        else:
            break
    logger.debug('Done CSV writer')

def parse_one_zip(zipfilename):
    '''
    worker: read queue of zipfilenames, opens zip file and pull xml files content to another queue
    '''
    zf = zipfile.ZipFile(zipfilename)
    for xmlname in zf.namelist():
        yield zf.read(xmlname).decode('utf8')
    zf.close()

def worker_unzip(qu_zip, qu_xml):
    '''
    worker: read queue of zipfilenames, opens zip file and pull xml files content to another queue
    '''
    logger.debug('Start unzipper')
    while True:
        zipfilename = qu_zip.get()
        if zipfilename:
            #logger.debug('unzip from {}'.format(zipfilename))
            for xml_content in parse_one_zip(zipfilename):
                #logger.debug('Queue XML.')
                if xml_content:
                    qu_xml.put(xml_content)
            #logger.debug('done unzip from {}'.format(zipfilename))
        else:
            for i in range(XML_WORKERS_COUNT):
                qu_xml.put(None)
            break
    logger.debug('Done unzipper')

def parse_one_xml(xml_content):
    try:
        root = etree.parse(StringIO(xml_content))
    except Exception as e:
        logger.error(e)
        logger.error(xml_content)
        return ('---error---','---error--')
    csv1_item  = { vr.get('name'): vr.get('value') for vr in root.findall('var') }
    if not 'id' in csv1_item or not 'level' in csv1_item:
        logger.warning('Invalid XML: no var "id" or "level"\n{}'.format(xml_content))
        logger.warning(repr(csv1_item))
        return ('---error---','---error--')
    csv2 = [CSV_COLUMN_SEPARATOR.join([csv1_item["id"], vr.get('name')]) for vr in root.findall('objects/object')]

    return (CSV_COLUMN_SEPARATOR.join(csv1_item[col] for col in ('id','level')), CSV_LINE_SEPARATOR.join(csv2))

def worker_parse_xml(qu_xml, qu_csv):
    '''
    worker: read queue of zipfilenames, opens zip file and pull xml files content to another queue
    '''
    logger.debug('Start XML parser')
    while True:
        xmlcontent = qu_xml.get()
        if xmlcontent:
            #logger.debug('get XML to parse')
            csvs = parse_one_xml(xmlcontent)
            #logger.debug('done XML parsing')
            qu_csv.put(csvs)
        else:
            for i in range(CSV_WORKERS_COUNT):
                qu_csv.put(None)
            break
    logger.debug('Done XML parser')

def parse_zips(qu_zip, folder="."):
    logger.debug('Start lookup zip-files')
    for fname in os.listdir(folder):
        if fname.endswith('.zip'):
            qu_zip.put(os.path.join(folder,fname))
    for i in range(ZIP_WORKERS_COUNT):
        qu_zip.put(None)
    logger.debug('Done lookup zip files')

if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    # create lock
    lock_csv = mp.Lock()
    # create queues
    # "None" in queue is sign of end of data stream
    qu_zip = mp.Queue(QUEUE_MAX_SIZE_ZIP)
    qu_xml = mp.Queue(QUEUE_MAX_SIZE_XML)
    qu_csv = mp.Queue(QUEUE_MAX_SIZE_CSV)
    # create unzip workers
    workers = []
    for i in range(ZIP_WORKERS_COUNT):
        p = mp.Process(target=worker_unzip, args=(qu_zip, qu_xml), name='Unzipper #{}'.format(i))
        p.start()
        workers.append(p)
    # create parse-xml workers
    for i in range(XML_WORKERS_COUNT):
        p = mp.Process(target=worker_parse_xml, args=(qu_xml, qu_csv), name='XML parser #{}'.format(i))
        p.start()
        workers.append(p)
    # create write-csv worker
    for i in range(CSV_WORKERS_COUNT):
        p = mp.Process(target=csv_writer, args=(qu_csv, lock_csv), name='CSV Writer #{}'.format(i))
        p.start()
        workers.append(p)

    # run fulling queue for "unzippers"
    parse_zips(qu_zip, folder='zips')
    for p in workers:
        p.join()

