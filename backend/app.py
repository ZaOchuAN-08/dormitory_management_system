from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from werkzeug.security import check_password_hash 
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)  # 启用跨域请求支持

app.config['MYSQL_HOST'] = '127.0.0.1' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'csc3170_project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# 登录路由 /login 
@app.route('/login', methods=['POST'])
def login():
    """
    通过 ID 和密码进行登录认证
    """
    try:
        data = request.json
        user_id = data.get('id')
        password = data.get('password')
        cur = mysql.connection.cursor()

        if not user_id or len(user_id)!=9 or not password:
            return jsonify({'success': False, 'message': 'Please enter valid ID and password.'}), 400

        user = None
        role = None

        sql_warden = "SELECT WARDEN_ID, WARDEN_NAME, WARDEN_PASSWORD_HASHED FROM warden WHERE WARDEN_ID = %s"
        cur.execute(sql_warden, (user_id,))
        user_data = cur.fetchone()
            
        if user_data:
            db_hash = user_data.get('WARDEN_PASSWORD_HASHED')
            if db_hash and check_password_hash(db_hash, password):
                user, role = user_data, 'warden'

        if not user:
            sql_tutor = "SELECT TUTOR_ID, TUTOR_NAME, TUTOR_PASSWORD_HASHED FROM tutor WHERE TUTOR_ID = %s"
            cur.execute(sql_tutor, (user_id,))
            user_data = cur.fetchone()
            
            if user_data:
                db_hash = user_data.get('TUTOR_PASSWORD_HASHED')
                if db_hash and check_password_hash(db_hash, password):
                    user, role = user_data, 'tutor'

        if not user:
            sql_student = "SELECT STUDENT_ID, STUDENT_NAME, PASSWORD_HASHED FROM student WHERE STUDENT_ID = %s"
            cur.execute(sql_student, (user_id,))
            user_data = cur.fetchone()
            
            if user_data:
                db_hash = user_data.get('PASSWORD_HASHED')
                if db_hash and check_password_hash(db_hash, password):
                    user, role = user_data, 'student'

        if user:
            user.pop('PASSWORD_HASHED', None)
            user.pop('TUTOR_PASSWORD_HASHED', None)
            user.pop('WARDEN_PASSWORD_HASHED', None)
            return jsonify({'success': True, 'role': role, 'user_info': user}), 200
        else:
            return jsonify({'success': False, 'message': 'Incorrect user ID or password.'}), 401

    except Exception as e:
        app.logger.error(f"Error occurs during logging: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
    finally:
        if 'cur' in locals() and cur:
            cur.close()

# 显示学生信息及修改手机号 
@app.route('/student/info', methods=['GET'])
def get_student_info():
    """
    根据 URL 参数中的 STUDENT_ID 获取学生的详细信息。
    """
    student_id = request.args.get('id')
    cur = mysql.connection.cursor()
    
    if not student_id:
        return jsonify({'success': False, 'message': 'Missing student ID parameter'}), 400

    try:
        cur = mysql.connection.cursor()
        sql = "SELECT STUDENT_ID, STUDENT_NAME, GENDER, SCHOOL, MAJOR, ROOM_ID, STUDENT_PHONE_NUM, STUDENT_EMAIL_ADDRESS FROM student WHERE STUDENT_ID = %s"
        cur.execute(sql, (student_id,))
        info = cur.fetchone()

        if info:
            app.logger.info(f"Fetch student {student_id} information successfully.")
            # print(info)
            return jsonify({'success': True, 'info': info}), 200
        else:
            return jsonify({'success': False, 'message': 'Unable to find student info.'}), 404

    except Exception as e:
        app.logger.error(f"Error occurs loading student info: {e}")
        return jsonify({'success': False, 'message': 'Server query error'}), 500
    finally:
        if cur:
            cur.close()
@app.route('/student/update_phone', methods=['POST'])
def update_student_phone():
    """
    修改学生的手机号码。
    """
    data = request.json
    student_id = data.get('id')
    new_phone = data.get('new_phone')
    cur = None

    if not student_id or not new_phone:
        return jsonify({'success': False, 'message': 'Missing ID or new phone number.'}), 400
    
    if len(new_phone) != 11 or not new_phone.startswith('1'):
        return jsonify({'success': False, 'message': 'Invalid phone number format.'}), 400

    try:
        cur = mysql.connection.cursor()
        
        sql = "UPDATE student SET STUDENT_PHONE_NUM = %s WHERE STUDENT_ID = %s"
        cur.execute(sql, (new_phone, student_id))
        
        if cur.rowcount > 0:
            mysql.connection.commit()
            app.logger.info(f"Student {student_id} phone number updated successfully.")
            return jsonify({'success': True, 'message': 'Phone number updated successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Phone number unchanged.'}), 404

    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"Error occurred while updating student's phone number: {e}")
        return jsonify({'success': False, 'message': 'Server update error.'}), 500
    finally:
        if cur:
            cur.close()

