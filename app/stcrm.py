#coding=utf-8
from flask import *
#import sqlt
import sqlite3
from functools import wraps
from time import asctime
from datetime import date,datetime,timedelta
import os
import xlrd

from flask.ext import excel
from flask.ext.sqlalchemy import SQLAlchemy

from flask_paginate import Pagination, get_page_args


app=Flask(__name__)
app.config.from_pyfile('app.cfg')
app.secret_key="has"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SuperTendCRM.db'
db = SQLAlchemy(app)

def datetime2timestamp(dt, convert_to_utc=False):
  ''' Converts a datetime object to UNIX timestamp in milliseconds. '''
  if isinstance(dt, datetime):
    if convert_to_utc: # 是否转化为UTC时间
      dt = dt + timedelta(hours=-8) # 中国默认时区
    timestamp = (dt - datetime(1970, 1, 1)).total_seconds()
    return long(timestamp)
  return dt

def timestamp2datetime(timestamp, convert_to_local=False):
  ''' Converts UNIX timestamp to a datetime object. '''
  if isinstance(timestamp, (int, long, float)):
    dt = datetime.utcfromtimestamp(timestamp)
    if convert_to_local: # 是否转化为本地时间
      dt = dt + timedelta(hours=8) # 中国默认时区
    return dt
  return timestamp

def timestamp_utc_now():
  return datetime2timestamp(datetime.utcnow())

def timestamp_now():
  return datetime2timestamp(datetime.now())

@app.before_request
def before_request():
    g.conn = sqlite3.connect('SuperTendCRM.db')
    g.conn.row_factory = sqlite3.Row
    g.cur = g.conn.cursor()


@app.teardown_request
def teardown(error):
    if hasattr(g, 'conn'):
        g.conn.close()

class custinfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custid = db.Column(db.Text)
    custname = db.Column(db.Text)
    contact = db.Column(db.Text)
    baseinfo = db.Column(db.Text)
    address = db.Column(db.Text)
    status = db.Column(db.Text)
    fine = db.Column(db.Text)
    content = db.Column(db.Text)
    usedbattery = db.Column(db.Text)
    memo = db.Column(db.Text)
    date = db.Column(db.Text)
    saleman = db.Column(db.Text)
    createtime = db.Column(db.Text)
    updatetime = db.Column(db.Text)

