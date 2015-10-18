# -*- coding: utf-8 -*-
"""
Created on Fri Jan 02 15:56:33 2015

@author: mmasika

Final Project of Intro to Data Science
"""

# Important packages

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy
import scipy.stats
import statsmodels.api as sm
import pandasql
from ggplot import *



# Obtaining and cleaning data

turnstile_data = pd.read_csv("turnstile_weather_v2.csv")
turnstile_data['Count']=1
print turnstile_data.head(n=3)
print turnstile_data.info()

# There are no missing values in the data

'''
# U N I T  &  S T A T I O N
'''

data_unit=turnstile_data[['UNIT','Count']].groupby('UNIT').count()

# The same dataframe we can get by means of pivot table
# data_unit_pivot=turnstile_data.pivot_table(['Count'],rows=['UNIT'],aggfunc=sum)

print turnstile_data['UNIT'].describe()
print turnstile_data['station'].describe()
#print turnstile_data[['UNIT','station'].describe()

# We have information about 240 Units, the smallest occurs in the dataset
# 88 times and the biggest 186 times

# Relationship to the staion

# Either we can use crosstable - however, the table is not that clear or 
# again a groupby crosstab_statunit= pd.crosstab(turnstile_data.UNIT,
# turnstile_data.station,margins=True)


data_station=turnstile_data[['station','Count']].groupby(['station']).count()
data_unitstation=turnstile_data[['station','UNIT','Count']].groupby(['UNIT','station']).count()

# From this analysis we see that one station can have more than one unit but 
# one unit has only one station

# Another possibility is to use the pandasql

q = """
select distinct UNIT
from turnstile_data 
"""
#Execute your SQL command against the pandas frame
unique_unit = pandasql.sqldf(q.lower(), locals())

q = """
select distinct station
from turnstile_data 
"""
#Execute your SQL command against the pandas frame
unique_station = pandasql.sqldf(q.lower(), locals())

q = """
select distinct UNIT, station
from turnstile_data 
"""
#Execute your SQL command against the pandas frame
unique_unitstation = pandasql.sqldf(q.lower(), locals())

# Which stations have more than one unit?

unique_unitstation['count']=1

q = """
select station, sum(count)
from unique_unitstation group by station
"""
#Execute your SQL command against the pandas frame
uniques = pandasql.sqldf(q.lower(), locals())

print uniques[uniques['sum(count)']>1]

# There are some stations which have more than one unit - e.g. 50 ST with 3 units   
    
'''
# D A T E
'''

print turnstile_data['DATEn'].describe()

index = pd.DatetimeIndex(turnstile_data['DATEn'])

print index

# So we have information about the whole May (31 days)

# It is interesting to know if each unit provides informations for the whole
# months

q = """
select distinct UNIT, DATEn
from turnstile_data 
"""
#Execute your SQL command against the pandas frame
unique_unitdate = pandasql.sqldf(q.lower(), locals())

# As the number of observations<7440 some of the units were not available for
# the whole month

unique_unitdate['DATEn']=pd.to_datetime(unique_unitdate['DATEn'])
unique_unitdate=unique_unitdate.sort(['DATEn'])

print unique_unitdate

q = """
select distinct UNIT, count(DATEn)
from unique_unitdate group by  (UNIT) 
"""
count_unitdate = pandasql.sqldf(q.lower(), locals())

print count_unitdate[count_unitdate['count(daten)']<31]

# 8 Units have less than 31 days. The most extreme case is R459 with only 16 days

'''
# T I M E
'''
q="""
select distinct TIMEn, hour , count(Count)
from turnstile_data group by TIMEn,hour
"""

unique_time=pandasql.sqldf(q.lower(),locals())

# There is information only for 6 hours - 0,4,8,12,16,20
# The fewest infor we have for hour 8 - may influence enters and exits hourly
# Especially a peak by 12 hours

'''
# E N T R I E S
'''

print turnstile_data['ENTRIESn'].describe()

q = """
select count(*) from turnstile_data where ENTRIESn==0
"""
print pandasql.sqldf(q.lower(), locals())
print turnstile_data[turnstile_data['ENTRIESn']==0]

# 14 observations with zero Entries, again mostly at 8 hour

print turnstile_data[(turnstile_data['UNIT']=='R100')  & (turnstile_data['DATEn']=='5/3/2011')]

# Alternatively

