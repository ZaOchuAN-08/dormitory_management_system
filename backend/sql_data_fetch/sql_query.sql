SELECT `STUDENT_ID`, `PASSWORD`
FROM student
WHERE room_id = 'C502'; --可更改为想要的房间

SELECT t.`TUTOR_ID`, t.`TUTOR_PASSWORD`
FROM tutor AS t
JOIN floor AS f ON t.`TUTOR_ID` = f.`TUTOR_ID`
WHERE f.`BUILDING_ID` = 'C' --可更改为想要的楼栋
  AND f.`FLOOR_ID` = '5'; --可更改为想要的楼层

SELECT w.`WARDEN_ID`, w.`WARDEN_PASSWORD`
FROM warden AS w
JOIN building AS b ON w.`WARDEN_ID` = b.`WARDEN_ID`
WHERE b.`BUILDING_ID` = 'C';  --可更改为想要的楼栋
