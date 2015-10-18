import sys
import string


'''
# P R O B L E M  S E T  5.1
# R I D E R S H I P  P E R  S T A T I O N
'''

# mapper 

def mapper():
    for line in sys.stdin:
        data=line.strip().split(",")
        if len(data)!=22 or data[1]=='UNIT':
            continue
        unit=data[1]
        entries=data[6]
        print "{0}\t{1}".format (unit, entries)

mapper()

# reducer

def reducer():
    old_key=None
    entries=0
    for line in sys.stdin:
        data=line.strip().split("\t")
        if len(data)!=2:
            continue
        this_key, count = data
        if old_key and old_key != this_key:
            print"{0}\t{1}".format(old_key, entries)
            entries = 0
            
        old_key = this_key
        entries += float(count)
    if old_key != None:
        print"{0}\t{1}".format(old_key, entries)  
      
reducer()


'''
# P R O B L E M  S E T  5.2
# R I D E R S H I P  B Y  W E A T H E R  T Y P E 
'''

# mapper 

def mapper():
    def format_key(fog, rain):
        return '{}fog-{}rain'.format(
            '' if fog else 'no',
            '' if rain else 'no'
        )

    for line in sys.stdin:
        data=line.strip().split(",")
        if len(data)!=22 or data[1]=='UNIT':
            continue
        rain=float(data[15])
        fog=float(data[14])
        entries=data[6]
        print "{0}\t{1}".format (format_key(fog,rain), entries)
    	
mapper()

# reducer
def reducer():
    riders = 0      # The number of total riders for this key
    num_hours = 0   # The number of hours with this key
    old_key = None

    for line in sys.stdin:
        data=line.strip().split("\t")
        if len(data)!=2:
            continue
        this_key, count = data
        if old_key and old_key != this_key:
            print"{0}\t{1}".format(old_key, riders/num_hours)
            riders = 0
            num_hours=0
            
        old_key = this_key
        riders += float(count)
        num_hours += 1.0
    if old_key != None:
        print"{0}\t{1}".format(old_key, riders/num_hours)
    
reducer()

'''
# P R O B L E M  S E T  5.3
# B U S I E S T  H O U R
'''
 
# mapper 
def mapper():

    for line in sys.stdin:
        data=line.strip().split(",")
        if len(data)!=22 or data[1]=='UNIT':
            continue
        unit=data[1]
        entries=data[6]
        date=data[2]
        time=data[3]
        c="{0}\t{1}\t{2}\t{3}".format (unit, entries, date, time)
        #logging.info(c)
        print c
        
        # your code here

mapper()


# reducer
def reducer():

    max_entries = 0
    old_key = None
    datetime = ''

    for line in sys.stdin:
        data = line.strip().split("\t")
        if len(data) != 4:
            continue
            
        this_key, count, data, time = data
        count = float(count)
        
        if old_key and old_key != this_key:
            print "{0}\t{1}\t{2}".format(old_key,datetime,max_entries)
            max_entries = 0
            datetime = ""
            
        old_key = this_key
        if count >= max_entries:
            max_entries = count
            datetime = str(data) + " " + str(time)
            
    if old_key != None:
        print "{0}\t{1}\t{2}".format(old_key, datetime, max_entries)

reducer()


























