//Q1
SELECT b.bid, bname, count(r.bid) as reserved_times FROM boats as b  inner join reserves as r on b.bid = r.bid group by b.bid, b.bname order by b.bid;

//Q2
SELECT s.sid, s.sname FROM sailors as s WHERE NOT  exists (SELECT * FROM boats as b WHERE b.color = 'r
ed' AND NOT exists (SELECT * FROM reserves as r WHERE s.sid = r.sid AND b.bid = r.bid));

//Q3
SELECT distinct s.sid, s.sname FROM sailors as s, reserves as r, boats as b
WHERE s.sid = r.sid AND b.color ='red' AND r.bid = b.bid AND s.sid NOT in (SELECT s.sid FROM sailors as s, reserves as r, boats as b WHERE s.sid = r.sid AND r.bid = b.bid AND b.color != 'red' );

//Q4
SELECT b.bid, b.bname, COUNT(r.bid) as Num_Reservations FROM boats as b, reserves as r
WHERE b.bid = r.bid group by b.bid
order by Num_Reservations DESC limit 1;

//Q5
SELECT s.sid, s.sname FROM sailors as s
WHERE s.sid NOT IN (SELECT r.sid FROM reserves as r INNER JOIN boats as b ON r.bid = b.bid WHERE b.color = 'red')
order by s.sid;

//Q6
SELECT AVG(age) as Average_Age FROM sailors WHERE rating = 10; 

//Q7
SELECT s.* FROM sailors as s
INNER JOIN (SELECT rating, MIN(age) as min_age FROM sailors GROUP BY rating) as s1
ON s.rating = s1.rating AND s1.min_age = s.age
ORDER BY s.rating;

//Q8
SELECT temp.bid, temp.sid, MAX(count_res) FROM (SELECT r.bid as bid, r.sid as sid, COUNT(r.bid) as count_res
from reserves r, sailors s
where r.sid = s.sid
GROUP BY r.bid, r.sid
ORDER BY count_res DESC) as temp
GROUP BY temp.bid
ORDER BY temp.bid;