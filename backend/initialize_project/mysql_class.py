import pymysql

'''实现封装和动态控制管理'''
class MySQLdb:

    def __init__(self, host, user, password, database):
        '''初始化数据库连接'''
        self.connection = pymysql.connect(
            host = host,
            user = user,
            password = password,
            database = database,
            autocommit = False  # 关闭自动提交
        )
        self.cursor = self.connection.cursor()
    
    def close_connection(self): 
        '''关闭数据库连接'''
        self.cursor.close()
        self.connection.close()

    def delete_database(self, db_name):
        '''删除数据库'''
        try:
            delete_query = f"DROP DATABASE IF EXISTS {db_name}"
            self.cursor.execute(delete_query)
            self.connection.commit()
            print(f"Database {db_name} deleted successfully.")
        except pymysql.MySQLError as e:
            print(f"Error deleting database: {e}")
            self.connection.rollback()

    def create_database(self, db_name):
        '''创建数据库'''
        try:
            create_query = f"CREATE DATABASE {db_name}"
            self.cursor.execute(create_query)
            self.connection.commit()
            print(f"Database {db_name} created successfully.")
        except pymysql.MySQLError as e:
            print(f"Error creating database: {e}")
            self.connection.rollback()

    def show_db_tables(self, db_name):
        '''选择数据库并返回其中的所有表格'''
        try:
            query = f"USE {db_name}"
            self.cursor.execute(query)
            self.cursor.execute("SHOW TABLES")
            databases = self.cursor.fetchall()
            if databases:
                return [db[0] for db in databases]
            else:
                print(f"No tables found in database {db_name}.")
                return []
        except pymysql.MySQLError as e:
            print(f"Error using database: {e}")
            return []
        
    def create_table(self, database, table_name, columns):
        '''创建表格'''
        use_query = f"USE {database}"
        self.cursor.execute(use_query)
        create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"   # Columns使用字符串格式
        try:
            self.cursor.execute(create_query)
            self.connection.commit()
            print(f"Table {table_name} created successfully.")
        except pymysql.MySQLError as e:
            print(f"Error creating table: {e}")
            self.connection.rollback()

    def delete_table(self, table_name):
        '''删除表格'''
        '''避免频繁调用数据库，仅在初始化时使用'''
        # use_query = f"USE {database}" # 避免频繁调用数据库
        # self.cursor.execute(use_query)
        delete_query = f"DROP TABLE IF EXISTS {table_name}"
        try:
            self.cursor.execute(delete_query)
            self.connection.commit()
            print(f"Table {table_name} deleted successfully.")
        except pymysql.MySQLError as e:
            print(f"Error deleting table: {e}")
            self.connection.rollback()
    
    def add_column(self, table_name, column_name, column_type):
        """向表格中添加列"""
        try:
            alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            self.cursor.execute(alter_query)
            self.connection.commit()
            print(f"Column {column_name} added to table {table_name} successfully.")
        except pymysql.Error as e:
            print(f"Error adding column: {e}")
            self.connection.rollback()

    def check_data_exists(self, table_name, column_names, values):
        """检查数据是否已存在"""
        try:
            where_conditions = ' AND '.join([f"{col} = %s" for col in column_names])
            select_query = f"SELECT {', '.join(column_names)} FROM {table_name} WHERE {where_conditions}"
            
            self.cursor.execute(select_query, values)
            result = self.cursor.fetchone()
            
            if result is not None:
                return result == tuple(values)
            return False
        
        except pymysql.Error as e:
            print(f"Error checking data existence: {e}")
            return False
    
    def insert_or_update_data(self, table_name, column_names, values):
        """插入或更新数据"""
        try:
            placeholders = ', '.join(['%s'] * len(column_names))
            column_list = ', '.join(column_names)
            update_clause = ', '.join([f"{col} = %s" for col in column_names])
            
            insert_query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"

            self.cursor.execute(insert_query, values * 2)   # values需要传递两次：一次用于VALUES，一次用于UPDATE
            return True
            
        except pymysql.Error as e:
            print(f"Error inserting/updating data: {e}")
            self.connection.rollback()
            return False
    
    def insert_into_table(self, data, column_indices, table_name, column_names):
        """将DataFrame数据插入到指定表格"""
        # 参数检查
        if len(column_indices) != len(column_names):
            print("Error: Number of column indices does not match number of column names.")
            return False
        if len(column_indices) < 1:
            print("Error: At least one column is required.")
            return False
        
        success_count = 0
        error_count = 0
        
        for index, row in data.iterrows():
            try:
                values = [row.iloc[column_index] for column_index in column_indices]
                if self.check_data_exists(table_name, column_names, values):
                    continue
                if self.insert_or_update_data(table_name, column_names, values):
                    if table_name == 'student':
                        room_index, bed_index = column_names.index('ROOM_ID'), column_names.index('BED_ID')
                        room_id, bed_id = values[room_index], values[bed_index]
                        update_query1 = "UPDATE bed SET AVAILABILITY = 0 WHERE ROOM_ID = %s AND BED_ID = %s"
                        update_params1 = (room_id, bed_id)
                        update_query2 = "UPDATE room SET REMAIN_BEDS = REMAIN_BEDS - 1 WHERE ROOM_ID = %s"
                        self.cursor.execute(update_query1, update_params1)
                        self.cursor.execute(update_query2, (room_id,))
                        
                        where_clause =  f"ROOM_ID='{room_id}'"
                        room_bed_data = self.select_data('room', 'REMAIN_BEDS', where_clause)
                        room_remain_beds = room_bed_data[0][0]
                        if room_remain_beds == 0:
                            update_query3 = "UPDATE room SET IS_EMPTY = 0 WHERE ROOM_ID = %s"
                            self.cursor.execute(update_query3, (room_id,))
                    else: pass
                    success_count += 1
                else:
                    error_count += 1 
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                error_count += 1
        self.connection.commit()    # 统一提交
        print(f"Table {table_name} insert operations completed. Success: {success_count}, Errors: {error_count}")
        return error_count == 0
    
    def select_data(self, table_name, columns='*', where_clause=None, params=None):
        """从表格中选择数据"""
        try:
            select_query = f"SELECT {columns} FROM {table_name}"
            if where_clause:
                select_query += f" WHERE {where_clause}"
            self.cursor.execute(select_query, params)   # 防止恶意注入
            results = self.cursor.fetchall()
            self.connection.commit()
            return results
        except pymysql.Error as e:
            print(f"Error selecting data: {e}")
            return None

    def clear_table(self, table_name):
        """清空表格数据"""
        try:
            clear_query = f"DELETE FROM {table_name}"
            self.cursor.execute(clear_query)
            self.connection.commit()
            print(f"Table {table_name} cleared successfully.")
        except pymysql.Error as e:
            print(f"Error clearing table: {e}")
            self.connection.rollback()  
    
    def delete_all_tb(self, database):
        """初始化：删除数据库中所有表格"""
        use_query = f"USE {database}" # 避免频繁调用数据库
        self.cursor.execute(use_query)
        try:
            tables = ["student", "bed", "room", "floor", "tutor", "building", "warden"] # 按照外键依赖顺序删除
            tables += ["repair_request", "adjust_request"]
            for tb_name in tables:
                self.delete_table(tb_name)
            self.connection.commit()
            print(f"All tables in database '{database}' deleted successfully.")
        except pymysql.Error as e:
            print(f"Error deleting all databases: {e}")
            self.connection.rollback()  