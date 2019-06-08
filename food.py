
import boto3
import json
import logging
import os
import hmac
import hashlib
import urllib.parse as urlparse
import gspread
import datetime
import dateparser
from oauth2client.service_account import ServiceAccountCredentials

class Food:
    
   

    


    

    START_ROW=6
    START_COL=2
    DAY_LENGTH=8
    WEEKEND_LENGTH=3


    def __init__(self, sheet_name):
    
        keyfile_dict = {
          "type": "service_account",
          "project_id": "lunchborg",
          "private_key_id": "3fdead89702b3a003c8334cdfbcab6ed4a619134",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC2WS6EC6cGHGOG\n1003sfwGO8jzyD2w0La3V640XQ7Nfmue8KjzCJ47HJyg/LxsTAc7QrHV7JeWWabO\nVzdh+9th/ksqqXrzismOo+06fmaXV6YOoZ3yA0cWihsyQ8uv/QTxs4P3p9eyYLQP\nQrUhDI+LkGaNTO1KO+krGeEBtNqTNeSik0PPfXWb2Wss0jgZJILSuO5KS+ND3GRK\njLsfnaLUDMOK1Pr11mq0nE/F698X2PChsvP4WKyI9AflN4ZBFo/4mg8+iN+V9nMW\n6cpAZXHlGbD6Y8lWCMBug5qrQQR8b8yr5gXBJf6w+IaCcAu+6y0iSTOfqKvY4opp\nsSMUXsK3AgMBAAECggEAAoJzCIhi/3Yajzh4xQ+yWyc5rLuEVpjE8dfHaS2OHeJd\nq2GBw0SZ575D33uEHOrHI9fjSBm2eSEbBX+u1X31h7InVvaKcb4v9Dws1/lKy+Br\nvbxI63trNXiJZdqyoDrmysGLSywRp9Zirq0uBIHmFJvge+pml+rPEYLuMLq6CRUT\nvdVTGLIk+4OYMGHP5DuKe1KjnaDO3li/AXiyFJzigiTbBvk3fQ041/2lvqo0dT24\n98ZGgvLp/hA3Ys5apIuU1roIATIdIZbiIHGRemMcGGCm8IJOPO1PuiCgDIprePJ3\nx0f1Xvp8tkSI8PiSuaj9AeyIt+NDc2dREjZi3dPD2QKBgQDmr9L4u9PIP/Nem/vY\nK+kKX+fCWANkCjyizwLVMwUQ9zVfrswxDJEJmlhHZtYYvaFRB8kNKgTuCNl/g4za\nZeHgUy8iRppds9sEMvXJArNQFaSc4kLCrlWtl+BKxLCqsLZ7QDOrIZQeVQ3WQzhT\nzaH79MglREiUNTDIeAe73S8nMwKBgQDKW34BYjcIuiRHQeRk1W4dGCWUsq4MOwR0\nnIHLVRvd8pfHATpM80z6T0iN7PI1EVSHNouMeKOERJNUa8TizIghglq6o6siNYWL\nRm8E/1tjCKVtuZJOD1EWs3OJy4/K+tfHdOGDpdBTU0Au6D9AeqHXS+jIOeOEX2za\n7tQr3KCmbQKBgENY33HIfBrBOM7NIShKIX3q4+FkCpFhP7SUVRJjE76RPV7SzEAh\nmBJCojUuO6D7c6YRbMvQEaJgqQbGJA/6oIf6IQ+Tpytl/7HpIsJtbGYb+3PlxnHJ\nra/BYDTT2XPrpUq0QqFaa0CzuhdshnxI01qYavoeRkYmhThxemiJOWPrAoGBAKkn\n0i1V7Kte7vSiIEoqH+IyTTgAJX4T16WjLtzKSIFASaARZqrst2yG2h/J8q5pzj85\nWW4Tap0mtgHcFLmCQEnCrhVWu7fdBcVnG2cSD1K554/RkHuwUhin6e1GPO1wwu/4\nxItIEN2WuhB8FGPSH3fZ/L1jps0A9/4Lp1EDHUgBAoGAfX0eBkETl2e9XaqOCM+K\nAoZ/rDHY4D9xjSlnd0VV9YNUFezasT4urHUDwIlsXXuPgqSkc1SpEg/YYS7LtfKG\ndMf0G13DEmluFLz/eBel9US0wWRged7/+QoUEiZu5wgasUP6M1YRee8oVnAC7Kkk\nMYQ6rv3qpu8DsRW8kLmrbdE=\n-----END PRIVATE KEY-----\n",
          "client_email": "lunchborg@lunchborg.iam.gserviceaccount.com",
          "client_id": "112593059769958611489",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lunchborg%40lunchborg.iam.gserviceaccount.com"
        }
        
        scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict=keyfile_dict, scopes=scope)
        client = gspread.authorize(creds)
        self.sheet = client.open("Test Lunch Keukenconfessies - Studyportals").worksheet(sheet_name)


    def workdaycount(self,first, second, inc = 0):
       if first == second:
          return 0
       import math
       if first > second:
          first, second = second, first
       if inc:
          from datetime import timedelta
          second += timedelta(days=1)
       interval = (second - first).days
       weekspan = int(math.ceil(interval / 7.0))
       if interval % 7 == 0:
          return interval - weekspan * 2
       else:
          wdf = first.weekday()
          if (wdf < 6) and ((interval + wdf) // 7 == weekspan):
             modifier = 0
          elif (wdf == 6) or ((interval + wdf + 1) // 7 == weekspan):
             modifier = 1
          else:
             modifier = 2
          return interval - (2 * weekspan - modifier)    
          
          
    def prev_working_day(self):
        adate = datetime.datetime.today()
        adate -= datetime.timedelta(days=1)
        while adate.weekday() > 4: # Mon-Fri are 0-4
            adate -= datetime.timedelta(days=1)
        return adate
        
    def next_working_day(self):
        adate = datetime.datetime.today()
        adate = adate + datetime.timedelta(days=1)
        if adate.isoweekday() in set((6, 7)):
            adate += datetime.timedelta(days=adate.isoweekday() % 5)
        return adate

    def get_menu(self,date2):
        
        date1 = dateparser.parse(self.sheet.cell(self.START_ROW,self.START_COL).value)
        
        workday_count = self.workdaycount(date1,date2)
        
        weekends = workday_count // 5

        today_row = self.START_ROW+workday_count*self.DAY_LENGTH+weekends*self.WEEKEND_LENGTH
        
        
        warm = "*"+self.sheet.cell(today_row,3).value+"* _"+self.sheet.cell(today_row,4).value+"_"
        salad = "*"+self.sheet.cell(today_row+2,3).value+"* _"+self.sheet.cell(today_row+2,4).value+"_"
        bread = "*"+self.sheet.cell(today_row+4,3).value+"* _"+self.sheet.cell(today_row+4,4).value+"_"
        
        return "{}\n{}\n{}".format(warm,salad,bread)
        
    
    def search_for_name(self,date2,name):
        date1 = dateparser.parse(self.sheet.cell(self.START_ROW,self.START_COL).value)
        
        workday_count = self.workdaycount(date1,date2)
        
        weekends = workday_count // 5

        today_row = self.START_ROW+workday_count*self.DAY_LENGTH+weekends*self.WEEKEND_LENGTH
        
        for col in range(6,20):
            for row in range(today_row,today_row+5):
                if self.sheet.cell(row,col).value.strip()==name:
                    return row,col
                    
        raise Exception("Couldn't find name to unsubscribe!")

        
    
    def search_for_empty_spot(self,date2,preference):
        date1 = dateparser.parse(self.sheet.cell(self.START_ROW,self.START_COL).value)
        
        workday_count = self.workdaycount(date1,date2)
        
        weekends = workday_count // 5

        today_row = self.START_ROW+workday_count*self.DAY_LENGTH+weekends*self.WEEKEND_LENGTH
        
        if preference == 'vegetarian':
            min_col = 6
            max_col = 10
        
        if preference == 'carnivore':
            min_col = 12
            max_col = 20
        
        for col in range(min_col,max_col):
            for row in range(today_row,today_row+5):
                if not self.sheet.cell(row,col).value.strip():
                    return row,col
            
        raise Exception("Couldn't find empty spot!")
    
    def subscribe_menu(self,date2,preference,name):
        
        row,col = self.search_for_empty_spot(date2,preference)
        
        self.sheet.update_cell(row,col,name)
        
        return "OK!"
    
    def unsubscribe_menu(self,date2,name):
        
        row,col = self.search_for_name(date2,name)
        
        self.sheet.update_cell(row,col,"")
        
        return "OK!"
    
        