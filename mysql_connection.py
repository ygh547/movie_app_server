import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(
        host = 'jhdb.ct294vqgyq74.ap-northeast-2.rds.amazonaws.com',
        database = 'movie1_db',
        user = 'movie_user',
        password = 'movie1234'
    )
    return connection