print turnstile_data.loc[(turnstile_data['UNIT']=='R100')  & (turnstile_data['DATEn']=='5/3/2011'),\
["UNIT","DATEn","ENTRIESn","ENTRIESn_hourly"]]


'''
# E X I T S
'''

print turnstile_data['EXITSn'].describe()

q = """
select count(*) from turnstile_data where EXITSn==0
"""
print pandasql.sqldf(q.lower(), locals())
print turnstile_data[turnstile_data['EXITSn']==0]

# 14 observations with zero Exits, again mostly at 8 hour


'''
# E N T R I E S  H O U R L Y
'''

print turnstile_data['ENTRIESn_hourly'].describe(percentiles=[.05, .1, .25, 0.5, 0.75, 0.9, 0.95, 0.99])


print turnstile_data[['UNIT','DATEn','hour']][turnstile_data['ENTRIESn_hourly']>30000]

# There are some observation with very large number of hourly entries




'''
# E X I T S  H O U R L Y
'''

print turnstile_data['EXITSn_hourly'].describe(percentiles=[.05, .1, .25, 0.5, 0.75, 0.9, 0.95, 0.99])

# There are some observation with very large number of hourly entries


'''
# D A Y  &  W E E K E N D
'''

print turnstile_data['day_week'][turnstile_data['weekday']==1].describe(percentiles=[.05, .1, .25, 0.5, 0.75, 0.9, 0.95, 0.99])

# Weekday is 1 if it is a day in the week (Mon - Friday), i.e. day_week is from 0 to 4

'''
# W E A T H E R  C O N D I T I O N S
'''

# rain

turnstile_data_rainprecipi=turnstile_data[["rain", "meanprecipi"]]
turnstile_data_rainprecipi["rain_string"] = \
np.where(turnstile_data_rainprecipi["rain"] == 1, "raining", "not raining")
turnstile_data_rainprecipi.groupby("rain_string").describe()

print turnstile_data['conds'].describe()

turnstile_data['rain_time']=np.where(turnstile_data['precipi']>0,1,0)

# there is 12 unique weather conditions:
# 5 Cloud conditions - clear, scaterred clouds, partly cloudy, mostly cloudy and overcast
# 4 Rain conditions - light drizzle, light rain, rain, heavy rain
# 3 Foggy conditions - fog, mist and haze

# The differences between separat conditions are not that clear

q= """
select distinct conds,fog,rain_time, count(Count)
from turnstile_data group by conds,fog,rain_time
"""

unique_conds=pandasql.sqldf(q.lower(),locals())

# Differences between rainy conditions

print turnstile_data['precipi'][turnstile_data['conds']=="Light Drizzle"].describe\
(percentiles=[.05, .1, .25, 0.5, 0.75, 0.9, 0.95, 0.99])

print turnstile_data['precipi'][turnstile_data['conds']=="Light Rain"].describe\
(percentiles=[.05, .1, .25, 0.5, 0.75, 0.9, 0.95, 0.99])

print turnstile_data['precipi'][turnstile_data['conds']=="Rain"].describe\
(percentiles=[.05, .1, .25, 0.5, 0.75, 0.9, 0.95, 0.99])

print turnstile_data['precipi'][turnstile_data['conds']=="Heavy Rain"].describe\
(percentiles=[.05, .1, .25, 0.5, 0.75, 0.9, 0.95, 0.99])

# Light Drizzle - almost no rain max=0.01, 90% of observations at 0, mean=0.0007
# Light Rain - 25% of observations at 0, but higher than drizzle, mean =0.017
# Rain - still some observations at 0, but the mean is 0.137
# No Zeros, but smaller precipi than by rain

# New rain variable - generated from the weather conditions variable

turnstile_data['rain_conds']=np.where((turnstile_data['conds']=='Light Drizzle') | \
(turnstile_data['conds']=='Light Rain') | (turnstile_data['conds']=='Rain') | \
(turnstile_data['conds']=='Heavy Rain'),1,0)

turnstile_data_raincond=turnstile_data[["rain_conds", "ENTRIESn_hourly"]]
turnstile_data_raincond["rain_string"] = \
np.where(turnstile_data_raincond["rain_conds"] == 1, "raining", "not raining")
turnstile_data_raincond.groupby("rain_string").describe()

turnstile_precipi=turnstile_data.groupby("conds",as_index=False)\
['precipi'].mean()

#################################################################
#################################################################
#################################################################
#
# S T A T I S T I C A L  T E S T
#
#################################################################
#################################################################
#################################################################

