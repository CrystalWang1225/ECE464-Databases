from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey, Table
import pytest
metadata = MetaData()

url_path = "mysql+pymysql://root:rootroot1234@localhost/hw11"
engine = create_engine(url_path, echo=True)
connection = engine.connect()

Session = sessionmaker(bind = engine)
session = Session()

Base = declarative_base()

boats = Table('boats', metadata,
              Column('bid', Integer, primary_key=True),
              Column('bname', String(20)),
              Column('color', String(15)),
              Column('length', Integer))

sailors = Table('sailors', metadata,
                Column('sid', Integer, primary_key=True),
                Column('sname', String(20)),
                Column('rating', Integer),
                Column('dob', Date))


reserves = Table('reserves',metadata,
                 Column('sid', Integer, ForeignKey('sailors.sid'),primary_key = True),
                 Column('bid', Integer, ForeignKey('boats.bid'), primary_key=True),
                 Column('day', Date),
                 Column('price', Integer))

employees = Table('employees', metadata,
                  Column('eid', Integer, primary_key= True),
                  Column('ename', String(20)),
                  Column('start_date', Date),
                  Column('wage', Integer))

work_sheets = Table('work_sheets', metadata,
                    Column('eid', Integer, ForeignKey('employees.eid')),
                    Column('date', Date),
                    Column('total_hours', Integer))
costs = Table('costs', metadata,
              Column('cid', Integer, primary_key=True),
              Column('eid', Integer, ForeignKey('employees.eid'), primary_key=True),
              Column('bid', Integer, ForeignKey('boats.bid'), primary_key=True),
              Column('cost', Integer),
              Column('date', Date))

# function to get biweekly wage
def get_bi_wage():
    sql = "SELECT employees.eid, employees.ename ,employees.wage * work_sheets.total_hours AS Wages FROM work_sheets JOIN employees ON employees.eid=work_sheets.eid WHERE date >= '2020/10/10' AND date <= '2020/10/27';"
    result = connection.execute(sql)
    r = result.fetchall()
    return r

# function to calculate the total the boat company has to pay the employee's by
def get_total_wage():
    result = get_bi_wage()
    total_wage = 0
    for each in result:
        total_wage += each[2]
    assert total_wage == 890
    return total_wage

def get_boat_profit():
    sql = "SELECT r.bid, SUM(r.price) - SUM(c.cost) AS profit from costs as c JOIN reserves as r ON c.bid =r.bid  GROUP BY r.bid ORDER BY r.bid;"
    result = connection.execute(sql)
    r = result.fetchall()
    return r

def get_total_profit():
    result = get_boat_profit()
    total_profit = 0
    for each in result:
        total_profit += each[1]
    total_profit = total_profit - get_total_wage()
    assert total_profit == 2200

if __name__ == '__main__':
    metadata.drop_all(engine)
    metadata.create_all(engine)

    with open('part3.sql', 'r') as line:
        for each in line:
            each = each.strip('\n')
            connection.execute(each)

    get_total_wage()
    get_total_profit()

