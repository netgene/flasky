import sqlite3 as Lite
con=Lite.connect('SuperTendCRM.db')
cur=con.cursor()
#cur.execute('drop table if exists cust_info')
#cur.execute('create table cust_info(id integer primary key autoincrement, custname text, companyname text, address text, post text, tel text, mobile text, fax text, memo text)')
#cur.execute('drop table if exists custinfo')
cur.execute('create table custinfo(id integer primary key autoincrement, custid text, custname text, contact text, baseinfo text, address text, status text, fine text, content text, usedbattery text, memo text, date text, createtime text, updatetime text, saleman text)')
cur.execute('create table dict(id integer primary key autoincrement, dictname text, dictvalue text')
con.commit()