# Normality of the hourly entries

(k2, pvalue) = scipy.stats.normaltest(turnstile_data["ENTRIESn_hourly"])
print k2, pvalue

# Rain - daily variable

def entries_histogram(turnstile_weather):
    plt.figure()
    turnstile_weather['ENTRIESn_hourly'][turnstile_weather['rain']==0].\
    hist(bins=100,stacked=True,color='g', alpha=0.7,label='No Rain')
    turnstile_weather['ENTRIESn_hourly'][turnstile_weather['rain']==1].\
    hist(bins=100,stacked=True,color='b', alpha=0.4,label='Rain')
    plt.title("Hourly Entries by weather conditions (rain/no rain)")
    plt.xlabel("Hourly Entries")
    plt.xlim([0,10000])
    plt.ylabel("Frequency")
    plt.legend()
    return plt

plot = entries_histogram(turnstile_data)


# Alternatively we can get some summary statistics

turnstile_data_rain=turnstile_data[["rain", "ENTRIESn_hourly"]]
turnstile_data_rain["rain_string"] = \
np.where(turnstile_data_rain["rain"] == 1, "raining", "not raining")
turnstile_data_rain.groupby("rain_string").describe()
# Statistical difference in metro usage by (rain and no rain)

# Mann-Whitney U test

def mann_whitney_plus_means(turnstile_weather,variable):
    entries_rain=turnstile_weather['ENTRIESn_hourly'][turnstile_weather[variable]==1]
    entries_norain=turnstile_weather['ENTRIESn_hourly'][turnstile_weather[variable]==0]
    with_rain_mean=np.mean(entries_rain)
    without_rain_mean=np.mean(entries_norain)
    U,p=scipy.stats.mannwhitneyu(entries_rain,entries_norain)
    m_u=len(entries_rain)*len(entries_norain)/2
    sigma_u = np.sqrt(len(entries_rain)*len(entries_norain)*(len(entries_rain)+len(entries_norain)+1)/12)
    z=(U-m_u)/sigma_u
    p=2*(1-scipy.stats.norm.cdf(np.absolute(z)))      
    return with_rain_mean, without_rain_mean, U, p 



# Welch's t test

def welch_test(turnstile_weather,variable):
    entries_rain=turnstile_weather['ENTRIESn_hourly'][turnstile_weather[variable]==1]
    entries_norain=turnstile_weather['ENTRIESn_hourly'][turnstile_weather[variable]==0]
    with_rain_mean=np.mean(entries_rain)
    without_rain_mean=np.mean(entries_norain)
    t,p=scipy.stats.ttest_ind(entries_rain,entries_norain, equal_var = False)
    return with_rain_mean, without_rain_mean,t,p


# Results:

# Daily rain

print mann_whitney_plus_means(turnstile_data,'rain')
print welch_test(turnstile_data,'rain')

# Hourly rain

print mann_whitney_plus_means(turnstile_data,'rain_time')
print welch_test(turnstile_data,'rain_time')

# Rain conditions

print mann_whitney_plus_means(turnstile_data,'rain_conds')
print welch_test(turnstile_data,'rain_conds')



#################################################################
#################################################################
#################################################################
#
# D A T A  V I S U A L I Z A T I O N
#
#################################################################
#################################################################
#################################################################

# HOURLY ENTRIES DISTRIBUTION BY RAIN AND NO RAIN

# for matplotlib implementation see the above section

# ggplot

turnstile_data['Rain']=np.where(turnstile_data['rain']==1, 'rain', 'no rain') 

gg1 = ggplot(turnstile_data,aes(x='ENTRIESn_hourly', fill='Rain'))+\
geom_histogram(binwidth=300) + xlab('Number of hourly entries') + \
ylab('Frequency') + ggtitle("Histogram: Hourly Entries by rainy conditions") + \
scale_x_continuous(breaks=(0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000),\
labels=(0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000),limits=(0,10000)) + \
facet_wrap('Rain')


print gg1
ggsave ('histogram_ggplot_rain.png',gg1)



# SUBWAY USAGE BY STATION

turnstile_station=turnstile_data.groupby(['station'],as_index=False)\
['ENTRIESn_hourly'].mean()
gg2=ggplot(turnstile_station,aes(x='station',y='ENTRIESn_hourly'))+\
geom_bar(stat='identity') + xlab('Station') + \
ylab('Hourly Entries') + ggtitle("Hourly Entries by station") + \
scale_x_date(breaks=date_breaks('weeks'), labels=date_format('%m-%d'))

