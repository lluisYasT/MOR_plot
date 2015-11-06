#!/usr/bin/env python

import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline
import mysql.connector as myc

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


def duration_calls_profit(dias_media):
    query ="SELECT date, SUM(billsec) as duration, COUNT(billsec) as calls, SUM(IF(reseller_price <= 0.001, user_price, reseller_price)) - SUM(provider_price) as profit FROM calls WHERE disposition='ANSWERED' GROUP BY date"
    rows = retrieve_db(query)
    date = [];
    duration = [];
    calls = [];
    profit = [];
    for column in rows:
        date.append(column[0])
        duration.append(float(column[1])/60.0)
        calls.append(float(column[2]))
        profit.append(float(column[3]))

    duration_avg = media(date, duration, dias_media)
    calls_avg = media(date, calls, dias_media)
    profit_avg = media(date, profit, dias_media)
    
    plt.subplot(311)
    plt.plot(date, duration_avg, 'r')
    plt.title("Duración (m)")
    plt.subplot(312)
    plt.plot(date, calls_avg, 'g')
    plt.title("Nº de llamadas")
    plt.subplot(313)
    plt.plot(date, profit_avg, 'b')
    plt.title("Beneficio")

    plt.show()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dias_media = float(sys.argv[1])
    else:
        dias_media=15.0
    
    duration_calls_profit(dias_media)
