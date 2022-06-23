from http import HTTPStatus
from tokenize import group
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

import pandas as pd

class MovieRecomResource(Resource) :
    @jwt_required()
    def get(self) :
        
        #1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()
        #2. 추천을 위한 상관계수 데이터프레임을 읽어온다.
        df = pd.read_csv('data/movie_correlations.csv', index_col = 'title')
        print(df)

        #3. 이 유저의 별점 정보를, 디비에서 가져온다.

        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''select r.userId, r.movieId, r.rating, m.title 
                        from rating r
                        join movie m
                        on r.movieID = m.id and r.userId = %s;'''

            record = (user_id, )                  

            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query,record)

            # 5. select 문은, 아래 함수를 이용해서, 데이터를 받아온다.
            result_list = cursor.fetchall()

            print(result_list)
            
            # # 중요! 디비에서 가져온 timstamp는 
            # # 파이썬의 datetime 으로 자동 변경된다.
            # # 문제는 이 데이터를 json으로 바로 보낼 수 없으므로,
            # # 문자열로 바꿔서 다시 저장해서 보낸다.
            # i=0
            # for record in result_list :
            #     result_list[i]['avg'] = float(record['avg'])
                
            #     i = i+1

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e), 'error_no' : 20}, 503

        # 디비로 부터 가져온, 내 별점 정보를, 데이터프레임으로
        # 만들어준다.
        df_my_rating = pd.DataFrame(data=result_list)

        # 추천 영화를 저장할, 빈 데이터프레임 만든다.
        similar_movie_list = pd.DataFrame()

        for i in range( len(df_my_rating) ) :
            similar_movie = df[df_my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlation']
            similar_movie['Weight'] = df_my_rating['rating'][i] * similar_movie['Correlation']
            similar_movie_list = similar_movie_list.append(similar_movie)

        # 영화 제목이 중복된 영화가 있을수있다.
        # 중복된 영화는, Weight 가 가장 큰(max)값으로 해준다.
        similar_movie_list.reset_index(inplace=True)
        
        similar_movie_list = similar_movie_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 내가 이미 봐서, 별점을 남긴 영화는 여기서 제외 해야한다.

        print(similar_movie_list)

        similar_movie_list = similar_movie_list.reset_index()

        # 내가 이미 본 영화 제목만 가져온다.
        title_list = df_my_rating['title'].tolist()

        # similar_movie_list 에 내가 본영화인 title_list 를 제외하고 가져온다.

        print(similar_movie_list)
        print(title_list)

        # similar_movie_list['title'].isin(title_list)

        recomm_movie_list = similar_movie_list.loc[ ~similar_movie_list['title'].isin(title_list) , ]

        print(recomm_movie_list.iloc[ 0 : 19+1 , ])



        return {'result' : 'success', 'movie_list' : recomm_movie_list.iloc[ 0 : 19+1 , ].to_dict('records')}

class MovieRecomRealTimeResource(Resource):
    @jwt_required()
    def get(self) :
        # 1. 클라이언트로부터 데이터 받아온다.
        user_id = get_jwt_identity()

        # 2. 추천을 위한 상관계수를 위해, 데이터베이스에서 데이터를 받아온다.


        #3. 이 유저의 별점 정보를, 디비에서 가져온다.

        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()

            query = '''select r.userId, r.movieId, r.rating, m.title  
                        from rating r
                        join movie m
                        on r.movieId = m.id;'''

            # record = (user_id, )                  

            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query)

            # 5. select 문은, 아래 함수를 이용해서, 데이터를 받아온다.
            result_list = cursor.fetchall()

            df = pd.DataFrame(data=result_list)
            
            # 피봇 테이블한후, 상관계수를 뽑는다.
            df = df.pivot_table(index='userId',columns='title', values='rating')

            #영화별로 50개 이상의 리뷰있는 영화만 상관계수 계산하기
            df = df.corr(min_periods=50)

            # 2. 쿼리문 만들기
            query = '''select r.userId, r.movieId, r.rating, m.title 
                        from rating r
                        join movie m
                        on r.movieID = m.id and r.userId = %s;'''

            record = (user_id, )                  

            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query,record)

            # 5. select 문은, 아래 함수를 이용해서, 데이터를 받아온다.
            result_list = cursor.fetchall()

            print(result_list)
            
            # # 중요! 디비에서 가져온 timstamp는 
            # # 파이썬의 datetime 으로 자동 변경된다.
            # # 문제는 이 데이터를 json으로 바로 보낼 수 없으므로,
            # # 문자열로 바꿔서 다시 저장해서 보낸다.
            # i=0
            # for record in result_list :
            #     result_list[i]['avg'] = float(record['avg'])
                
            #     i = i+1

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e), 'error_no' : 20}, 503

        # 디비로 부터 가져온, 내 별점 정보를, 데이터프레임으로
        # 만들어준다.
        df_my_rating = pd.DataFrame(data=result_list)

        # 추천 영화를 저장할, 빈 데이터프레임 만든다.
        similar_movie_list = pd.DataFrame()

        for i in range( len(df_my_rating) ) :
            similar_movie = df[df_my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlation']
            similar_movie['Weight'] = df_my_rating['rating'][i] * similar_movie['Correlation']
            similar_movie_list = similar_movie_list.append(similar_movie)

        # 영화 제목이 중복된 영화가 있을수있다.
        # 중복된 영화는, Weight 가 가장 큰(max)값으로 해준다.
        similar_movie_list.reset_index(inplace=True)
        
        similar_movie_list = similar_movie_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 내가 이미 봐서, 별점을 남긴 영화는 여기서 제외 해야한다.

        print(similar_movie_list)

        similar_movie_list = similar_movie_list.reset_index()

        # 내가 이미 본 영화 제목만 가져온다.
        title_list = df_my_rating['title'].tolist()

        # similar_movie_list 에 내가 본영화인 title_list 를 제외하고 가져온다.

        print(similar_movie_list)
        print(title_list)

        # similar_movie_list['title'].isin(title_list)

        recomm_movie_list = similar_movie_list.loc[ ~similar_movie_list['title'].isin(title_list) , ]

        print(recomm_movie_list.iloc[ 0 : 19+1 , ])



        return {'result' : 'success', 'movie_list' : recomm_movie_list.iloc[ 0 : 19+1 , ].to_dict('records')}


        
            