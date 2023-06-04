
import requests
import json
import pandas as pd
# from pandas_geojson import read_geojson_url #pip install pandas_geojson, decided to get it with requests. 
import eel 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sqlite3
import csv
import os
import traceback

class Publish():
    def __init__(self):
        self.obesity_end_point = 'https://chronicdata.cdc.gov/resource/hn4x-zwk7.json'
        self.obesit_end_point_geojson = 'https://chronicdata.cdc.gov/resource/hn4x-zwk7.geojson'
        eel.init('web', allowed_extensions=['.html'])
        self.eel = eel
        

class NoSelf():
    def __init__(self):
        global publish
        self.obesity_end_point = publish.obesity_end_point
        self.obesit_end_point_geojson = publish.obesit_end_point_geojson

    def startPage():
        try:
            eel.start('project3.html', port=0)
        except Exception as e:
            print(f"ERROR {e} KEEP IN MIND THAT THIS SCRIPT REQUIRES YOU TO pip install eel")

    @eel.expose
    def updateDatabase():
        conn = sqlite3.connect('./Resources/obesity.db')
        try:
            conn.execute('''CREATE TABLE obesity_data
                (yearstart,yearend,locationabbr,locationdesc,datasource,class,topic,question,data_value_type,data_value,data_value_alt,
                low_confidence_limit,high_confidence_limit,sample_size,age_years,classid,topicid,questionid,datavaluetypeid,locationid,
                stratificationcategory1,stratification1,stratificationcategoryid1,stratificationid1,computed_region_bxsw_vy29,
                computed_region_he4y_prf8,geolocation_latitude,geolocation_longitude,geolocation_human_address,education,gender,income,
                total,race_ethnicity,data_value_footnote_symbol,data_value_footnote)''') # this columns must match our data. 
        except Exception as e: 
            print(e)
            eel.updateMessage("Database already exist reading it")
            NoSelf.readDataBase()
            return
            # eel.popAlert(str(e))
        try:
            # Import data from CSV file
            c = conn.cursor()
            with open('./Resources/obesity_data.csv', 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == 'yearstart': continue
                    clause = 'INSERT INTO obesity_data (yearstart,yearend,locationabbr,locationdesc,datasource,class,\
                            topic,question,data_value_type,data_value,data_value_alt,low_confidence_limit,high_confidence_limit,\
                            sample_size,age_years,classid,topicid,questionid,datavaluetypeid,locationid,stratificationcategory1,\
                            stratification1,stratificationcategoryid1,stratificationid1,computed_region_bxsw_vy29,\
                            computed_region_he4y_prf8,geolocation_latitude,geolocation_longitude,geolocation_human_address,\
                            education,gender,income,total,race_ethnicity,data_value_footnote_symbol,data_value_footnote)\
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'    
                    c.execute(clause,row)
            # Query data from table
            cursor = conn.execute("SELECT * from obesity_data")
            for row in cursor:
                print(row)

            conn.commit()
            conn.close()
        except Exception as e:
            traceback.print_exc()
            message = "THE DATABASE CODE HAS ISSUES IN PYTHON... FUNCTION 'updateDatabase'  " + str(e)
            # eel.popAlert(message)
            eel.updateMessage(message)
               

    @eel.expose
    def readDataBase():
        eel.updateMessage("READING DATA BASE ")   
        conn = sqlite3.connect('./Resources/obesity.db')
        cursor = conn.execute("SELECT * from obesity_data")
        tempList = []
        for row in cursor:
            listOfKeys = [
                "yearstart",
                "yearend",
                "locationabbr",
                "locationdesc",
                "datasource",
                "class",
                "topic",
                "question",
                "data_value_type",
                "data_value",
                "data_value_alt",
                "low_confidence_limit",
                "high_confidence_limit",
                "sample_size",
                "age_years",
                "classid",
                "topicid",
                "questionid",
                "datavaluetypeid",
                "locationid",
                "stratificationcategory1",
                "stratification1",
                "stratificationcategoryid1",
                "stratificationid1",
                "computed_region_bxsw_vy29",
                "computed_region_he4y_prf8",
                "geolocation_latitude",
                "geolocation_longitude",
                "geolocation_human_address",
                "education",
                "gender",
                "income",
                "total",
                "race_ethnicity",
                "data_value_footnote_symbol",
                "data_value_footnote"
            ]
            d = dict()
            indx = 0
            for el in row:
                d.update({listOfKeys[indx] : str(el)})
                indx += 1
            tempList.append(d)
            eel.updateMessage(row)
            print(row)
        eel.updateMessage(" COMPLETED READING DATABASE")
        return(tempList)

    @eel.expose
    def collectData():
        global publish
        if os.path.exists('./Resources/obesity.db'):
            data = NoSelf.readDataBase()
            return(data)
        eel.updateMessage("Collecting Data, please wait")
        try:
            dataJson = requests.get(publish.obesity_end_point)
            # dataGeoJson = requests.get(publish.obesit_end_point_geojson) # we will pass this to JS instead? maybe.... 
            d = json.loads(dataJson.text) #pass data to JS 
            df = pd.json_normalize(d)
            df.columns = df.columns.str.replace('[:,@]', '', regex=True)
            df.columns = df.columns.str.replace('[.]', '_', regex=True)
            df.to_csv('./Resources/obesity_data.csv', index=False, encoding='utf-8')
            eel.updateMessage("")
            return(d)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    if not os.path.exists("./Resources"):
        os.makedirs("./Resources")
    publish = Publish()
    startPage = NoSelf.startPage()
 
