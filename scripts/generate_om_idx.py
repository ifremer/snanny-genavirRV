import xlrd
import datetime
import uuid
import string
import re
import os
import json
import requests
import geohash
import timehash
import netCDF4
from coards import from_udunits
import numpy
from rdp import rdp
from couchbase import Couchbase
from netCDF4 import num2date, date2num, chartostring


book = xlrd.open_workbook("../inputs/export-attide-sismer.xlsx")
snanny_system_view_rest = "http://visi-common-couchbase1:8092/snanny_systems_dev/_design/system_keyFilter/_view/snanny_system_keyFilter"
## couchbase connexion
c = Couchbase.connect(bucket='snanny_observations_dev', host='134.246.144.118', timeout=1)


#### TSG #####
#sheetno = 0
#template_file = "../swe/templates/tsg_om_json_template.json"


#### CINNA ####
sheetno = 1
template_file = "../swe/templates/cinna_om_json_template.json"

## sheet 0: TSG
## sheet 1: CINNA
sh = book.sheet_by_index(sheetno)
header=True
record = {}
for rx in range(sh.nrows):
    if (header==True):
        header = False
    else:
        ## get varialbe values
        ## generate UUID
        record['localuuid'] = str(uuid.uuid1())
        ## read column in excel file
        record['crnom'] = sh.row(rx)[0].value
        record['crno'] = str(int(sh.row(rx)[1].value))
        record['caman'] = str(int(sh.row(rx)[2].value))
        navire_temp = sh.row(rx)[3].value
        record['navire'] = sh.row(rx)[3].value
        ## procedure-tsg: SBE
        ## procedure-cinna: CINNA
        ## procedure uri
        param = {"key": str('"code___' + record['navire']+ '_SBE' '"') }
        r1 = requests.get(snanny_system_view_rest, params=param)
        data = r1.json()
        ancestors = data['rows'][0]['value']['ancestors']
        ancestors_str = ("\",\"").join(ancestors)
        record['procedurekey'] = str('"' + ancestors_str + '"')
        # read netcdf files
        ncfile = sh.row(rx)[11].value
        print(ncfile)
        record['filepath'] = ncfile
        record['updatedate'] = str(os.path.getmtime(ncfile))
        nc = netCDF4.Dataset(ncfile)
        lat = nc.variables['lat'][::100]
        lon = nc.variables['long'][::100]
        timeA  = nc.variables['time'][::100]
        timeUnit = nc.variables['time'].units
        timeOrigin = datetime.datetime.strptime(timeUnit.split('since ')[1], "%Y-%m-%d %H:%M:%S UTC")
        timeDelta = datetime.datetime(1970, 1, 1) - timeOrigin
        for i in range(len(lat)):
            record['latitude'] = str(lat[i])
            record['longitude'] = str(lon[i])
            try:
                record['geohash'] = '"' +  '","'.join(list(geohash.encode(float(lat[i]), float(lon[i])))) + '"'
            except Exception:
                record['geohash'] = '"_"'
            _timeStamp = (timeA[i] - timeDelta.days)*24*3600 - timeDelta.seconds
            record['measuredate'] = str(_timeStamp)
            timehashStr = timehash.encode(_timeStamp)
            record['timehash'] =  '"' + '","'.join(list(timehashStr)) + '"'
            recordDataString = ""
            with open(template_file, "rt") as fin:
                for line in fin:
                     foundPatList = re.findall('___[a-z]*___', line)
                     for pat in foundPatList:
                         line= line.replace(pat, record[pat.split('___')[1]])
                     recordDataString+=line
            fin.close()
            try:
                c.set(record['localuuid'] + '_' +  timehashStr, json.loads(recordDataString))
            except ValueError:
                print('Insert failure:')
                print(recordDataString)
        nc.close()




