import mysql.connector
from DB import get_db_connection

def get_song(song_id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM song WHERE song_id = %s" #<-- เครื่องหมาย * คือการเรียกทุกอย่างใน Database ของ song_id นั้นพวก column
                                                            #สามารถเปลี่ยน * เป็นชื่อ Column ที่ต้องการเรียกแทนได้
                                                            #หลัง FROM คือชื่อคารางที่ต้องการเรียกข้อมูล 
                                                            #WHERE คือกำหนดเงื่อนไขในการเรียกเช่นอันนี้คือ song_id = เลขid ที่รับเข้ามา
            cursor.execute(query, (song_id,))   #Cast เป็น Tuple
            song = cursor.fetchone()
            return song
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        print("Failed database connection.")
# ทดลองดึงข้อมูลเพลงมาให้ song_id ที่ 1
for i in range(1,20): #ทดลองดึงเพลงมา 19 เพลงจาก song_id 1-20
    song_data = get_song(i) 
    if song_data:
        print(f"Song data: {song_data}")
    else:
        print("Song not found or error occurred.")