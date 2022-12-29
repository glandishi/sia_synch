#script to create templates for BC from SIA db

import pyodbc
from settings import db_user, db_password
from datetime import date,timedelta,datetime
#Functions
def createTimeframes(start,end):
    tomm = datetime.now().replace(hour=0, minute=0) + timedelta(days=1)
    startDate = datetime.strftime(tomm + timedelta(minutes=start*30),"%Y-%m-%d %H:%M")
    endDate = datetime.strftime(tomm + timedelta(minutes=(end+1)*30),"%Y-%m-%d %H:%M")
    #print("Start date: %s" % startDate)
    #print("End date: %s" % endDate)
    return startDate,endDate
def getTomorrowDay():
    template = "_______"
    tomorrow = date.isoweekday(date.today()) #should be +1 but then list will take next value, not proper one
    day = list(template)
    day[tomorrow] = "1"
    day = "".join(day)
    return day
def getSuff(srv):
    suff = ""
    if srv == '10':
        suff = "bel_"
    elif srv == '12':
        suff = "can_"
    elif srv == '16':
        suff = "bin_"
    else:
        suff = "is4_"
    return suff
def getTimeframe(timeFrame):
    seq = False
    seq_num = 0
    time_list = []
    temp_list = []
    for ttime in range(len(timeFrame)):
        if timeFrame[ttime] == '1':
            if seq == False:
                seq = True
                seq_num += 1
                # print("seq_num:",seq_num)
            # print("MATCH position",ttime+1,"value:",time[ttime], "time:",(ttime+1)/2,"listID:",seq_num-1, seq)
            #time_list[seq_num - 1].append(ttime)
            temp_list.append(ttime)
        else:
            if seq:
                time_list.append(temp_list)
                temp_list = []
            seq = False
            # print("----- position", ttime + 1, "value:", time[ttime],"seq_num-1:",seq_num-1, seq)
    return time_list

#template
template_header = "SECTION=MAINTENANCEMODE\nACTION=ADD\nCHANGE NUMBER=SIA_synch_" +  datetime.strftime(datetime.now(),"%Y-%m-%d") + "\nDESCRIPTION=sia synch\nENDACTION=1\n"
template_from = ""
template_until = ""
template_end = "MONITORING SOLUTION=\n"
#DB
#conn_str = 'Driver={ODBC Driver 17 for SQL Server};Server=FGSFDS\SIA_DB;Database=sia_prod;UID=andy;PWD=123456;'
conn_str = 'Driver={ODBC Driver 13 for SQL Server};Server=%IP;Database=win_asset_prod;UID=' + db_user + ';PWD=' + db_password + ';'
conn = pyodbc.connect(conn_str)
day = getTomorrowDay()
query2 = "SELECT RebootTime, count(*) FROM [win_asset_prod].[inventory].[maintenance] where RebootDay like ? group by RebootTime"
query3 = "select sys.name FROM [win_asset_prod].[inventory].[server] as sys left join [win_asset_prod].[inventory].[maintenance] as sw on sys.id = sw.serverid where sw.RebootDay like ? and sw.RebootTime = ? and (sys.name like 'xw10%' or sys.name like 'xc10%' or sys.name like 'xw12%' or sys.name like 'xc12%' or sys.name like 'xw16%' or sys.name like 'xc16%' or sys.name like 'xw01%' or sys.name like 'xc01%')"
cursor = conn.cursor()
cursor.execute(query2, day)
timeframes = [] #start and end date of specific set
time_serv = {} #dictionary with timeframe_id: servers relation
temp_num, temp_name = 0, ""
print("working for that day:", day)
for i in cursor: #getting list of distinct timeframe_id
    time_serv[i.RebootTime] = [] #creating empty list as a value for timeframe_id key
for i in time_serv: #getting server list for specific timeframe_id
    cursor.execute(query3, day, i)
    for d in cursor: #add servername values to the respective timeframe_id key in time_serv dictionary
        if d:
                time_serv[i].append(d.name)
conn.close()


for i in time_serv: #done for each key in the time_serv dictionary
    if time_serv[i]:
        tmp_tf = getTimeframe(i) #this will produce list or lists with staring and ending halfhour, ie [[0,1],[10,11,12,13]] = from 00:00 to 01:00 and from 05:00 to 07:00
        for d in tmp_tf: #iterating through nested lists
                timeframes = createTimeframes(d[0],d[-1]) #taking first and last values to create start and end dates
                #print("timeframes start end",timeframes)
                template_from = "FROM=" + str(timeframes[0]) + "\n"
                template_until = "UNTIL=" + str(timeframes[1]) + "\n"
                #print("from %s until %s" % (template_from, template_until))
        temp_num += 1
        temp_name = "/temporary/sia_rpm/output/" + datetime.strftime(datetime.now() ,"%y-%m-%d") + "_" + str(temp_num) + ".txt"
    #my_file = open(temp_name, "w", encoding="utf-8")
        my_file = open(temp_name, "w")
        template_str = template_header + template_from + template_until + template_end
        my_file.write(template_str)
        for srv in time_serv[i]: #looping through the values list of specific key and add each server to the end of file
                srv = getSuff(srv[2:4]) + srv + "\n"
                #srv ="bel_" +srv + "\n"
                my_file.write(srv.lower())
my_file.close()
