#!/usr/bin/env python

import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.interpolate import spline
import mysql.connector as myc
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import time
import re

def media(date,data,dias=30):
    length = len(data)
    i = 0
    avg = []
    data_temp = 0
    while i < len(data):
        data_temp += data[i]
        if i%dias==0:
            avg.append(data_temp / float(dias))
            data_temp = 0
        elif i==len(data)-1:
            avg.append(data_temp / float(i%dias))
        i += 1

    xold = np.linspace(0,1,len(avg))
    xnew = np.linspace(0,1,len(data))
    data_smooth = spline(xold,avg,xnew)

    return data_smooth

def retrieve_db(query):
    try:
        cnx = myc.connect(user="mor", password="mor", host="127.0.0.1", port=3306, database="mor")


        cursor = cnx.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()
    except myc.Error as error:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    else:
        cnx.close()

    return rows


def duration_calls_profit(dias_media, date_start=None, date_end=None):
    if date_start:
        date_start_query = " AND date>='" + date_start.isoformat() + "'";
    else:
        date_start_query = ""

    if date_end:
        date_end_query = " AND date<='" + date_end.isoformat() + "'";
    else:
        date_end_query = " AND date<='" + date.today().isoformat() + "'";

    query ="SELECT date, SUM(billsec) as duration, COUNT(billsec) as calls, SUM(IF(reseller_price <= 0.001, user_price, reseller_price)) - SUM(provider_price) as profit " + \
            "FROM calls WHERE disposition='ANSWERED'" + date_start_query + date_end_query + " GROUP BY date"
    rows = retrieve_db(query)
    dates = [];
    duration = [];
    calls = [];
    profit = [];
    for column in rows:
        dates.append(column[0])
        duration.append(float(column[1])/60.0)
        calls.append(float(column[2]))
        profit.append(float(column[3]))

    duration_avg = media(dates, duration, dias_media)
    calls_avg = media(dates, calls, dias_media)
    profit_avg = media(dates, profit, dias_media)
    
    plt.subplot(311)
    plt.plot(dates, duration_avg, 'r')
    plt.title("Duración (m)")
    plt.subplot(312)
    plt.plot(dates, calls_avg, 'g')
    plt.title("Nº de llamadas")
    plt.subplot(313)
    plt.plot(dates, profit_avg, 'b')
    plt.title("Beneficio")

    plt.show()

def calls_hour(date_start, date_end):
    if date_start:
        date_start_query = " AND date>='" + date_start.isoformat() + "'";
    else:
        date_start_query = ""

    if date_end:
        date_end_query = " AND date<='" + date_end.isoformat() + "'";
    else:
        date_end_query = " AND date<='" + date.today().isoformat() + "'";

    query = "SELECT calldate FROM calls WHERE disposition='ANSWERED'" +\
            date_start_query + date_end_query

    rows = retrieve_db(query)
    calldates = [ 60*(t[0].hour*60 + t[0].minute) + t[0].second for t in rows]
    hours = [x*60*60 for x in range(0,24)]
    labels=map(lambda x: str(x/3600), hours)

    plt.xticks(hours,labels)
    plt.hist(calldates,bins=24)

    plt.show()


def string2date(date_string):
    try:
        date_object = datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as err:
        print("Wrong date format\n")
        print("It should be like: 2015-10-25")
        exit(-1)
    if date_object < datetime.today():
        return date_object
    else:
        print("Date can't be in the future")
        exit(-1)

if __name__ == "__main__":

    date_start=datetime(1970,1,1)
    date_end = datetime.today()
    if len(sys.argv) >= 2:
        date_start = string2date(sys.argv[1])
    if len(sys.argv) >= 3:
        date_end = string2date(sys.argv[2])

    dias_media = round((date_end - date_start).days/20)
    if dias_media < 1:
        dias_media = 1
    elif dias_media > 60:
        dias_media = 60
    
    print(dias_media)
    #duration_calls_profit(dias_media, date_start, date_end)
    calls_hour(date_start, date_end)