# 显示导师信息及修改手机号 
@app.route('/tutor/info', methods=['GET'])
def get_tutor_info():
    """
    根据 URL 参数中的 TUTOR_ID 获取导师的详细信息。
    """
    tutor_id = request.args.get('id')
    cur = mysql.connection.cursor()
    
    if not tutor_id:
        return jsonify({'success': False, 'message': 'Missing tutor ID parameter'}), 400

    try:
        cur = mysql.connection.cursor()
        sql = "SELECT TUTOR_ID, TUTOR_NAME, TUTOR_GENDER, TUTOR_EMAIL_ADDRESS, TUTOR_PHONE_NUM FROM tutor WHERE TUTOR_ID = %s"
        cur.execute(sql, (tutor_id,))
        info = cur.fetchone()

        if info:
            app.logger.info(f"Fetch tutor {tutor_id} information successfully.")
            # print(info)
            return jsonify({'success': True, 'info': info}), 200
        else:
            return jsonify({'success': False, 'message': 'Unable to find tutor info.'}), 404
    except Exception as e:
        app.logger.error(f"Error occurs loading tutor info: {e}")
        return jsonify({'success': False, 'message': 'Server query error'}), 500
    finally:
        if cur:
            cur.close()
@app.route('/tutor/update_phone', methods=['POST'])
def update_tutor_phone():
    """
    修改导师的手机号码。
    """
    data = request.json
    tutor_id = data.get('id')
    new_phone = data.get('new_phone')
    cur = None

    if not tutor_id or not new_phone:
        return jsonify({'success': False, 'message': 'Missing ID or new phone number.'}), 400
    
    if len(new_phone) != 11 or not new_phone.startswith('1'):
        return jsonify({'success': False, 'message': 'Invalid phone number format.'}), 400

    try:
        cur = mysql.connection.cursor()
        
        sql = "UPDATE tutor SET TUTOR_PHONE_NUM = %s WHERE TUTOR_ID = %s"
        cur.execute(sql, (new_phone, tutor_id))
        
        if cur.rowcount > 0:
            mysql.connection.commit()
            app.logger.info(f"Tutor {tutor_id} phone number updated successfully.")
            return jsonify({'success': True, 'message': 'Phone number updated successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Phone number unchanged.'}), 404

    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"Error occurred while updating tutor's phone number: {e}")
        return jsonify({'success': False, 'message': 'Server update error.'}), 500
    finally:
        if cur:
            cur.close()

# 显示舍监信息及修改手机号 
@app.route('/warden/info', methods=['GET'])
def get_warden_info():
    """
    根据 URL 参数中的 WARDEN_ID 获取舍监的详细信息。
    """
    warden_id = request.args.get('id')
    cur = mysql.connection.cursor()
    
    if not warden_id:
        return jsonify({'success': False, 'message': 'Missing warden ID parameter'}), 400

    try:
        cur = mysql.connection.cursor()
        sql = "SELECT WARDEN_ID, WARDEN_NAME, WARDEN_GENDER, WARDEN_EMAIL_ADDRESS, WARDEN_PHONE_NUM FROM warden WHERE WARDEN_ID = %s"
        cur.execute(sql, (warden_id,))
        info = cur.fetchone()

        if info:
            app.logger.info(f"Fetch warden {warden_id} information successfully.")
            # print(info)
            return jsonify({'success': True, 'info': info}), 200
        else:
            return jsonify({'success': False, 'message': 'Unable to find warden info.'}), 404

    except Exception as e:
        app.logger.error(f"Error occurs loading warden info: {e}")
        return jsonify({'success': False, 'message': 'Server query error'}), 500
    finally:
        if cur:
            cur.close()
