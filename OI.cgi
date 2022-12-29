#!/bin/python
". /home/ncosys/sqllib/db2profile"
import sys
import cgi, cgitb, os
cgitb.enable(display=1, logdir=None, context=5, format="html")
os.environ['IBM_DB_DIR']="/home/ncosys/sqllib"
os.environ['IBM_DB_LIB']="/home/ncosys/sqllib/lib"
os.environ['IBM_DB_INCLUDE']="/home/ncosys/sqllib/include"
os.environ['DB2_HOME']="/home/ncosys/sqllib"
os.environ['DB2INSTANCE']="ncosys"
os.environ['DB2LIB']="/home/ncosys/sqllib/lib"
os.environ['IBM_DB_HOME']="/home/ncosys/sqllib"
os.environ['LD_LIBRARY_PATH']="/home/db2_client/clidriver/lib"
os.environ['LD_LIBRARY_PATH']="/home/ncosys/sqllib/lib"
import ibm_db
import ibm_db_dbi
import base64
from settings import db_user, db_b64pass

# Create instance of FieldStorage
form = cgi.FieldStorage()

conn_str='database=infodb;hostname=%IP;port=50000;protocol=tcpip;uid=' + db_user + ';pwd=' +  base64.b64decode(db_b64pass.decode("utf-8"))

ibm_db_conn = ibm_db.connect(conn_str,'','')
conn = ibm_db_dbi.Connection(ibm_db_conn)
if conn is None:
    print ("\nERROR: Unable to connect.")
    print ("<h2> Unable to connect</h2>")

col_name = ['OPERATORINSTRUCTION','MONITORINGSOLUTION','SUBACCOUNT','SEVERITY','ALERTKEY','ITMDISPLAYITEM','Mobile_Number','GROUP','MANUALSMS', 'Node', 'MANUALLINK_1','MANUALLINK_2','MANUALADRESS_1','MANUALADRESS_2']

# Get data from fields
#node_attr = form.getvalue('$selected_rows.Node')
alertkey_attr  = form.getvalue('$selected_rows.AlertKey')
if alertkey_attr == None :
        url = "event=loadapp&value=sr&additionalevent=insert&additionaleventvalue=REPORTEDBY=%EMAIL|EXTERNALSYSTEM=EMAIL|OWNERGROUP=%GROUP|DESCRIPTION=Request from Operation team for OI|DESCRIPTION_LONGDESCRIPTION=AlertKey:{}|CLASSIFICATIONID=OTHER_REQUEST|IMPACT=3|URGENCY=1|SITEID=BXD-01|PLUSPCUSTOMER=IDT-00|CLASSIFICATIONID=REQUEST".format(alertkey_attr)
        long_url = '%URL?{}'.format(url)
        print """
<table style="border-collapse: collapse; width: 80%;" border="1">
<tbody>
<tr>
<tr><td class="tableheader"> Click The link to Create SR for NON AlertKey</td>
<td class="tabledata"><a target="_blank" rel="noopener noreferrer" href="{}">CREATE SR</a></td>
</tr>
</tbody>
</table>""".format(long_url,long_url)
        exit (-1)
subaccount_attr  = form.getvalue('$selected_rows.SubAccount')
monitoringsolution_attr  = form.getvalue('$selected_rows.MonitoringSolution')
severity_attr  = form.getvalue('$selected_rows.Severity')
serial_attr = form.getvalue('$serial_row.Serial')
query_exten = ""


def isAttrsEmpty():
        if severity_attr == '' or  monitoringsolution_attr == '' or subaccount_attr == '':
                return True
        return False


if isAttrsEmpty() == True:
        print('<center><div class="headerWebtop" style="color:red">There is no Operator Instruction for the ALERTKEY:{}, Create SR using below link</div></center>'.format(alertkey_attr))
        print('<div>MONSOL:{}, SEVERITY:{}, SUBACCOUNT:{}, ALERTKEY:{}</div>'.format(monitoringsolution_attr,severity_attr,subaccount_attr,alertkey_attr))
        url = "event=loadapp&value=sr&additionalevent=insert&additionaleventvalue=REPORTEDBY=SYOPER@IS4F.COM|EXTERNALSYSTEM=EMAIL|OWNERGROUP=%GROUP|DESCRIPTION=Request from Operation team for OI|DESCRIPTION_LONGDESCRIPTION=SubAccount:{} Monsol:{} AlertKey:{} Severity:{}|CLASSIFICATIONID=OTHER_REQUEST|IMPACT=3|URGENCY=1|SITEID=BXD-01|PLUSPCUSTOMER=IDT-00|CLASSIFICATIONID=REQUEST".format(subaccount_attr,monitoringsolution_attr,alertkey_attr,severity_attr)
        long_url = 'https://servicedesk.cs.is4f.com/maximo/ui/maximo.jsp?{}'.format(url)
        exit(-1)

