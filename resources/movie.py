from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector



class MovieListResource(Resource):

    def get(self) :
        # 1. 클라이언트로부터 데이터 받아온다.
        # offset : 0 , limit : 25

        offset = request.args['offset']
        limit = request.args['limit']
        order = request.args['order']

        # 2. 디비로부터 영화 가져온다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''select m.id, m.title,count(r.movieId) as cnt, ifnull(avg(r.rating), 0) as avg
                        from movie m
                        left join rating r
                        on m.id = r.movieId
                        group by m.id
                        order by ''' + order + ''' desc
                        limit '''+offset+''' , '''+limit+'''; '''

            # record = (user_id, )                  

            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query)

            # 5. select 문은, 아래 함수를 이용해서, 데이터를 받아온다.
            result_list = cursor.fetchall()

            print(result_list)
            
            # # 중요! 디비에서 가져온 timstamp는 
            # # 파이썬의 datetime 으로 자동 변경된다.
            # # 문제는 이 데이터를 json으로 바로 보낼 수 없으므로,
            # # 문자열로 바꿔서 다시 저장해서 보낸다.
            i=0
            for record in result_list :
                result_list[i]['avg'] = float(record['avg'])
                
                i = i+1
            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e), 'error_no' : 20}, 503

        return {'result' : 'success', 'count' : len(result_list), 'items' : result_list}, 200

class MovieResource(Resource) :
    def get(self, movieId) :
        # 1. 클라이언트로부터 데이터 받아온다.
        
        try :
            connection = get_connection()

            query = '''select m.*, count(r.movieId) as cnt, ifnull(avg(r.rating), 0) as avg
                        from movie m
                        left join rating r
                        on m.id = r.movieId
                        where m.id = %s
                        group by m.id
                        ;'''
            record = (movieId, )
            
            # select 문은, dictionary = True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # select 문은, 아래 함수를 이용해서, 데이터를 가져온다.
            result_list = cursor.fetchall()

            print(result_list)

            # 중요! 디비에서 가져온 timestamp 는 
            # 파이썬의 datetime 으로 자동 변경된다.
            # 문제는! 이데이터를 json 으로 바로 보낼수 없으므로,
            # 문자열로 바꿔서 다시 저장해서 보낸다.
            i = 0
            for record in result_list :
                result_list[i]['avg'] = float(record['avg'])
                result_list[i]['year'] = record['year'].isoformat()
                result_list[i]['createdAt'] = record['createdAt'].isoformat()
                i = i + 1                

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e), 'error_no' : 20}, 503

        return {'result' : 'success', 'items' : result_list[0]}, 200




class MoviesearchResource(Resource) :
    def get(self) :
        # 1. 클라이언트로부터 데이터 받아온다.
        # ?keyword=re&offset=0&limit=25

        keyword = request.args['keyword']
        offset = request.args['offset']
        limit = request.args['limit']
        

        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''select m.title, count(r.movieId) as cnt, ifnull(avg(r.rating),0) as avg
                        from movie m
                        left join rating r
                            on m.id = r.movieId 
                        where m.title like '%'''+keyword+'''%'
                        group by m.id
                        limit '''+offset+''' , '''+limit+'''; '''

            # record = (title, )                  

            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query)

            # 5. select 문은, 아래 함수를 이용해서, 데이터를 받아온다.
            result_list = cursor.fetchall()

            print(result_list)
            
            # # 중요! 디비에서 가져온 timstamp는 
            # # 파이썬의 datetime 으로 자동 변경된다.
            # # 문제는 이 데이터를 json으로 바로 보낼 수 없으므로,
            # # 문자열로 바꿔서 다시 저장해서 보낸다.
            i=0
            for record in result_list :
                result_list[i]['avg'] = float(record['avg'])
                
                i = i+1
            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e), 'error_no' : 20}, 503
        
        return {'result' : 'success','count' : len(result_list) ,'items' : result_list}, 200


