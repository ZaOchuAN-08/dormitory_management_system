from mysql_class import MySQLdb

DB_HOST = '127.0.0.1'   #   Change to your host
DB_USER = 'root'        #   Change to your user name
DB_PASS = '123456'      #   Change to your password for sql
DB_NAME = 'csc3170_project'     #   Change to the database name

if __name__ == '__main__':

    db = MySQLdb(
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASS,
        database = DB_NAME
    )

    db.delete_all_tb(DB_NAME)  # 初始化

    ## 按照结构建立数据库表格

    # 创建 warden 表格
    warden_query = [
        "WARDEN_ID INT PRIMARY KEY",
        "WARDEN_NAME VARCHAR(50)",
        "WARDEN_PHONE_NUM VARCHAR(50)",
        "WARDEN_EMAIL_ADDRESS VARCHAR(50)",
        "WARDEN_PASSWORD INT",
        "WARDEN_GENDER VARCHAR(50)",
        "WARDEN_TBPROCESSED_REQ_NUM INT",
        "WARDEN_HBPROCESSED_REQ_NUM INT"
    ]
    db.create_table(DB_NAME, "warden", ", ".join(warden_query))

    # 创建 building 表格
    building_query = [
        "BUILDING_ID VARCHAR(50) PRIMARY KEY",
        "WARDEN_ID INT",
        "FOREIGN KEY (WARDEN_ID) REFERENCES warden(WARDEN_ID)"
    ]
    db.create_table(DB_NAME, "building", ", ".join(building_query))

    # 创建 tutor 表格
    tutor_query = [
        "TUTOR_ID INT PRIMARY KEY",
        "TUTOR_NAME VARCHAR(50)",
        "TUTOR_PHONE_NUM VARCHAR(50)",
        "TUTOR_EMAIL_ADDRESS VARCHAR(50)",
        "TUTOR_PASSWORD INT",
        "TUTOR_TBPROCESSED_REQ_NUM INT",
        "TUTOR_HBPROCESSED_REQ_NUM INT",
        "TUTOR_GENDER VARCHAR(50)"
    ]
    db.create_table(DB_NAME, "tutor", ", ".join(tutor_query))

    # 创建 floor 表格
    floor_query = [
        "BUILDING_ID VARCHAR(50)",
        "FLOOR_ID INT",
        "TUTOR_ID INT",
        "FLOOR_GENDER VARCHAR(50)",
        "PRIMARY KEY (BUILDING_ID, FLOOR_ID)",
        "FOREIGN KEY (BUILDING_ID) REFERENCES building(BUILDING_ID)",
        "FOREIGN KEY (TUTOR_ID) REFERENCES tutor(TUTOR_ID)"
    ]
    db.create_table(DB_NAME, "floor", ", ".join(floor_query))

    # 创建 room 表格
    room_query = [
        "ROOM_ID VARCHAR(50) PRIMARY KEY",
        "BUILDING_ID VARCHAR(50)",
        "FLOOR_ID INT",
        "IS_EMPTY INT",
        "ELECTRICITY_BALANCE FLOAT(50)",
        "REQ_TBPROCESSED_NUM INT",
        "REQ_HBPROCESSED_NUM INT",
        "REMAIN_BEDS INT",
        "FOREIGN KEY (BUILDING_ID, FLOOR_ID) REFERENCES floor(BUILDING_ID, FLOOR_ID)"
    ]
    db.create_table(DB_NAME, "room", ", ".join(room_query))

    # 创建 bed 表格
    bed_query = [
        "ROOM_ID VARCHAR(50)",
        "BED_ID VARCHAR(50)",
        "AVAILABILITY INT",
        "PRIMARY KEY (ROOM_ID, BED_ID)",
        "FOREIGN KEY (ROOM_ID) REFERENCES room(ROOM_ID)"
    ]
    db.create_table(DB_NAME, "bed", ", ".join(bed_query))

    # 创建 student 表格
    student_query = [
        "STUDENT_ID INT PRIMARY KEY", 
        "STUDENT_NAME VARCHAR(50)",
        "BUILDING_ID VARCHAR(50)",
        "FLOOR_ID INT",
        "ROOM_ID VARCHAR(50)",
        "BED_ID VARCHAR(50)",
        "GENDER VARCHAR(50)",
        "STUDENT_PHONE_NUM VARCHAR(50)",
        "MAJOR VARCHAR(50)",
        "SCHOOL VARCHAR(50)",
        "STUDENT_EMAIL_ADDRESS VARCHAR(50)",
        "PASSWORD INT",
        "FOREIGN KEY (ROOM_ID, BED_ID) REFERENCES bed(ROOM_ID, BED_ID)"
    ]
    db.create_table(DB_NAME, "student", ", ".join(student_query))

    repair_query = [
        "REQUEST_ID INT AUTO_INCREMENT PRIMARY KEY",
        "STUDENT_ID INT",
        "ROOM_ID VARCHAR(50)",
        "REPAIR_TYPE VARCHAR(50)",
    ]
    db.create_table(DB_NAME, "repair_request", ", ".join(repair_query))

    adjust_query = [
        "REQUEST_ID INT AUTO_INCREMENT PRIMARY KEY",
        "STUDENT_ID INT",
        "BUILDING_ID VARCHAR(50)",
        "FLOOR_ID INT",
        "TO_ROOM_ID VARCHAR(50)",
        "BED_ID VARCHAR(50)"
    ]
    db.create_table(DB_NAME, "adjust_request", ",".join(adjust_query))
    
    print(db.show_db_tables(DB_NAME))
    # db.close_connection()