if len(alertkey_attr) == 8 :
        query_exten = "SubAccount='{}' AND AlertKey='{}'".format(subaccount_attr,alertkey_attr)
else:
        query_exten = "Severity='{}' AND SubAccount='{}' AND AlertKey='{}' AND lower(MonitoringSolution)='{}'".format(severity_attr,subaccount_attr,alertkey_attr,monitoringsolution_attr)





def executeQuery(query):
        return ibm_db.exec_immediate(ibm_db_conn,query)

query = "SELECT OPERATORINSTRUCTION,MONITORINGSOLUTION,SUBACCOUNT,SEVERITY,ALERTKEY,ITMDISPLAYITEM,Mobile_Number,GROUP,MANUALSMS from OPERATORINSTRUCTION where {}".format(query_exten)
result = executeQuery(query)
cols = ibm_db.fetch_tuple(result)
sHTMLHeader="""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
<STYLE type="text/css">
h1.headerTool
{
        font-size: 30pt;
        font-weight: bold;
        letter-spacing: -4px;
}

.headerReg, .headerTM
{
        font-size: 20pt;
        vertical-align: super;
}

.headerWebtop
{
        font-size: 38;
        font-weight: 500;
        letter-spacing: 0px;
        color: black;
}

body
{
        background-color: #ECECEC;
        color: #000508;
        font-family: verdana, serif; font-size:18pt;
}

.systemMsg
{
        font-size: 30pt;
        font-weight: bold;
}
.tableheader{
width: 20.0484%;
color: black;
border-style: none none solid none;
padding-top: 21px;
padding-bottom: 21px;
background-color: white;
padding-right: 20px;
text-align:right;
letter-spacing: 1px;
}

.tabledata{
width: 50.9516%;
border-style: none none solid none;
padding-right: 10px;
padding-top: 16px;
padding-bottom: 16px;
padding-left: 20px;
background-color: white;
font-weight: bold;
font-family: verdana;
white-space: pre-line;
}

</STYLE>
</HEAD>
<BODY>
"""
print (sHTMLHeader)
print ('<center><div class="headerWebtop">Operator Instruction  </div></br></br>')

if cols:
        i=0
        for x in cols :
                if i==0:
                        x = x.encode("utf-8",errors='ignore')
                        x = x.replace("\n", "<br />")
                if i==3:
                        if x==2:
                                x = '2 - Warning'
                        if x==3:
                                x = '3 - Minor'
                        if x==4:
                                x = '4 - Critical'
                        if x==5:
                                x = '5 - Fatal'
                print """
<table style="border-collapse: collapse; width: 80%;" border="1">
<tbody>
<tr>
<td class="tableheader">{}: </td>
<td class="tabledata">{}</td>
</tr>
</tbody>
</table>""".format(col_name[i],x)
                i= i+1
else:
        print('<center><div class="headerWebtop" style="color:red">There is no Operator Instruction for the ALERTKEY:{}, Create SR using below link</div></center>'.format(alertkey_attr))
        #print('<div>MONSOL:{}, SEVERITY:{}, SUBACCOUNT:{}, ALERTKEY:{}</div>'.format(monitoringsolution_attr,severity_attr,subaccount_attr,alertkey_attr))
        url = "event=loadapp&value=sr&additionalevent=insert&additionaleventvalue=REPORTEDBY=SYOPER@IS4F.COM|EXTERNALSYSTEM=EMAIL|OWNERGROUP=%GROUP|DESCRIPTION=Request from Operation team for OI|DESCRIPTION_LONGDESCRIPTION=SubAccount:{} Monsol:{} AlertKey:{} Severity:{}|CLASSIFICATIONID=OTHER_REQUEST|IMPACT=3|URGENCY=1|SITEID=%SITE|PLUSPCUSTOMER=%CUSTOMER|CLASSIFICATIONID=REQUEST".format(subaccount_attr,monitoringsolution_attr,alertkey_attr,severity_attr)
        long_url = '%URL?{}'.format(url)
        print """
<table style="border-collapse: collapse; width: 80%;" border="1">
<tbody>
<tr>
<tr><td class="tableheader"> click the link </td>
<td class="tabledata"><a target="_blank" rel="noopener noreferrer" href="{}">CREATE SR</a></td>
</tr>
</tbody>
</table>""".format(long_url,long_url)
print ("</center></h3>")
print ("</body>")
print ("</html>")