def login_required(test):
    @wraps(test)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return test(*args,**kwargs)
        else:
            flash('you need to login first')
            return redirect(url_for('login'))
    return wrap

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != 'abc':
            flash('Invalid username')
        elif request.form['password'] != '123':
            flash('Invalid password')
        else:
            session['logged_in']=True
            flash('You were logged in')
            return redirect(url_for('get_custlist'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    return redirect(url_for('welcome'))

#---------------------------------------------

@app.route('/')
def welcome():
    return render_template('home.html')

@app.route('/cust_list')
@login_required
def get_custlist():
    return render_template('custlist.html')

@app.route('/custlistjson')
@login_required
def get_custlist_json():
    g.cur.execute('select id, custid, custname, contact, baseinfo, address, status, fine, content, usedbattery, memo, date, saleman, createtime, updatetime from custinfo order by date desc')
    value=[dict(id=i[0], custid=i[1], custname=i[2], contact=i[3], baseinfo=i[4], address=i[5], status=i[6], fine=i[7], content=i[8], usedbattery=i[9], memo=i[10], date=i[11], saleman=i[12], createtime=(timestamp2datetime(long(i[13]),True)).strftime('%Y-%m-%d %H:%M:%S'), updatetime=(timestamp2datetime(long(i[14]),True)).strftime('%Y-%m-%d %H:%M:%S'), link='/cust/%d'%(i[0]), delete='/cust_del/%d'%(i[0]) ) for i in g.cur.fetchall()]
    return jsonify({'data':value})


@app.route('/cust/<int:id>')
@login_required
def get_custinfo(id):
    g.cur.execute('select id, custid, custname, contact, baseinfo, address, status, fine, content, usedbattery, memo, date, saleman, createtime, updatetime from custinfo where id = %d'%(id) )
    value=[dict(id=i[0], custid=i[1], custname=i[2], contact=i[3], baseinfo=i[4], address=i[5], status=i[6], fine=i[7], content=i[8], usedbattery=i[9], memo=i[10], date=i[11], saleman=i[12], createtime=(timestamp2datetime(long(i[13]),True)).strftime('%Y-%m-%d %H:%M:%S'), updatetime=(timestamp2datetime(long(i[14]),True)).strftime('%Y-%m-%d %H:%M:%S') ) for i in g.cur.fetchall()]
    return render_template('cust.html',value=value)

@app.route('/cust')
@login_required
def get_cust_form():
    value=[dict(id='', custid='', custname='', contact='', baseinfo='', address='', status='', fine='', content='', usedbattery='', memo='', date='', saleman='', createtime='', updatetime='' )]
    return render_template('cust.html', value=value)

@app.route('/cust', methods=['POST'])
@login_required
def submit_custinfo():
    if len(request.form['id']) == 0:
        g.cur.execute('insert into custinfo(custid, custname, contact, baseinfo, address, status, fine, content, usedbattery, memo, date, saleman, createtime, updatetime) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [request.form['custid'], request.form['custname'], request.form['contact'], request.form['baseinfo'], request.form['address'], request.form['status'], request.form['fine'], request.form['content'], request.form['usedbattery'], request.form['memo'], request.form['date'], request.form['saleman'], timestamp_utc_now(), timestamp_utc_now() ])
    else:
        g.cur.execute('update custinfo set custid=?, custname=?, contact=?, baseinfo=?, address=?, status=?, fine=?, content=?, usedbattery=?, memo=?, date=?, saleman=?, updatetime=? where id = %d'%(int(request.form['id'])), [request.form['custid'], request.form['custname'], request.form['contact'], request.form['baseinfo'], request.form['address'], request.form['status'], request.form['fine'], request.form['content'], request.form['usedbattery'], request.form['memo'], request.form['date'], request.form['saleman'], timestamp_utc_now() ])
    g.conn.commit()

    return render_template('custlist.html')

@app.route('/cust_del/<int:id>')
@login_required
def delete_custinfo(id):
    g.cur.execute('delete from custinfo where id = %d'%(id) )
    g.conn.commit()

    return render_template('custlist.html')

@app.route('/mcalendar')
@login_required
def get_mcalendar():
    return render_template('mcalendar.html')

@app.route('/mcalendarjson')
@login_required
def get_mcalendar_json():
    g.cur.execute('select distinct(substr(date, 0, 11)) from custinfo')
    value=[dict(startDate=i[0], endDate=i[0] ) for i in g.cur.fetchall()]
    return jsonify({'data':value})


@app.route("/export", methods=['GET'])
@login_required
def doexport():
    return excel.make_response_from_tables(db.session, [custinfo], "xls")

@app.route("/customer_export", methods=['GET'])
@login_required
def docustomexport():
    query_sets = custinfo.query.all()
    column_names = ['id', 'custid', 'custname', 'contact', 'baseinfo', 'address', 'status', 'fine', 'content', 'usedbattery', 'memo', 'date', 'saleman']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls")

@app.route('/sys_admin')
@login_required
def sys_admin():
    return render_template('sys_admin.html')

def open_excel(file= 'file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print (str(e))

# 根据索引获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的所以  ，by_index：表的索引
def excel_table_byindex(file= 'file.xls',colnameindex=0,by_index=0):
    data = open_excel(file)
    table = data.sheets()[by_index]
    nrows = table.nrows #行数
    ncols = table.ncols #列数
    colnames =  table.row_values(colnameindex) #某一行数据
    list =[]
    for rownum in range(1,nrows):
        row = table.row_values(rownum)
        if row:
            app = {}
            for i in range(len(colnames)):
               app[colnames[i]] = row[i]
            list.append(app)
    return list

ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/customer_import', methods=['GET', 'POST'])
@login_required
def customer_import():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename

        # 判断文件名是否合规
        if file and allowed_file(filename):
            file.save(os.path.join('./upload', filename))
        else:
            flash('失败:上传文件格式不对')
            return "导入失败!上传文件格式不对"

        # 添加到数据库
        tables = excel_table_byindex(file='./upload/' + filename)
        sucess = 0
        for row in tables:
                # 判断表格式是否对
                if 'custid' not in row or 'custname' not in row or\
                    'contact' not in row or 'baseinfo' not in row or\
                    'status' not in row or 'fine' not in row or\
                    'content' not in row or 'usedbattery' not in row or\
                    'memo' not in row or 'date' not in row or\
                    'saleman' not in row:
                    flash('失败:excel表格式不对')
                    return "导入失败!excel表格式不对"
                # 判断字段是否存在
                #if row['custid'] != '' and row['custname'] != '' and \
                #    row['contact'] != '' and row['status'] != '':
                if row['date'] =='':
                    tmpdate=''
                else:
                    tmpdate=date(*(xlrd.xldate_as_tuple(row['date'], 0))[:3]).strftime('%Y-%m-%d')
                cust_info = custinfo(
                                custid=row['custid'],
                                custname=row['custname'],
                                contact=row['contact'],
                                baseinfo=row['baseinfo'],
                                address=row['address'],
                                status=row['status'],
                                fine=row['fine'],
                                content=row['content'],
                                usedbattery=row['usedbattery'],
                                memo=row['memo'],
                                date=tmpdate,
                                saleman=row['saleman'],
                                createtime = timestamp_utc_now(),
                                updatetime = timestamp_utc_now()
                                )
                # 判断是否id重复
                flag = True
                #if Device.query.filter_by(device_id=device.device_id).count() > 0:
                #    flash('失败:设备ID:%s已存在' %device.device_id)
                #    flag = False
                # 判断simid是否重复
                if flag:
                    db.session.add(cust_info)
                    sucess += 1
                else:
                    return "导入失败!重复数据!"
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return "导入失败!rollback!"
        return "导入成功!导入了" + str(sucess) + "条客户信息！"

@app.route('/sys_custs_deleteall')
@login_required
def sys_custs_deleteall():
    g.cur.execute('delete from custinfo' )
    g.conn.commit()

    return "清除所有客户信息成功！"

@app.route('/dictstatusjson')
@login_required
def get_dict_status_json():
    g.cur.execute('select id, dictvalue from dict where dictname="status"')
    value=[dict(id=i[0], status=i[1], delete='/dictstatusdel/%d'%(i[0]) ) for i in g.cur.fetchall()]
    return jsonify({'data':value})

@app.route('/dictstatusadd', methods=['POST'])
@login_required
def dict_status_add():
    if len(request.form['status'].strip()) == 0:
        return render_template('sys_admin.html')
    
    g.cur.execute('insert into dict(dictname, dictvalue)values("status", ?)', [request.form["status"]])
    g.conn.commit()

    return render_template('sys_admin.html')

@app.route('/dictstatusdel/<int:id>')
@login_required
def dict_status_del(id):
    g.cur.execute('delete from dict where id = %d'%(id) )
    g.conn.commit()

    return render_template('sys_admin.html')

if __name__ == '__main__':  
    app.run(host="0.0.0.0",port=8080, debug=False)
