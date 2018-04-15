#!/usr/bin/python

from peewee import Model, CharField, IntegerField, FloatField, DateTimeField, ForeignKeyField, PrimaryKeyField
from peewee import SqliteDatabase
from peewee import OperationalError, IntegrityError

from colorama import Fore, Style, Back
from sh import Command
import time

import os
import sys
import hashlib
import base64
import argparse
import json
# from web import sqlite_web

DBPATH = os.path.abspath('scanres.db')
DB = SqliteDatabase(DBPATH)

SCANSCHEMA = {
    "uid": '',
    "b_id": '',
    "s_id": '',
    "s_item": '',
    "s_summary" : '',
    "s_details" : '',
    "s_result": '',
    "s_scantime": time.asctime()
}

class SCAN(Model):
    uid = CharField(primary_key=True)
    b_id = CharField()
    s_id = CharField()
    s_item = CharField()
    s_summary = CharField()
    s_details = CharField()
    s_result = CharField()
    s_scantime = DateTimeField()

    class Meta:
        database = DB

try:
    DB.connect()
    if not SCAN.table_exists():
        print(
            Fore.YELLOW + "SCAN Table Not Exist, And Now We Will Create It" + Fore.RESET)
        DB.create_table(SCAN)
except Exception as e:
    pass

def summary2detail(summaryid):
    res = SCAN.select().dicts().where(SCAN.s_item == summaryid)
    print(Fore.GREEN + "[+] :"+Fore.RESET + res[0]['s_item'])
    print("\t--",res[0]['s_summary'])
    # print("\t--",res[0]['s_details'])

    return res[0]['s_summary'], res[0]['s_details']

def insertDB(scanres):

    t_scan = {
        "uid": scanres.u_id,
        'b_id': scanres.b_id,
        "s_id": scanres.s_id,
        "s_item": scanres.target,
        "s_summary": scanres.result['Summary'],
        "s_details": scanres.result['Details'], 
        "s_result": scanres.result,
        "s_scantime": time.asctime()
    }
    try:
        with DB.atomic():
            if SCAN.select().where(SCAN.s_item == scanres.target):
                exists_target = SCAN.get(SCAN.s_item == scanres.target)
                exists_target.delete_instance()

            SCAN.create(**t_scan)

    except OperationalError as e:
        print(Fore.RED + " Database is locked" + Fore.RESET)
        pass
    except IntegrityError as e:
        pass

def exportDB(sacnbatch_id, filename):
    try:
        res = SCAN.select().dicts().where(SCAN.b_id == sacnbatch_id)
        with open(filename, 'w') as f:
            for item in res:
                f.write(item['s_item']+",")
                f.write(item['s_summary']+",")
                f.write(json.dumps(item['s_result'],  ensure_ascii=False))
                f.write('\n')
                
    except Exception as e :
        print(Fore.RED + "ExportDB" + Fore.RESET,e)
        pass

def readDB():
    pass

def listDB(limit):
    pass
