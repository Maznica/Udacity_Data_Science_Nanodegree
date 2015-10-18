import pandas
import pandasql
import csv
import datetime

'''
# P R O B L E M  S E T  2.1
# N U M B E R  O F  R A I N Y  D A Y S 
'''

def num_rainy_days(filename):    
    weather_data = pandas.read_csv(filename)
    q = """
    select count(*) from weather_data where rain=1
    """
    #Execute your SQL command against the pandas frame
    rainy_days = pandasql.sqldf(q.lower(), locals())
    return rainy_days

'''
# P R O B L E M  S E T  2.2
# T E M P E R A T U R E  B Y  F O G G Y-C O N D I T I O N S 
'''

def max_temp_aggregate_by_fog(filename):
    weather_data = pandas.read_csv(filename)
    q = """
    select fog,max(cast (maxtempi as integer)) from weather_data group by fog
    """
    temp_by_fog = pandasql.sqldf(q.lower(), locals())
    return temp_by_fog


'''
# P R O B L E M  S E T  2.3
# M E A N  (M E A N) T E M P E R A T U R E  O N  W E E K E N D 
'''

def avg_mean_temperature(filename):
    weather_data = pandas.read_csv(filename)
    q = """
    select avg(cast (meantempi as integer)) from weather_data where\
    cast (strftime('%w', date) as integer) in (0,6)
    """
    #Execute your SQL command against the pandas frame
    mean_temp_weekends = pandasql.sqldf(q.lower(), locals())
    return mean_temp_weekends

'''
# P R O B L E M  S E T  2.4
# M E A N  (M I N) T E M P E R A T U R E  O N  R A I N Y D A Y S
'''

def avg_min_temperature(filename):
    weather_data = pandas.read_csv(filename)
    q = """
    select avg(cast (mintempi as integer)) from weather_data \
    where rain=1 and mintempi>55;
    """
    #Execute your SQL command against the pandas frame
    mean_temp_rain = pandasql.sqldf(q.lower(), locals())
    return mean_temp_rain

'''
# P R O B L E M  S E T  2.5
# F I X  T U R N S T I L E  D A T A
'''

def fix_turnstile_data(filenames):
    for name in filenames:
        f=open(name, 'rb')
        reader=csv.reader(f)
        w=open("updated_" + name, 'wb')
        writer=csv.writer(w)
        for row in reader:
            header=row[0:3]
            rowclipped=row[len(header):]
            x = 0
            for i in range(len(rowclipped)/5):
                writer.writerow(header + rowclipped[x:(x+5)])
                x=x+5
        f.close()
        w.close()
 
# I found a hint at piazza: https://piazza.com/class/i23uptiifb6194?cid=116

'''
# P R O B L E M  S E T  2.6
# C R E A T E  M A S T E R  D A T A
'''

def create_master_turnstile_file(filenames, output_file):
    w=open(output_file, 'wb')
    writer=csv.writer(w)
    writer.writerow(['C/A','UNIT','SCP','DATEn','TIMEn', \
    'DESCn','ENTRIESn','EXITSn'])
    for filename in filenames:
        f=open(filename, 'rb')
        reader=csv.reader(f)
        for line in reader:
            writer.writerow( line )
        f.close()
    w.close()
    # alternatively, we can combine the data in the following way:
    ''' 
    with open(output_file, 'w') as master_file:
       master_file.write('C/A,UNIT,SCP,DATEn,TIMEn,DESCn,ENTRIESn,EXITSn\n')
       for filename in filenames:
           for line in open(filename, 'r'):
               master_file.write( line ) 
    '''

'''
# P R O B L E M  S E T  2.7
# F I L T E R  B Y  R E G U L A R
'''                

def filter_by_regular(filename):
    turnstile_data = pandas.read_csv(filename)
    turnstile_data=turnstile_data[turnstile_data['DESCn']=='REGULAR']
    return turnstile_data  
 
'''
# P R O B L E M  S E T  2.8
# G E T  H O U R L Y  E N T R I E S
'''      

def get_hourly_entries(df):
    df['ENTRIESn_hourly']=df['ENTRIESn']-df['ENTRIESn'].shift(1)
    df['ENTRIESn_hourly'].fillna(1,inplace=True)
    return df

# Alternatively we can use following codes
'''
df['ENTRIESn_hourly'] = 1 #Create new column and set all values to 1 (instead of using .shift)
for i in range(0,len(df)-1):
df.ENTRIESn_hourly[i+1] = df.ENTRIESn[i+1] - df.ENTRIESn[i] 
return df

df['Entriesn_hourly'] = df['ENTRIESn'].diff(1)
df['Entriesn_hourly'].fillna(1, inplace = True)
'''

'''
# P R O B L E M  S E T  2.9
# G E T  H O U R L Y  E X I T S
'''   

def get_hourly_exits(df):
    df['EXITSn_hourly'] = df['EXITSn'].diff(1)
    df['EXITSn_hourly'].fillna(0, inplace = True)
    #df['EXITSn_hourly'] = df.EXITSn.sub(df.EXITSn.shift()).fillna(0)
    return df

'''
# P R O B L E M  S E T  2.10
# T R A N S F O R M  T I M E  T O  T H E  H O U R 
'''   

def time_to_hour(time):
    if time[0]=='0':
        hour=int(time[1])
    else:
        hour=int(time[:2])
    return hour

'''
# P R O B L E M  S E T  2.11
# F O R M A T  D A T E S  I N  S U B W A Y  D A T A
'''   

def reformat_subway_dates(date):
    date_formatted = datetime.datetime.strptime(date,"%m-%d-%y")
    date_formatted=date_formatted.strftime("%Y-%m-%d")
    return date_formatted


'''
# S O M E  T E S T S
'''  
print num_rainy_days('weather_underground.csv')
print max_temp_aggregate_by_fog('weather_underground.csv')
print avg_mean_temperature('weather_underground.csv')
print avg_min_temperature('weather_underground.csv')

print fix_turnstile_data(['turnstile_110528.txt', 'turnstile_110604.txt'])
print create_master_turnstile_file(['updated_turnstile_110528.txt', \
'updated_turnstile_110604.txt'],"turnstile_data_master_opt1.csv")

turnstile_data=filter_by_regular("turnstile_data_master_opt1.csv")
print filter_by_regular("turnstile_data_master_opt1.csv")
#turnstile_data.to_csv('masterdata_regular.csv')

#turnstile_master = pandas.read_csv('masterdata_regular.csv')
student_df = turnstile_data.groupby(['C/A','UNIT','SCP']).apply(get_hourly_entries)
print student_df
#student_df.to_csv('masterdata_entries_hour.csv')

#turnstile_entries= pandas.read_csv('masterdata_entries_hour.csv')
student_dif = student_df.groupby(['C/A','UNIT','SCP']).apply(get_hourly_exits)
print student_dif
student_dif['Hour']=student_dif['TIMEn'].map(time_to_hour)
print student_dif

subway_final = student_dif.copy(deep=True)
subway_final['DATEn'] = subway_final['DATEn'].map(reformat_subway_dates)
print subway_final

'''
# J O I N  W I T H  W E A T H E R  D A T A 
'''  
weather_final=pandas.read_csv('weather_underground.csv')
final_data=subway_final.merge(weather_final, left_on='DATEn', right_on='date')


