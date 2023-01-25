import csv
import argparse
import glob
from datetime import date
"""
First part: Go through files in a folder looking for particular string - error code. 
The second part: Parse files and create DDL statements; 
How to run it: 
python ????/parse_log_create_hotfix.py ' ???SS/pdm2xml_convertor/test/test_files'
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for converting xml-files with xslt into a new xml')
    parser.add_argument('path', type=str, help='location of the source pdm')
    args = parser.parse_args()

    matchingError = 'Failure 6956'
    today = date.today()
    today = today.strftime("%y%m%d")
    print("-- HOTFIX FOR TERADATA ALTER STATEMENTS ON COLUMNS WITH STATISTICS")
    for file in glob.glob(args.path+"/Error*DDL*"):
        file1 = open(file, 'r')
        Lines = file1.readlines()
        lineMinus1 = currentline = ""
        for line in Lines:
            lineMinus2 = lineMinus1
            lineMinus1 = currentline
            currentline = line
            if matchingError in currentline:
                finalLineToParse = lineMinus2[lineMinus2.rfind('ALTER'):]
                split_matchinLine = finalLineToParse.split(" ")
                table_name = split_matchinLine[2]
                bkp_table_name = table_name+"_BKP"+today
                column_name = split_matchinLine[4]
                print("--FIXING TABLE: "+table_name)
                print("CREATE TABLE "+bkp_table_name+" as "+table_name+" WITH DATA AND STATISTICS;")
                print("DROP STATISTICS on "+ table_name+";")
                print(finalLineToParse.strip())
                print("COLLECT STATISTICS ON "+table_name+" from "+ bkp_table_name+ ";")