print gg2
ggsave('barplot_stations.png',gg2)

# The same figure with matplotlib
plt.figure(figsize=(18,18))
turnstile_station.plot(kind='bar') # this row makes the figure
plt.title("Hourly Entries by Station")
plt.xlabel("Station")
plt.ylabel("Hourly Entries")
plt.tick_params(axis="both", which="both", bottom="off", top="off",  
                labelbottom="off", left="off", right="off", labelleft="on") 
plt.legend()

plt.savefig("barplot2_stations.png",dpi=180)


# Weather Conditions

turnstile_data['conds_h']=np.where((turnstile_data['conds']=='Light Drizzle') | \
(turnstile_data['conds']=='Light Rain') | (turnstile_data['conds']=='Rain') | \
(turnstile_data['conds']=='Haze') | (turnstile_data['conds']=='Heavy Rain'),\
"conditions_2","conditions_1") 

turnstile_conditions=turnstile_data.groupby(['conds','conds_h'],as_index=False)\
['ENTRIESn_hourly'].mean()

gg3=ggplot(turnstile_conditions[(turnstile_conditions['conds']!='Fog') & \
(turnstile_conditions['conds']!='Mist') & (turnstile_conditions['conds_h']\
=='conditions_1') ],aes(x='conds',y='ENTRIESn_hourly'))+\
geom_bar(stat='identity') + xlab('Conditions') + \
ylab('Hourly Entries') + ggtitle("Hourly Entries by Weather conditions") + \
scale_x_discrete("conds")

print gg3
ggsave('barplot_conds_1.png',gg3)

turnstile_cond2=turnstile_conditions[turnstile_conditions['conds_h']\
=='conditions_2']

"""
gg4=ggplot(turnstile_cond2,aes(x='conds',y='ENTRIESn_hourly'))+\
geom_bar(stat='identity') + xlab('Conditions') + \
ylab('Hourly Entries') + ggtitle("Hourly Entries by Weather conditions") + \
scale_x_discrete("conds")

print gg4
ggsave('barplot_conds_2.png',gg4)
"""

# Rain conditions

turnstile_rain=turnstile_data.groupby(turnstile_data['rain'],as_index=False)\
['ENTRIESn_hourly'].mean()

gg5=ggplot(turnstile_rain,aes(x='rain',y='ENTRIESn_hourly',width=.5))+\
geom_bar(stat='identity') + xlab('Rain_day') + scale_x_discrete\
(breaks=(0,1),labels=(0,1)) +\
ylab('Hourly Entries') + ggtitle("Hourly Entries by daily rain conditions")

print gg5
ggsave('barplot_rain_1.png',gg5)

turnstile_raintime=turnstile_data.groupby(turnstile_data['rain_time'],as_index=False)\
['ENTRIESn_hourly'].mean()

turnstile_data_raintime=turnstile_data[["rain_time", "ENTRIESn_hourly"]]
turnstile_data_raintime.groupby("rain_time").describe()

gg6=ggplot(turnstile_raintime,aes(x='rain_time',y='ENTRIESn_hourly',width=.5))+\
geom_bar(stat='identity') + xlab('Rain_hour') + scale_x_discrete\
(breaks=(0,1),labels=(0,1)) +\
ylab('Hourly Entries') + ggtitle("Hourly Entries by hourly rain conditions")

print gg6
ggsave('barplot_rain_2.png',gg6)

turnstile_rainconds=turnstile_data.groupby(turnstile_data['rain_conds'],as_index=False)\
['ENTRIESn_hourly'].mean()

turnstile_raincond=turnstile_data[["rain_conds", "ENTRIESn_hourly"]]
turnstile_raincond.groupby('rain_conds').describe()

gg7=ggplot(turnstile_rainconds,aes(x='rain_conds',y='ENTRIESn_hourly',width=.5))+\
geom_bar(stat='identity') + xlab('Rain_Conditions') + scale_x_discrete\
(breaks=(0,1),labels=(0,1)) +\
ylab('Hourly Entries') + ggtitle("Hourly Entries by hourly rain conditions")

print gg7
ggsave('barplot_rain_3.png',gg7)


# Precipitation rate

