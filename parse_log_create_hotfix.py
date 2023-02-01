import csv
import argparse
import glob
from datetime import date
import sys,os,stat
import numpy as np
import shutil
import itertools
import shutil

"""
First part: Go through files in a folder looking for particular string - error code. 
The second part: Parse files and create DDL statements; 
How to run it: 
source /opt/miniconda3/bin/activate /mgmt/data/conda/envs/dwh-automation 
python ????/parse_log_create_hotfix.py ' ???SS/pdm2xml_convertor/test/test_files'
"""

def parseDatabaseName(table_name,listOfTables,listOfStgTables,listOfTTSTables,MatrixOfTenantsTables,listOfTenants):
    databaseNameTableNameFull =  table_name.split(".")
    listOfTTSTables.append(databaseNameTableNameFull[0][8:])
    listOfTenants.append(databaseNameTableNameFull[0][:8])
    TupplefTenantsTables = (databaseNameTableNameFull[0][:8], table_name[8:])
    MatrixOfTenantsTables.append(TupplefTenantsTables)


def unique(list1):
    x = np.array(list1)
    #print(np.unique(x))
    return np.unique(x)

def listOfDirectories(listOfTables):
    path_of_the_directory= '/home/je42278/l87_teradata_code_automation_rbwv2/code/teradata/code'
    path_output = '/home/je42278/DDL_HOTFIX_CREATION/OUTPUT_FILES/'
    shutil.rmtree(path_output)
    os.makedirs(path_output, exist_ok=True)
    os.chmod(path_output,0o777)
    print("Going through GIT repository looking for required artifact")
    for folderName in os.listdir(path_of_the_directory):
        if  "Table" in folderName:
            for filename in os.listdir(path_of_the_directory+"/"+folderName):

               for Tuple in MatrixOfTenantsTables:
                   TupleTableName = Tuple[1]
                   if "WRK" in TupleTableName:
                       TupleTableName =TupleTableName[:7]+TupleTableName[11:]
                   if TupleTableName in filename:
                       path = '/home/je42278/DDL_HOTFIX_CREATION/OUTPUT_FILES/'+Tuple[0]+'/'
                       os.makedirs(path, exist_ok=True)
                       os.chmod(path,0o777)
                       temp_output_file = open(path+Tuple[1]+today+".sql", 'w')
                       os.chmod(path+Tuple[1]+today+".sql",0o777)
                       temp_output_file.write("-- HOTFIX FOR TERADATA ALTER STATEMENTS ON COLUMNS WITH STATISTICS\n")
                       temp_output_file.write("RENAME TABLE "+Tuple[0]+Tuple[1]+" as "+Tuple[0]+Tuple[1]+"_BKP"+today+";\n")
                       #shutil.copyfile(os.path.join(path_of_the_directory+"/"+folderName,filename),os.path.join('/home/je42278/DDL_HOTFIX_CREATION/OUTPUT_FILES/'+Tuple[0],filename))
                       #temp_output_file.close()
                       fin = open(os.path.join(path_of_the_directory+"/"+folderName,filename), "rt")
                       #read file contents to string
                       data = fin.read()
                       #replace all occurrences of the required string
                       data = data.replace('@TENANT_ID@_@DATAGROUP_CD@_@SBX_NAME@', Tuple[0]  )
                       temp_output_file.write(data)
                       temp_output_file.write("INSERT INTO "+Tuple[0]+Tuple[1]+" SELECT * FROM  "+Tuple[0]+Tuple[1]+"_BKP"+today+";\n")
                       #temp_output_file.write("COLLECT STATISTICS ON "+Tuple[0]+Tuple[1]+" from "+ Tuple[0]+Tuple[1]+"_BKP"+today+ ";\n\n")
                       temp_output_file.close()


def createFinalHotfixFiles():
    path = '/home/je42278/DDL_HOTFIX_CREATION/OUTPUT_FILES'
    print("Hotfix created for: ")
    for folderName in os.listdir(path):
        # getting excel files to be merged from the Desktop
        # read all the files with extension .xlsx i.e. excel
        filenames = glob.glob(path+"/"+folderName+"/"+"*.sql")
        # for loop to iterate all excel files
        with open(path+"/"+folderName+"hotfix.sql", 'w') as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    outfile.write(infile.read())
            print(outfile.name)






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for converting xml-files with xslt into a new xml')
    parser.add_argument('--path', type=str, help='location of the source pdm')
    args = parser.parse_args()

    matchingError = 'Failure 6956'
    today = date.today()
    today = today.strftime("%y%m%d")
    file_path = os.path.dirname(sys.argv[0])

    output_file = open(file_path+"/HOTFIX_ALTER_STATISTICS"+today+".sql", 'w')
    os.chmod(file_path+"/HOTFIX_ALTER_STATISTICS"+today+".sql",0o777)
    output_file.write("-- HOTFIX FOR TERADATA ALTER STATEMENTS ON COLUMNS WITH STATISTICS\n")
    listOfStgTables =[]
    listOfTables =[]
    listOfTTSTables =[]
    MatrixOfTenantsTables =[]
    listOfTenants = []
    print ("---  Parsing Error files ------")
    for file in glob.glob(args.path+"/Error*DDL*"):

        print (file)
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
                parseDatabaseName(table_name,listOfTables,listOfStgTables,listOfTTSTables,MatrixOfTenantsTables,listOfTenants)
                bkp_table_name = table_name+"_BKP"+today
                column_name = split_matchinLine[4]
                output_file.write("--FIXING TABLE: "+table_name+"\n")
                output_file.write("CREATE TABLE "+bkp_table_name+" as "+table_name+" WITH DATA AND STATISTICS;\n")
                output_file.write("DROP STATISTICS on "+ table_name+";\n")
                output_file.write(finalLineToParse.strip())
                output_file.write("COLLECT STATISTICS ON "+table_name+" from "+ bkp_table_name+ ";\n\n")




    output_file.close()
    listOfDirectories(MatrixOfTenantsTables)
    createFinalHotfixFiles()






