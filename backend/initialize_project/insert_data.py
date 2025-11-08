from mysql_class import MySQLdb
import os
import pandas

if __name__ == '__main__':
    host = "127.0.0.1"
    user = "root"
    password = "123456"
    database = "csc3170_project"
    db = MySQLdb(host, user, password, database)
    cursor = db.connection.cursor()

    ## 按照结构建立数据库表格

    # warden 表格
    warden_cols = [
        "WARDEN_ID",
        "WARDEN_NAME",
        "WARDEN_PHONE_NUM",
        "WARDEN_EMAIL_ADDRESS",
        "WARDEN_PASSWORD",
        "WARDEN_GENDER",
        "WARDEN_TBPROCESSED_REQ_NUM",
        "WARDEN_HBPROCESSED_REQ_NUM"
    ]

    # building 表格
    building_cols = [
        "BUILDING_ID",
        "WARDEN_ID"
    ]

    # tutor 表格
    tutor_cols = [
        "TUTOR_ID",
        "TUTOR_NAME",
        "TUTOR_PHONE_NUM",
        "TUTOR_EMAIL_ADDRESS",
        "TUTOR_PASSWORD",
        "TUTOR_TBPROCESSED_REQ_NUM",
        "TUTOR_HBPROCESSED_REQ_NUM",
        "TUTOR_GENDER"
    ]

    # floor 表格
    floor_cols = [
        "BUILDING_ID",
        "FLOOR_ID",
        "TUTOR_ID",
        "FLOOR_GENDER"
    ]

    # room 表格
    room_cols = [
        "ROOM_ID",
        "BUILDING_ID",
        "FLOOR_ID",
        "IS_EMPTY",
        "ELECTRICITY_BALANCE",
        "REQ_TBPROCESSED_NUM",
        "REQ_HBPROCESSED_NUM",
        "REMAIN_BEDS"
    ]

    # bed 表格
    bed_cols = [
        "ROOM_ID",
        "BED_ID",
        "AVAILABILITY"
    ]

    # student 表格
    student_cols = [
        "STUDENT_ID", 
        "STUDENT_NAME",
        "BUILDING_ID",
        "FLOOR_ID",
        "ROOM_ID",
        "BED_ID",
        "GENDER",
        "STUDENT_PHONE_NUM",
        "MAJOR",
        "SCHOOL",
        "STUDENT_EMAIL_ADDRESS",
        "PASSWORD",
    ]
    
    ## 插入基础数据

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(BASE_DIR, '..', 'data')

    dorm_path = os.path.join(data_dir, 'dormitory_information.xlsx')
    room_path = os.path.join(data_dir, 'room_basic_information.xlsx')
    student_path = os.path.join(data_dir, 'student_info_2000.xlsx')

    dorm_data = pandas.read_excel(dorm_path)
    room_data = pandas.read_excel(room_path)
    student_data = pandas.read_excel(student_path)
    # student_data = pandas.read_excel('new_students.xlsx')

    db.insert_into_table(dorm_data, [2, 3, 4, 5, 6, 7, 16, 17], 'warden', warden_cols)    # 可变
    db.insert_into_table(dorm_data, [0, 2], 'building', building_cols)  # 不可变
    db.insert_into_table(dorm_data, [8, 9, 10, 11, 12, 13, 15, 14], 'tutor', tutor_cols)  # 不可变
    db.insert_into_table(dorm_data, [0, 1, 8, 14], 'floor', floor_cols) # 可变
    db.insert_into_table(room_data, [2, 0, 1, 4, 6, 7, 8, 9], 'room', room_cols)   # 可变
    db.insert_into_table(room_data, [2, 3, 5], 'bed', bed_cols) # 可变
    db.insert_into_table(student_data, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'student', student_cols) # 可变
    