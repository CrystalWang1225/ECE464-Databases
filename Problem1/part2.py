from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func,PrimaryKeyConstraint,desc,asc,distinct
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pytest

url_path = "mysql+pymysql://root:rootroot1234@localhost/hw1"
engine = create_engine(url_path, echo=True)
connection = engine.connect()

# print(conn.execute("SELECT * from sailors").fetchall())

Base = declarative_base()


class Sailor(Base):
    __tablename__ = 'sailors'

    sid = Column(Integer, primary_key=True)
    sname = Column(String)
    rating = Column(Integer)
    age = Column(Integer)

    def __repr__(self):
        return "<Sailor(id=%s, name='%s', rating=%s, age =%s)>" % (self.sid, self.sname, self.rating, self.age)


class Boat(Base):
    __tablename__ = 'boats'

    bid = Column(Integer, primary_key=True)
    bname = Column(String)
    color = Column(String)
    length = Column(Integer)

    reservations = relationship("Reservation", backref=backref('Boat'))

    def __repr__(self):
        return "<Boat(id=%s, name='%s', color=%s, length=%s)>" % (self.bid, self.bname, self.color, self.length)

class Reservation(Base):
    __tablename__ = 'reserves'
    __table_args__ = (PrimaryKeyConstraint('sid', 'bid', 'day'),{})
    sid = Column(Integer, ForeignKey('sailors.sid'), primary_key=True)
    bid = Column(Integer, ForeignKey('boats.bid'),primary_key=True)
    day = Column(DateTime,primary_key=True)

    boats = relationship("Boat", backref=backref('Reservation'))
    sailors = relationship("Sailor", backref=backref('Reservation'))

    def __repr__(self):
        return "<Reservation(bid=%s, sid='0%s, day=%s)>" % (self.bid, self.sid, self.day)

'''
        Below contains the testing for ORM query with MYSQL queries using the queries from part 1
'''

def assert_query(orm_query, sql_query):
    #executing the result of  the sql query here
    res = connection.execute(sql_query)
    sql_list = []
    orm_list = []

    for each in res:
        sql_list.append(each)
    print("sql list: ", sql_list)

    for each in orm_query:
        orm_list.append(each)
    print("orm list:", orm_list)

    #checking if the list obtained by orm query is the same as that of sql query
    assert orm_list == sql_list

# Creating a session
Session = sessionmaker(bind = engine)
session = Session()

def test1():
    sql_query = "SELECT b.bid, bname, count(r.bid) as reserved_times FROM boats as b  inner join reserves as r on b.bid = r.bid group by b.bid, b.bname order by b.bid;"
    orm_query = session.query(Reservation.bid, Boat.bname, func.count(Reservation.bid)).filter(Reservation.bid == Boat.bid).group_by(Reservation.bid, Boat.bname).order_by(Reservation.bid)
    assert_query(orm_query, sql_query)

def test2():
    sql_query = "SELECT s.sid, s.sname FROM sailors as s WHERE NOT  exists (SELECT * FROM boats as b WHERE b.color = 'red' AND NOT exists (SELECT * FROM reserves as r WHERE s.sid = r.sid AND b.bid = r.bid));"
    q1 = session.query(Boat.bid).filter(Boat.color == "red")
    c = q1.count()
    orm_query = session.query(Sailor.sid, Sailor.sname).filter(Reservation.bid.in_(q1)).filter(Reservation.sid == Sailor.sid).group_by(Reservation.sid).having(func.count(distinct(Reservation.bid)) == c)
    assert_query(orm_query,sql_query)

def test3():
    sql_query = " SELECT distinct s.sid, s.sname FROM sailors as s, reserves as r, boats as b WHERE s.sid = r.sid AND b.color ='red' AND r.bid = b.bid AND s.sid NOT in (SELECT s.sid FROM sailors as s, reserves as r, boats as b WHERE s.sid = r.sid AND r.bid = b.bid AND b.color != 'red' );"
    q1 = session.query(Boat.bid).filter(Boat.color == "red")
    q2 = session.query(Reservation.sid).filter(Reservation.bid.in_(q1))
    q3 = session.query(Boat.bid).filter(Boat.color != "red")
    q4 = session.query(Reservation.sid).filter(Reservation.bid.in_(q3))
    orm_query = session.query(Sailor.sid, Sailor.sname).filter(Sailor.sid.in_(q2)).filter(Sailor.sid.notin_(q4))
    assert_query(orm_query,sql_query)