@app.route('/warden/update_phone', methods=['POST'])
def update_warden_phone():
    """
    修改舍监的手机号码。
    """
    data = request.json
    warden_id = data.get('id')
    new_phone = data.get('new_phone')
    cur = None

    if not warden_id or not new_phone:
        return jsonify({'success': False, 'message': 'Missing ID or new phone number.'}), 400
    
    if len(new_phone) != 11 or not new_phone.startswith('1'):
        return jsonify({'success': False, 'message': 'Invalid phone number format.'}), 400

    try:
        cur = mysql.connection.cursor()
        
        sql = "UPDATE warden SET WARDEN_PHONE_NUM = %s WHERE WARDEN_ID = %s"
        cur.execute(sql, (new_phone, warden_id))
        
        if cur.rowcount > 0:
            mysql.connection.commit()
            app.logger.info(f"Warden {warden_id} phone number updated successfully.")
            return jsonify({'success': True, 'message': 'Phone number updated successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Phone number unchanged.'}), 404

    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"Error occurred while updating warden's phone number: {e}")
        return jsonify({'success': False, 'message': 'Server update error.'}), 500
    finally:
        if cur:
            cur.close()

@app.route('/student/dorm_info', methods=['GET'])
def get_student_dorm_info():
    """
    查询学生的宿舍信息（楼栋、房间、床位）和电费余额。
    假设 ROOM 表中有 ELECTRICITY_BALANCE 字段。
    """
    try:
        student_id = request.args.get('id')
        if not student_id:
            return jsonify({'success': False, 'message': 'Missing student ID'}), 400
        cur = mysql.connection.cursor()
        
        sql = """SELECT s.BUILDING_ID, s.FLOOR_ID, s.ROOM_ID, s.BED_ID, r.ELECTRICITY_BALANCE, r.REQ_TBPROCESSED_NUM, r.REQ_HBPROCESSED_NUM
                 FROM student s JOIN room r ON s.ROOM_ID = r.ROOM_ID
                 WHERE s.STUDENT_ID = %s"""
        cur.execute(sql, (student_id,))
        dorm_info = cur.fetchone()

        if dorm_info:
            app.logger.info(f"Fetch student {student_id} dorm and electricity information successfully.")
            #print(dorm_info)
            return jsonify({'success': True, 'dorm_info': dorm_info}), 200
        else:
            return jsonify({'success': False, 'message': 'Unable to find dorm info.'}), 404

    except Exception as e:
        app.logger.error(f"Error fetching dorm info: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error, Unable to load dorm info.'}), 500
    finally:
        if cur:
            cur.close()

@app.route('/student/recharge_electricity', methods=['POST'])
def recharge_electricity():
    """
    处理学生的电费充值请求。
    将充值金额加到对应的 ROOM 的 ELECTRICITY_BALANCE 字段。
    """
    try:
        data = request.get_json()
        student_id = data.get('id')
        amount = data.get('amount')

        if not student_id or not amount or not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid recharge request.'}), 400
        cur = mysql.connection.cursor()
        
        sql_select = "SELECT ROOM_ID FROM student WHERE STUDENT_ID = %s"
        cur.execute(sql_select, (student_id,))
        result = cur.fetchone()
        
        if not result or not result['ROOM_ID']:
            cur.close()
            return jsonify({'success': False, 'message': 'The students have not been assigned dormitories so they cannot recharge.'}), 404
        
        room_id = result['ROOM_ID']
        sql_update = """UPDATE room SET ELECTRICITY_BALANCE = ELECTRICITY_BALANCE + %s 
                        WHERE ROOM_ID = %s"""
        cur.execute(sql_update, (amount, room_id))
        mysql.connection.commit() # 提交事务

        # cur.execute("SELECT ELECTRICITY_BALANCE FROM room WHERE ROOM_ID = %s", (room_id,))
        # new_balance = cur.fetchone()['ELECTRICITY_BALANCE']
   
        return jsonify({'success': True, 'message': f'Room {room_id} recharge {amount:.2f} Yuan successfully.', 'new_balance': 'Need to recheck'}), 200

    except Exception as e:
        app.logger.error(f"Error processing recharge: {str(e)}")
        mysql.connection.rollback() # 失败时回滚
        return jsonify({'success': False, 'message': 'Server error, fail to recharge.'}), 500
    finally:
        if cur: cur.close()

@app.route('/tutor/students', methods=['GET'])
def get_tutor_students():
    """
    查询导师所管理楼层中的所有学生信息。
    """
    try:
        tutor_id = request.args.get('id')
        if not tutor_id:
            return jsonify({'success': False, 'message': 'Missing warden ID'}), 400

        cur = mysql.connection.cursor()
        
        sql_floor = "SELECT BUILDING_ID, FLOOR_ID FROM floor WHERE TUTOR_ID = %s"
        cur.execute(sql_floor, (tutor_id,))
        floor_info = cur.fetchone()
        
        if floor_info:
            app.logger.info(f"Successfully obtained the floor information managed by tutor {tutor_id}.")
        else:
            return jsonify({'success': False, 'message': 'No information on managed buildings was found.'}), 404
                
        sql_students = """SELECT S.STUDENT_ID, S.STUDENT_NAME, S.GENDER, S.SCHOOL, S.MAJOR, S.STUDENT_PHONE_NUM, S.ROOM_ID, S.BED_ID
                          FROM student S
                          WHERE S.BUILDING_ID = %s AND S.FLOOR_ID = %s
                          ORDER BY S.ROOM_ID, S.BED_ID"""
        cur.execute(sql_students, (floor_info['BUILDING_ID'], floor_info['FLOOR_ID']))
        students = cur.fetchall()

        floor_id = floor_info['BUILDING_ID'] + str(floor_info['FLOOR_ID'])
        
        if students:
            app.logger.info(f"Successfully obtained the student information managed by tutor {tutor_id} ")
            return jsonify({'success': True, 'students': students, 'floor_id': floor_id}), 200
        else:
            return jsonify({'success': True, 'students': students, 'floor_id': floor_id}), 200

    except Exception as e:
        app.logger.error(f"Error fetching warden tutors: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error, unable to load student information.'}), 500
    finally:
        if cur: cur.close()

@app.route('/warden/tutors', methods=['GET'])
def get_warden_tutors():
    """
    查询舍监所管理楼栋下的所有导师信息，并统计待处理申请数。
    """
    try:
        warden_id = request.args.get('id')
        if not warden_id:
            return jsonify({'success': False, 'message': 'Missing warden ID'}), 400

        cur = mysql.connection.cursor()
        
        sql_building = "SELECT BUILDING_ID FROM building WHERE WARDEN_ID = %s"
        cur.execute(sql_building, (warden_id,))
        building_info = cur.fetchone()
        
        if building_info:
            app.logger.info(f"Successfully obtained the building information managed by warden {warden_id}.")
        else:
            return jsonify({'success': False, 'message': 'No information on managed buildings was found.'}), 404
        
        building_id = building_info['BUILDING_ID']
        
        sql_tutors = """SELECT  T.TUTOR_ID, T.TUTOR_NAME, T.TUTOR_GENDER, T.TUTOR_PHONE_NUM, T.TUTOR_TBPROCESSED_REQ_NUM, F.FLOOR_ID
                        FROM tutor T
                        JOIN floor F ON T.TUTOR_ID = F.TUTOR_ID
                        WHERE F.BUILDING_ID = %s
                        GROUP BY T.TUTOR_ID, T.TUTOR_NAME, T.TUTOR_PHONE_NUM, T.TUTOR_GENDER, T.TUTOR_TBPROCESSED_REQ_NUM, F.FLOOR_ID
                        ORDER BY F.FLOOR_ID"""
        cur.execute(sql_tutors, (building_id,))
        tutors = cur.fetchall()
        if tutors:
            app.logger.info(f"Successfully obtained the tutor information managed by warden {warden_id}.")
            return jsonify({'success': True, 'tutors': tutors, 'building_id': building_id}), 200
        else:
            return jsonify({'success': True, 'tutors': tutors, 'building_id': building_id}), 200

    except Exception as e:
        app.logger.error(f"Error fetching warden tutors: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error, unable to load tutor information.'}), 500
    finally:
        if cur: cur.close()

@app.route('/warden/students', methods=['GET'])
def get_warden_students():
    """
    查询舍监所管理楼栋下的所有学生信息。
    """
    try:
        warden_id = request.args.get('id')
        if not warden_id:
            return jsonify({'success': False, 'message': 'Missing warden ID'}), 400

        cur = mysql.connection.cursor()
        
        sql_building = "SELECT BUILDING_ID FROM building WHERE WARDEN_ID = %s"
        cur.execute(sql_building, (warden_id,))
        building_info = cur.fetchone()
        
        if not building_info:
            return jsonify({'success': False, 'message': 'No information on managed buildings was found.'}), 404
        
        building_id = building_info['BUILDING_ID']
        
        sql_students = """SELECT S.STUDENT_ID, S.STUDENT_NAME, S.GENDER, S.SCHOOL, S.MAJOR, S.STUDENT_PHONE_NUM, S.ROOM_ID, S.BED_ID
                          FROM student S
                          WHERE S.BUILDING_ID = %s
                          ORDER BY S.ROOM_ID, S.BED_ID"""
        cur.execute(sql_students, (building_id,))
        students = cur.fetchall()

        return jsonify({'success': True, 'students': students, 'building_id': building_id}), 200

    except Exception as e:
        app.logger.error(f"Error fetching warden students: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error, unable to load student information.'}), 500
    finally:
        if cur: cur.close()

@app.route('/warden/dorm_status', methods=['GET'])
def get_warden_dorm_status():
    """
    查询舍监所管理楼栋下的所有宿舍状态：电费余额、空闲床位数等。
    """
    try:
        warden_id = request.args.get('id')
        if not warden_id:
            return jsonify({'success': False, 'message': 'Missing warden ID'}), 400

        cur = mysql.connection.cursor()
        
        sql_building = "SELECT BUILDING_ID FROM building WHERE WARDEN_ID = %s"
        cur.execute(sql_building, (warden_id,))
        building_info = cur.fetchone()
        
        if not building_info:
            return jsonify({'success': False, 'message': 'No information on managed buildings was found.'}), 404
        
        building_id = building_info['BUILDING_ID']
        
        sql_rooms = """SELECT R.ROOM_ID, R.FLOOR_ID,R.ELECTRICITY_BALANCE, 
                       (SELECT COUNT(*) FROM bed B WHERE B.ROOM_ID = R.ROOM_ID) AS MAX_CAPACITY,
                       COUNT(S.STUDENT_ID) AS GUESTS
                       FROM room R
                       LEFT JOIN student S ON R.ROOM_ID = S.ROOM_ID
                       WHERE R.BUILDING_ID = %s
                       GROUP BY R.ROOM_ID, R.FLOOR_ID, R.ELECTRICITY_BALANCE
                       ORDER BY R.ROOM_ID"""
        cur.execute(sql_rooms, (building_id,))
        room_status = cur.fetchall()
        
        sql_bed_summary = """SELECT (SELECT COUNT(*) FROM bed B WHERE B.ROOM_ID IN (SELECT ROOM_ID FROM room WHERE BUILDING_ID = %s)) AS Total_Beds,
                                    (SELECT COUNT(*) FROM student S WHERE S.BUILDING_ID = %s) AS Occupied_Beds"""
        cur.execute(sql_bed_summary, (building_id, building_id))
        bed_summary = cur.fetchone()

        total_beds = bed_summary['Total_Beds'] if bed_summary and bed_summary['Total_Beds'] else 0
        occupied_beds = bed_summary['Occupied_Beds'] if bed_summary and bed_summary['Occupied_Beds'] else 0
        available_beds = total_beds - occupied_beds

        return jsonify({
            'success': True, 
            'building_id': building_id,
            'summary': {
                'Total_Beds': total_beds,
                'Occupied_Beds': occupied_beds,
                'Available_Beds': available_beds
            },
            'room_status': room_status
        }), 200

    except Exception as e:
        app.logger.error(f"Error fetching dorm status: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error, unable to load dorm information.'}), 500
    finally:
        if cur: cur.close()

@app.route('/student/rooms', methods=['GET'])
def get_student_rooms():
    student_id = request.args.get('id')
    if not student_id:
        return jsonify({'success': False, 'message': 'Missing student ID'}), 400
    cur = mysql.connection.cursor()
    try:
        sql = "SELECT ROOM_ID FROM student WHERE STUDENT_ID = %s"
        cur.execute(sql, (student_id,))
        room = cur.fetchone()
        if room:
            return jsonify({'success': True, 'rooms': [room]})
        else:
            return jsonify({'success': False, 'rooms': [], 'message': 'No dorm info found'}), 404
    finally:
        cur.close()

@app.route('/student/buildings', methods=['GET'])
def get_student_buildings():
    student_id = request.args.get('id')
    if not student_id:
        return jsonify({'success': False, 'message': 'Building missing'}), 400
    cur = mysql.connection.cursor()
    try:
        sql = "SELECT BUILDING_ID FROM student WHERE STUDENT_ID = %s"
        cur.execute(sql, (student_id,))
        building = cur.fetchone()
        if building:
            return jsonify({'success': True, 'buildings': [building]})
        else:
            return jsonify({'success': False, 'buildings': [], 'message': 'No building info found'}), 404
    finally:
        cur.close()

@app.route('/student/adjust/rooms', methods=['GET'])
def get_adjust_rooms():
    building_id = request.args.get('building_id')
    floor_id = request.args.get('floor_id')
    if not building_id or not floor_id:
        return jsonify({'success': False, 'message': 'Missing building or floor info'}), 400

    cur = mysql.connection.cursor()
    try:
        sql = """SELECT ROOM_ID
                 FROM room
                 WHERE BUILDING_ID=%s AND FLOOR_ID=%s AND IS_EMPTY=1"""
        cur.execute(sql, (building_id, floor_id))
        rooms = cur.fetchall()
        if rooms:
            return jsonify({'success': True, 'rooms': rooms})
        else:
            return jsonify({'success': False, 'rooms': [], 'message': 'No room available'})
    finally:
        if cur:
            cur.close()

@app.route('/student/adjust/beds', methods=['GET'])
def get_adjust_beds():
    room_id = request.args.get('room_id')
    if not room_id:
        return jsonify({'success': False, 'message': 'Missing room info'}), 400

    cur = mysql.connection.cursor()
    try:
        sql = """SELECT BED_ID
                 FROM bed
                 WHERE ROOM_ID=%s AND AVAILABILITY=1"""
        cur.execute(sql, (room_id,))
        beds = cur.fetchall()
        if beds:
            return jsonify({'success': True, 'beds': beds})
        else:
            return jsonify({'success': False, 'beds': [], 'message': 'No available beds'})
    finally:
        if cur:
            cur.close()

# 学生提交维修申请
@app.route('/submit_repair_request', methods=['POST'])
def submit_repair_request():
    data = request.get_json()
    student_id = data.get('id')
    room_id = data.get('room_id')
    repair_type = data.get('repair_type')
    if not student_id or not room_id or not repair_type:
        return jsonify({'success': False, 'message': 'Missing information'}), 400
    cur = mysql.connection.cursor()

    try:
        # 找到该宿舍对应的导师
        sql_tutor = """SELECT t.TUTOR_ID, f.BUILDING_ID, f.FLOOR_ID
                       FROM tutor t
                       JOIN floor f ON t.TUTOR_ID = f.TUTOR_ID
                       JOIN room r ON r.FLOOR_ID = f.FLOOR_ID AND r.BUILDING_ID = f.BUILDING_ID
                       WHERE r.ROOM_ID = %s;"""
        cur.execute(sql_tutor, (room_id,))
        tutor_info = cur.fetchone()
        if not tutor_info:
            return jsonify({'success': False, 'message': 'No tutor found responsible for this floor.'}), 404
        
        tutor_id = tutor_info['TUTOR_ID']

        # 插入 repair_request
        insert_sql = """INSERT INTO repair_request (STUDENT_ID, ROOM_ID, REPAIR_TYPE)
                        VALUES (%s, %s, %s)"""
        cur.execute(insert_sql, (student_id, room_id, repair_type))
        
        # 更新导师的待处理申请数 +1
        update_query1 = """UPDATE tutor SET TUTOR_TBPROCESSED_REQ_NUM = TUTOR_TBPROCESSED_REQ_NUM + 1
                           WHERE TUTOR_ID = %s"""
        cur.execute(update_query1, (tutor_id,))
        
        # 更新宿舍 room 的待处理申请数 +1
        update_query2 = """UPDATE room SET REQ_TBPROCESSED_NUM = REQ_TBPROCESSED_NUM + 1
                           WHERE ROOM_ID = %s"""
        cur.execute(update_query2, (room_id,))
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Repair request submitted! The tutor will handle it as soon as possible.'})
    except Exception as e:
        app.logger.error(f"Error: 处理申请出现错误")
        return jsonify({'success': False, 'message': 'Server error, unable to process.'}), 500
    finally:
        if cur:
            cur.close()

# 导师处理维修申请
@app.route('/tutor/pending_requests', methods=['GET'])
def get_tutor_pending_requests():
    tutor_id = request.args.get('id')
    if not tutor_id:
        return jsonify({'success': False, 'message': 'Missing tutor ID'}), 400

    cur = mysql.connection.cursor()
    try:
        select_sql1 = """SELECT TUTOR_HBPROCESSED_REQ_NUM, TUTOR_TBPROCESSED_REQ_NUM FROM tutor WHERE TUTOR_ID = %s"""
        cur.execute(select_sql1, (tutor_id,))
        requests_num = cur.fetchone()

        select_sql2 = """SELECT rr.REQUEST_ID, S.STUDENT_ID, S.STUDENT_NAME, rr.ROOM_ID, rr.REPAIR_TYPE
                         FROM repair_request rr
                         JOIN student S ON rr.STUDENT_ID = S.STUDENT_ID
                         JOIN room R ON rr.ROOM_ID = R.ROOM_ID
                         JOIN floor F ON R.FLOOR_ID = F.FLOOR_ID
                         WHERE F.TUTOR_ID = %s
                         ORDER BY rr.REQUEST_ID"""
        cur.execute(select_sql2, (tutor_id,))
        students = cur.fetchall()
        return jsonify({'success': True, 'requests': requests_num, 'students': students})
    except Exception as e:
        app.logger.error(f"Error: 出现错误")
        return jsonify({'success': False, 'message': 'Server error, unable to process.'}), 500
    finally:
        cur.close()

@app.route('/tutor/process_repair_request', methods=['POST'])
def process_repair_request():
    data = request.get_json()
    request_id = data['request_id']
    room_id = data['room_id']
    action = data['action']
    tutor_id = request.args.get('id')
    if not tutor_id or not action or not request_id:
        return jsonify({'success': False, 'message': 'Missing information'}), 400
    cur = mysql.connection.cursor()
    
    try:
        # 导师待处理申请数 -1, 已处理数 +1
        update_query1 = """UPDATE tutor SET TUTOR_TBPROCESSED_REQ_NUM = GREATEST(TUTOR_TBPROCESSED_REQ_NUM-1, 0),
                           TUTOR_HBPROCESSED_REQ_NUM = TUTOR_HBPROCESSED_REQ_NUM + 1
                           WHERE TUTOR_ID = %s"""
        cur.execute(update_query1, (tutor_id,))

        # 房间待处理数 -1，已处理数 +1
        update_query2 = """UPDATE room SET REQ_TBPROCESSED_NUM = GREATEST(REQ_TBPROCESSED_NUM-1, 0),
                           REQ_HBPROCESSED_NUM = REQ_HBPROCESSED_NUM + 1
                           WHERE ROOM_ID = %s"""
        cur.execute(update_query2, (room_id,))

        # 删除该请求（或标记为已处理）
        cur.execute("DELETE FROM repair_request WHERE REQUEST_ID=%s", (request_id,))

        mysql.connection.commit()
        return jsonify({'success': True, 'message': f'{action} this repair request.'})
    except Exception as e:
        app.logger.error(f"Error: Error occurred when processing")
        return jsonify({'success': False, 'message': 'Server error, unable to process'}), 500
    finally:
        if cur:
            cur.close()

# 学生提交换宿申请
@app.route('/student/submit_adjust_request', methods=['POST'])
def submit_adjust_request():
    data = request.get_json()
    student_id = data.get('student_id')
    building_id = data.get('building_id')
    floor_id = data.get('floor_id')
    room_id = data.get('room_id')
    bed_id = data.get('bed_id')

    if not all([student_id, building_id, floor_id, room_id, bed_id]):
        return jsonify({'success': False, 'message': 'Missing information'}), 400

    cur = mysql.connection.cursor()
    try:
        # 获取原本房号
        cur.execute("SELECT ROOM_ID, BUILDING_ID, FLOOR_ID FROM student WHERE STUDENT_ID=%s", (student_id,))
        orig_info = cur.fetchone()
        # 获取舍监
        sql_tutor = """SELECT b.WARDEN_ID FROM building b
                       JOIN student s ON s.BUILDING_ID = b.BUILDING_ID
                       WHERE s.BUILDING_ID=%s"""
        cur.execute(sql_tutor, (orig_info['BUILDING_ID']))
        warden_info = cur.fetchone()
        if not warden_info:
            return jsonify({'success': False, 'message': 'Unable to find warden'}), 404
        warden_id = warden_info['WARDEN_ID']
        # 插入申请
        insert_sql = """INSERT INTO adjust_request (STUDENT_ID, BUILDING_ID, FLOOR_ID, TO_ROOM_ID, BED_ID)
                        VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(insert_sql, (student_id, building_id, floor_id, room_id, bed_id))
        # 更新舍监的待处理 +1
        update_warden = """UPDATE warden SET WARDEN_TBPROCESSED_REQ_NUM = WARDEN_TBPROCESSED_REQ_NUM + 1
                           WHERE WARDEN_ID=%s"""
        cur.execute(update_warden, (warden_id,))
        # 更新宿舍的待处理 +1
        update_room = """UPDATE room SET REQ_TBPROCESSED_NUM = REQ_TBPROCESSED_NUM + 1
                         WHERE ROOM_ID = %s"""
        cur.execute(update_room, (orig_info['ROOM_ID'],))
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Dormitory adjustment request submitted, awaiting warden processing.'})
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500
    finally:
        cur.close()

# 舍监处理换宿申请
@app.route('/warden/pending_adjust_requests', methods=['GET'])
def warden_pending_adjust_requests():
    warden_id = request.args.get('id')
    if not warden_id:
        return jsonify({'success': False, 'message': 'Missing warden ID'}), 400

    cur = mysql.connection.cursor()
    try:
        select_sql1 = """SELECT WARDEN_HBPROCESSED_REQ_NUM, WARDEN_TBPROCESSED_REQ_NUM FROM warden WHERE WARDEN_ID = %s"""
        cur.execute(select_sql1, (warden_id,))
        requests_num = cur.fetchone()

        select_sql3 = """SELECT ar.REQUEST_ID, s.STUDENT_ID, s.STUDENT_NAME, s.ROOM_ID, ar.BUILDING_ID, ar.FLOOR_ID, ar.TO_ROOM_ID, ar.BED_ID
                         FROM adjust_request ar
                         JOIN student s ON ar.STUDENT_ID = s.STUDENT_ID
                         JOIN building b ON ar.BUILDING_ID = b.BUILDING_ID
                         WHERE b.WARDEN_ID=%s"""
        cur.execute(select_sql3, (warden_id,))
        requests = cur.fetchall()
        return jsonify({'success': True, 'requests': requests, 'requests_num': requests_num})
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500
    finally:
        cur.close()

@app.route('/warden/process_adjust_request', methods=['POST'])
def process_adjust_request():
    data = request.get_json()
    request_id = data.get('request_id')
    action = data.get('action')  # '通过' 或 '拒绝'
    warden_id = request.args.get('id')
    if not all([request_id, action, warden_id]):
        return jsonify({'success': False, 'message': 'Missing information'}), 400

    cur = mysql.connection.cursor()
    try:
        # 获取申请信息
        cur.execute("SELECT STUDENT_ID, BUILDING_ID, FLOOR_ID, TO_ROOM_ID, BED_ID FROM adjust_request WHERE REQUEST_ID=%s", (request_id,))
        req = cur.fetchone()
        if not req:
            return jsonify({'success': False, 'message': 'No requests found.'}), 404

        # 获取原本房号
        cur.execute("SELECT ROOM_ID, BED_ID FROM student WHERE STUDENT_ID=%s", (req['STUDENT_ID'],))
        orig_info = cur.fetchone()
        orig_room_id = orig_info['ROOM_ID'] if orig_info else None
        orig_bed_id = orig_info['BED_ID'] if orig_info else None

        # 处理通过：更新学生宿舍信息
        if action == 'Approve':
            # 设置床位不可用
            update_bed = """UPDATE bed SET AVAILABILITY = 0 WHERE ROOM_ID=%s AND BED_ID=%s"""
            cur.execute(update_bed, (orig_room_id, orig_bed_id))
            update_student = """UPDATE student SET BUILDING_ID=%s, FLOOR_ID=%s, ROOM_ID=%s, BED_ID=%s
                                WHERE STUDENT_ID=%s"""
            cur.execute(update_student, (req['BUILDING_ID'], req['FLOOR_ID'], req['TO_ROOM_ID'], req['BED_ID'], req['STUDENT_ID']))
        
        # 删除申请
        cur.execute("DELETE FROM adjust_request WHERE REQUEST_ID=%s", (request_id,))

        # 导师待处理申请数 -1
        cur.execute("""UPDATE warden SET WARDEN_TBPROCESSED_REQ_NUM = GREATEST(WARDEN_TBPROCESSED_REQ_NUM-1,0),
                       WARDEN_HBPROCESSED_REQ_NUM = WARDEN_HBPROCESSED_REQ_NUM + 1
                       WHERE WARDEN_ID=%s""", (warden_id,))
        cur.execute("""UPDATE room SET REQ_TBPROCESSED_NUM = GREATEST(REQ_TBPROCESSED_NUM-1, 0),
                       REQ_HBPROCESSED_NUM = REQ_HBPROCESSED_NUM + 1
                       WHERE ROOM_ID = %s""", (orig_room_id,))

        mysql.connection.commit()
        return jsonify({'success': True, 'message': f'{action} this adjustment request.'})
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500
    finally:
        if cur: cur.close()

# --- 应用启动 ---
if __name__ == '__main__':
    # 打印明确的启动信息
    print("--------------------------------------------------")
    print(f"Flask App Loading...")
    print(f"Database: {app.config['MYSQL_DB']} @ {app.config['MYSQL_HOST']}")
    print(f"Visit frontend at: http://127.0.0.1:5000/")
    print("--------------------------------------------------")
    
    # 启动 Flask 应用，监听在 5000 端口
    app.run(debug=True, host='0.0.0.0', port=5000) 