gg8=ggplot(turnstile_data,aes(x='precipi',y='ENTRIESn_hourly'))+\
geom_point() + xlab('Actual Precipitation Rate') + geom_smooth() + \
ylab('Hourly Entries') + ggtitle("Hourly Entries by actual precipitation rate")

print gg8
ggsave('precipi_1.png',gg8)

gg9=ggplot(turnstile_data,aes(x='meanprecipi',y='ENTRIESn_hourly'))+\
geom_point() + xlab('Daily Average of Precipitation Rate') + \
ylab('Hourly Entries') + ggtitle("Hourly Entries by daily average of precipitation rate")

print gg9
ggsave('precipi_2.png',gg9)

# Temperature

gg10=ggplot(turnstile_data,aes(x='tempi',y='ENTRIESn_hourly'))+\
geom_point() + xlab('Actual Temperature') + geom_smooth(method='loess') +\
ylab('Hourly Entries') + ggtitle("Hourly Entries and actual temperature")

print gg10
ggsave('temperature_1.png',gg10)

gg11=ggplot(turnstile_data,aes(x='meantempi',y='ENTRIESn_hourly'))+\
geom_point() + xlab('Daily average temperature') + geom_smooth(method='loess') + \
ylab('Hourly Entries') + ggtitle("Hourly Entries by average temperature (daily)")

print gg11
ggsave('temperature_2.png',gg11)

gg11_1=ggplot(turnstile_data,aes(x='meantempi',y='ENTRIESn_hourly'))+\
geom_point() + xlab('Daily average temperature') + geom_smooth(method='loess') + \
ylab('Hourly Entries') + ggtitle("Hourly Entries by average temperature (daily)") 
print gg11_1

# Days

turnstile_days=turnstile_data.groupby('day_week',as_index=False)\
['ENTRIESn_hourly'].mean()

gg12=ggplot(turnstile_days,aes(x='day_week',y='ENTRIESn_hourly',width=.75))+\
geom_bar(stat='identity') + xlab('Days') + ylab('Hourly Entries') + \
ggtitle("Hourly Entries by day in the week") + \
scale_x_discrete(breaks=(0,1,2,3,4,5,6),\
labels=('Mon','Tue','Wed','Thu','Fri','Sat','Sun'))

print gg12
ggsave('entries_days.png',gg12)




#################################################################
#################################################################
#################################################################
#
# Linear Regression
#
#################################################################
#################################################################
#################################################################


# The main estimations are already provided in PS 3. Here we make two 
# robustness checks.

def predictions_ols(weather_turnstile):
    values=weather_turnstile['ENTRIESn_hourly']
    m=len(values)
    weather_turnstile['weekdaymprecipi']=weather_turnstile['weekday']*weather_turnstile['meanprecipi']
    features = weather_turnstile[['meanprecipi','weekday','weekdaymprecipi','meantempi']]
    features['ones'] = np.ones(m)
    dummy_hour = pd.get_dummies(weather_turnstile['hour'], prefix='hour')
    dummy_hour=dummy_hour.drop('hour_0.0',1)
    dummy_units = pd.get_dummies(weather_turnstile['UNIT'], prefix='unit')
    dummy_units=dummy_units.drop('unit_R012',1)
    features = features.join(dummy_units)
    features = features.join(dummy_hour)
    model = sm.OLS(values, features).fit(use_correction=True,use_t=True)
    new=model.get_robustcov_results(cov_type='HAC',maxlags=1)
    return new.predict(features), new.summary()

print predictions_ols(turnstile_data)



def predictions_ols1(weather_turnstile):
    values=weather_turnstile['ENTRIESn_hourly']
    m=len(values)
    weather_turnstile['weekdayrain']=weather_turnstile['weekday']*weather_turnstile['rain']
    features = weather_turnstile[['rain','weekday','weekdayrain','meantempi']]
    features['ones'] = np.ones(m)
    dummy_hour = pd.get_dummies(weather_turnstile['hour'], prefix='hour')
    dummy_hour=dummy_hour.drop('hour_0.0',1)
    dummy_units = pd.get_dummies(weather_turnstile['station'], prefix='st')
    dummy_units=dummy_units.drop('st_34 ST-PENN STA',1)
    features = features.join(dummy_units)
    features = features.join(dummy_hour)
    model = sm.OLS(values, features).fit()
    new=model.get_robustcov_results(cov_type='HAC',maxlags=1)
    return new.predict(features), new.summary()


print predictions_ols1(turnstile_data)














 
    
    