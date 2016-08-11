from __future__ import print_function
from bs4 import BeautifulSoup
from collections import defaultdict
from flask import Flask, jsonify, make_response, abort, url_for, request
from Harvard import Excel2CSV
from os.path import join, dirname, abspath
from IPython.display import HTML
import csv
import glob
import numpy as np
import os
import re
import requests
import time
import urllib2
import xlrd
import xlsxwriter
import xlwt

delMe = 0
w=1
x=2
y=3
z=4

#list800=[cell_obj_str,total_messages,category,last_three]
#listBBB=[cell_obj_str,category,accredited]

book = xlwt.Workbook(encoding="utf-8")

sheet1 = book.add_sheet("Results", cell_overwrite_ok=True)
sheet1.write(0,0, "Telephone Number")

url = "http://800notes.com/Phone.aspx/*"
headers = {'User-Agent': 'Chrome/39.0.2171.95 Safari/537.36 AppleWebKit/537.36 (KHTML, like Gecko)'}

response = requests.get(url, headers=headers)
content = BeautifulSoup(response.content, "lxml")
fileName = raw_input("Input the file with extension\n>")
stopPoint = fileName.index('.')
prepRev = fileName[stopPoint:]
csvTest = prepRev

if csvTest == ".csv":
   excelFile = xlsxwriter.Workbook(fileName + '.xlsx')
   worksheet = excelFile.add_worksheet()
   with open(fileName,'rb') as f:
      content = csv.reader(f)
      for index_col, data_in_col in enumerate(content):
            for index_row, data_in_cell in enumerate(data_in_col):
                  worksheet.write(index_col,index_row,data_in_cell)
   excelFile.close()
   fileName = (fileName + '.xlsx')
   delMe = 1
   print("Temporary Convert to xlsx done.\n")

deleteFile = fileName

fname = join(dirname(abspath('__file__')), '%s' % fileName)
#http://800notes.com/Phone.aspx/*-***-***-**** is the layout#

xl_workbook = xlrd.open_workbook(fname)
sheet_names = xl_workbook.sheet_names()
xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

website = raw_input("Input 1 for 800Notes, input 2 for BBB\n>")

if(website =="1"):
   sheet1.write(0,1, "# of Messages")
   sheet1.write(0,2, "Category")
   sheet1.write(0,3, "Last 3 Messages")         

if(website == "2"):
   sheet1.write(0,1, "Acreditted") 

col = xl_sheet.col_slice(0,1,10101010)
from xlrd.sheet import ctype_text
#print('(Column #) type:value')
for idx, cell_obj in enumerate(col):
   cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')  
   cell_obj_str = str(cell_obj)
   
   tele800 = (cell_obj_str[7] + "-" + cell_obj_str[8:11] + "-" + cell_obj_str[11:14] + "-" + cell_obj_str[14:18])
   teleBBB = ("%28" + cell_obj_str[8:11] + "%29+" + cell_obj_str[11:14] + "-" + cell_obj_str[14:18])
   print('(%s) %s' % (idx, tele800))
   w = tele800
   sheet1.write(idx+1, 0, w)
    
   if(website == "1"):
      reqInput = ('http://800notes.com/Phone.aspx/%s' % (tele800))
      print (reqInput)
      time.sleep(3)
      requestRec = requests.get(reqInput)
      soup = BeautifulSoup(requestRec.content, "lxml")
      print(requestRec.content)
      callType = soup.find('div',{'class':"callDetails"})
      print(callType)
      if callType is not (None):
         callCata = callType[10:]
         sheet1.write(idx+1, 2, callCata)
                
      stopPoint = fileName.index('.')
      prepRev = fileName[0:stopPoint]
      totalName = prepRev + "_rev_800.xls"  
      book.save(totalName)
      #x = bs4.divtotalmess
        
   if(website == "2"):
      reqInput = ('https://www.bbb.org/search/?splashPage=true&type=name&input='+ teleBBB +'&location=&tobid=&filter=business&radius=&country=USA%2CCAN&language=en&codeType=YPPA')
      print (reqInput)
      time.sleep(2)
      requestRec = requests.get(reqInput)
      soup = BeautifulSoup(requestRec.content,"lxml")
      divTags = soup.find('class')
      Badge = soup.find_all('img',{'class':'badge-accredited'})
      Hit = soup.find_all('td',{'class':'accredited'})
      if len(Hit)!=0:
         sheet1.write(idx+1,1,"Got a Hit")      
      if len(Badge)!=0:
         sheet1.write(idx+1,1,"Is Accredited")
      stopPoint = fileName.index('.')
      prepRev = fileName[0:stopPoint]
      totalName = prepRev + "_rev_BBB.xls"
      book.save(totalName)

Excel2CSV(totalName, "Results", prepRev + '.csv')

if delMe == 1:
   os.remove(deleteFile)
   print("Temp File Cleaned!\n")

print("Ding! All done!")