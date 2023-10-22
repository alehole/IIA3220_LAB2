import pymongo
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd 
import numpy as np
import statistics as st
from array import array
client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["PID1"]

## PV
t = []
data = []
collection = database["PV"]
# Retrieving and Formatting Data
for document in collection.find():
    MeasurementValue = document["MeasurementValue"]
    MeasurementDateTime = document["MeasurementDateTime"]
    timeformat = "%Y --%m --%d %H:%M:%S"
    MeasurementDateTime = datetime.strptime(MeasurementDateTime, timeformat)
    data.append(MeasurementValue)
    t.append(MeasurementDateTime)
    
# Plotting
plt.plot(t, data, 'o-')
plt.title('PV')
plt.xlabel('t[s]')
plt.ylabel('Temp[degC]')
plt.grid()
plt.show()


#Convert list to Python array using numpy.array
dataArr = np.array(data)
dataframe = pd.DataFrame(dataArr)
dfmean = dataframe.rolling(10).mean()
dfStd = dataframe.rolling(10).std()
plt.plot(t,dataArr, color="blue",label="PV")
plt.plot(t, dfmean, color="red", label="Rolling Mean PV")
plt.plot(t, dfStd, color="black", label = "Rolling Standard Deviation PV")
plt.title("PV, Rolling Mean, Standard Deviation")
plt.legend(loc="best")
plt.grid()
plt.show()


Min = min(dataArr)
print("min temperature is: " + str(Min) + " celsius" )
Max = max(dataArr)
print("Max temperature is: " + str(Max) + " celsius" )
Avg = st.mean(dataArr)
print("Average temperature is: " + str(Avg) + " celsius" )