def test4():
    sql_query = "SELECT b.bid, b.bname, COUNT(r.bid) as Num_Reservations FROM boats as b, reserves as r WHERE b.bid = r.bid group by b.bid order by Num_Reservations DESC limit 1;"
    orm_query = session.query(Reservation.bid, Boat.bname, func.count(Reservation.bid)).filter(Boat.bid == Reservation.bid).group_by(Reservation.bid).order_by(desc(func.count(Reservation.bid))).limit(1)
    assert_query(orm_query,sql_query)

def test5():
    sql_query = "SELECT s.sid, s.sname FROM sailors as s WHERE s.sid NOT IN (SELECT r.sid FROM reserves as r INNER JOIN boats as b ON r.bid = b.bid WHERE b.color = 'red') order by s.sid;"
    q1 = session.query(Boat.bid).filter(Boat.color == "red")
    q2 = session.query(Reservation.sid).filter(Reservation.bid.in_(q1))
    orm_query = session.query(Sailor.sid, Sailor.sname).filter(Sailor.sid.notin_(q2))
    assert_query(orm_query,sql_query)


def test6():
    sql_query = "SELECT AVG(age) as Average_Age FROM sailors WHERE rating = 10;"
    orm_query = session.query(func.avg(Sailor.age)).filter(Sailor.rating == 10).all()
    assert_query(orm_query,sql_query)

# TODO:check this
def test7():
    sql_query = " SELECT s.* FROM sailors as s INNER JOIN (SELECT rating, MIN(age) as min_age FROM sailors GROUP BY rating) as s1 ON s.rating = s1.rating AND s1.min_age = s.age ORDER BY s.sid;"
    q1 = session.query(Sailor.rating, func.min(Sailor.age)).group_by(Sailor.rating).subquery('q1')
    print(q1)
    orm_query =  session.query(Sailor.sid, Sailor.sname, Sailor.rating, Sailor.age).join(q1).order_by(Sailor.sid)
    assert_query(orm_query,sql_query)


def test8():
    sql_query = "SELECT t.bname, t.bid, t.sname, t.sid, MAX(count_res) FROM (SELECT b.bname, r.bid, s.sname, r.sid, COUNT(r.bid) as count_res FROM reserves as r, sailors as s, boats as b WHERE r.sid = s.sid AND b.bid = r.bid GROUP BY r.bid, r.sid ORDER BY count_res) as t GROUP BY t.sid, t.bid ORDER BY t.bid;"
    q1 = session.query(Reservation.bid, Reservation.sid, func.count(Reservation.bid).label('ntotal')).group_by( Reservation.bid, Reservation.sid).order_by(func.count(Reservation.bid)).subquery('q1')
    q2 = session.query(Reservation.sid).filter(Reservation.bid.in_(q1))
    # q2 = session.query(q1.c.bid, q1.c.sid, func.max(q1.c.ntotal)).group_by(q1.c.bid).subquery('q2')
    orm_query = session.query(Sailor.sid, Sailor.sname, Sailor.rating, Sailor.age).join(q2)

    assert_query(orm_query,sql_query)

def test9():
    sql_query = "SELECT t.bname, t.bid, t.sname, t.sid, MAX(count_res) FROM (SELECT b.bname, r.bid, s.sname, r.sid, COUNT(r.bid) as count_res FROM reserves as r, sailors as s, boats as b WHERE r.sid = s.sid AND b.bid = r.bid GROUP BY r.bid, r.sid ORDER BY count_res) as t GROUP BY t.sid, t.bid ORDER BY t.bid;"
    q1 = session.query(Reservation.bid, Reservation.sid, func.max(func.count(Reservation.bid))).group_by(Reservation.bid, Reservation.sid)
    orm_query = session.query(Sailor.sid, Sailor.sname).filter(Sailor.sid.in_(q1))
    assert_query(orm_query, sql_query)

test1()
test2()
test3()
test4()
test5()
test6()
