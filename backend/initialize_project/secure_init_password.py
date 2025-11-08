import pymysql
from mysql_class import MySQLdb
from werkzeug.security import generate_password_hash

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASS = '123456'
DB_NAME = 'csc3170_project'

db = MySQLdb(
    host = DB_HOST,
    user = DB_USER,
    password = DB_PASS,
    database = DB_NAME
)
cursor = db.cursor

db.add_column('student', 'PASSWORD_HASHED', 'VARCHAR(225)')
db.add_column('tutor', 'TUTOR_PASSWORD_HASHED', 'VARCHAR(225)')
db.add_column('warden', 'WARDEN_PASSWORD_HASHED', 'VARCHAR(225)')

def process_users(table_name, id_col, password_col, hash_col):
    """从表中读取所有用户ID和旧密码生成哈希并更新到哈希列。"""
    # 查询用户 ID 和旧密码
    users = db.select_data(table_name, f'{id_col}, {password_col}')
    if not users:
        print(f"No data founded.")
        return 0

    success_count = 0
            
    for user in users:
        user_id = user[0]
        plain_password = str(user[1])
        try:
            # 进行哈希和加盐
            hashed_password = generate_password_hash(plain_password)
                    
            update_query = f"UPDATE {table_name} SET {hash_col} = %s WHERE {id_col} = %s"
            cursor.execute(update_query, (hashed_password, user_id))
            success_count += cursor.rowcount
        except Exception as e:
            print(f"User {user_id} raises error: {e}")
                    
    print(f"{table_name} proccessed successfully. {success_count} records updated.")
    return success_count

def initialize_secure_passwords():
    """连接数据库并为所有用户的原有密码生成安全哈希"""
    try:
        process_users(
            table_name='student', 
            id_col='STUDENT_ID', 
            password_col='PASSWORD',
            hash_col='PASSWORD_HASHED'
        )

        process_users(
            table_name='tutor', 
            id_col='TUTOR_ID', 
            password_col='TUTOR_PASSWORD',
            hash_col='TUTOR_PASSWORD_HASHED'
        )

        process_users(
            table_name='warden', 
            id_col='WARDEN_ID', 
            password_col='WARDEN_PASSWORD',
            hash_col='WARDEN_PASSWORD_HASHED'
        )

        db.connection.commit()
        print(f"All passwords updated successfully.")
        # print("尝试加盐密码：", db.select_data('student', 'PASSWORD_HASHED', 'STUDENT_ID=112874695'))

    except (pymysql.MySQLError, Exception) as e:
        print(f"Error occurs: {e}")
        if db:
            db.connection.rollback()
    finally:
        if db:
            db.close_connection()

if __name__ == "__main__":
    initialize_secure_passwords()
