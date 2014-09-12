import xlrd
import datetime
import uuid
import string
import re
import os

book = xlrd.open_workbook("/home/isi-projets/sensorNanny/data/archive/export-attide-sismer.xlsx")

#### TSG #####
sheetno = 0
procedure = {
	'SUROIT':'http://ubisi54.ifremer.fr:8080/sensornanny/record/f04ae920-5a87-41be-afb5-d189836d631e',
	'THALASSA':'http://ubisi54.ifremer.fr:8080/sensornanny/record/fc4fe80f-e67f-44be-8a50-2130dc987b4d',
	'PP':'http://ubisi54.ifremer.fr:8080/sensornanny/record/17af49b0-5914-4e79-9697-a89f94e81a24',
	'ATALANTE':'http://ubisi54.ifremer.fr:8080/sensornanny/record/056cc4aa-d862-42b9-bd83-f537910405af',
	'THALIA':'http://ubisi54.ifremer.fr:8080/sensornanny/record/40b955b6-1dd0-4687-9ecf-dc8a5254a3f7'}
template_file = "/home3/homedir4/perso/tloubrie/projets/sensorNanny/genavir/om/sismer-tsg-navire-template.xml"
target_directory= "/home3/homedir4/perso/tloubrie/projets/sensorNanny/genavir/result/tsg"

#### CINNA ####
#sheetno = 1
#procedure = {
#	'SUROIT':'http://ubisi54.ifremer.fr:8080/sensornanny/record/a4452544-847f-47bb-87f7-ce08b4c6296c',
#	'THALASSA':'http://ubisi54.ifremer.fr:8080/sensornanny/record/9e6d24d0-bc76-4aef-9d7d-f2bc052dde34',
#	'PP':'http://ubisi54.ifremer.fr:8080/sensornanny/record/9db74bfa-035b-4561-86d4-819004434fb8',
#	'ATALANTE':'http://ubisi54.ifremer.fr:8080/sensornanny/record/6c6bf0c8-334d-48db-bda5-297b642a097b',
#	'THALIA':'http://ubisi54.ifremer.fr:8080/sensornanny/record/eff0e1e9-b82f-4375-81ac-718245447dc5'}
#template_file = "/home3/homedir4/perso/tloubrie/projets/sensorNanny/genavir/om/sismer-attitude-navire-template.xml"
#target_directory= "/home3/homedir4/perso/tloubrie/projets/sensorNanny/genavir/result/cinna"
####

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
    ## procedure-tsg: tsg instruments
    ## procedure-cinna: cinna instruments
    record['procedure'] = procedure[sh.row(rx)[3].value]
    ## compute iso8601 time
    date_arr_tmp = sh.row(rx)[4].value.split('/')
    dattmp_full = datetime.datetime(2000+int(date_arr_tmp[2]), int(date_arr_tmp[1]), int(date_arr_tmp[0])).isoformat()
    record['datdeb'] = dattmp_full.split('T')[0]
    ## compute iso8601 time
    date_arr_tmp = sh.row(rx)[5].value.split('/')
    dattmp_full = datetime.datetime(2000+int(date_arr_tmp[2]), int(date_arr_tmp[1]), int(date_arr_tmp[0])).isoformat()
    record['datfin'] = dattmp_full.split('T')[0]    
    ## boundingbox    
    record['latnor'] = str(sh.row(rx)[6].value)
    record['latsud'] = str(sh.row(rx)[7].value)
    record['lonwes'] = str(sh.row(rx)[8].value)
    record['lonest'] = str(sh.row(rx)[9].value)
    # file location
    record['ficadr'] = sh.row(rx)[11].value     
    record['updatedate'] = datetime.datetime.utcfromtimestamp(os.path.getmtime(record['ficadr'])).isoformat() 
    ## directory target ./result/tsg/: for cinna datasets
    ## directory target ./result/cinna/: for cinna datasets
    with open(target_directory + '/'+ record['localuuid'] + ".xml", "wt") as fout:
      ## sismer-tsg-navire-template.xml template for tsg intrument
      ## sismer-cinna-navire-template.xml template for cinna intrument
      with open(template_file, "rt") as fin:
        for line in fin:
	  foundPatList = re.findall('###[a-z]*###', line)
	  print foundPatList
	  for pat in foundPatList:
            line= line.replace(pat, record[pat.split('###')[1]])
	  fout.write(line)
      fin.close()
    fout.close()



