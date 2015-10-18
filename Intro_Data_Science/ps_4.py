import pandas as pd
from ggplot import *
import numpy as np

# For all problems we work with the improved dataset

turnstile_data=pd.read_csv("turnstile_weather_v2.csv")

'''
# P R O B L E M  S E T  4.1
# H O U R L Y  E N T R I E S  B Y  R A I N  A N D  T I M E
'''

def plot_weather_data(turnstile_weather):
    by_hour_mean=turnstile_weather.groupby(['hour','rain'],\
    as_index=False)['ENTRIESn_hourly'].mean()
    by_hour_mean['Rain']=np.where(by_hour_mean['rain']==1, 'rain', 'no rain') 
    
    plot = ggplot(by_hour_mean,aes(x='hour',y='ENTRIESn_hourly', fill='Rain',width=2)) + \
    geom_bar(stat='identity') + \
    xlab('Hour') + ylab('Number of Entries') + \
    ggtitle("NYC Tube Entries by hour and rain conditions") + \
    scale_x_discrete(breaks=(0,4,8,12,16,20),\
    labels=(0,4,8,12,16,20),limits=(0,23)) + \
    scale_y_continuous(limits=(0,4000)) + facet_wrap('Rain')
    return plot

gg= plot_weather_data(turnstile_data)
print gg
ggsave ('barplot_rain_hour.png',gg)


'''
# P R O B L E M  S E T  4.2
# 
'''

def plot_weather_data_2(data):
    data['Weekday'] =np.where(data['weekday']==1, 'Weekday', 'Weekend')
    by_hour_day=data.groupby(['hour','Weekday'],as_index=False)\
    ['ENTRIESn_hourly'].mean()
    plot = ggplot(by_hour_day,aes(x='hour',y='ENTRIESn_hourly',\
    colour='Weekday',fill="Weekday",width=2)) + geom_line() + \
    xlab('Hour') + ylab('Number of Entries') + \
    ggtitle("NYC Tube Entries by hour and weekday/weekend") + \
    scale_x_discrete(breaks=(0,4,8,12,16,20),\
    labels=(0,4,8,12,16,20),limits=(0,23))
    return plot

gg1= plot_weather_data_2(turnstile_data)
print gg1
ggsave('lineplot_weekend_hour.png',gg1)
#ggsave ('barplot_rain_hour.png',gg)





























