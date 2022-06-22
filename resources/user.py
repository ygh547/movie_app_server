from http import HTTPStatus
from os import access
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector
from email_validator import validate_email, EmailNotValidError

from utils import check_password, hash_password

class UserRegisterResource(Resource) :

    # 회원 가입
    def post(self):

        #1. 클라이언트로부터 넘어온 데이터를 받는다.
        # {
        #     "email": "a36@gmail.com",
        #     "password": "1234"
        #     "username": "Mod",
        #     "gender" : 1
        # }
        # 0은 여자 , 1은 남자

        data = request.get_json()

        #2. 이메일 형식 체크
        try:
            validate_email( data['email'] )
        
        except EmailNotValidError as e :
            return {'error' : str(e), 'error_no' : 1 } , 400

        #3. 비밀번호 길이 체크 4자리 이상 12자리 이하가 정상이다.
        if len( data['password'] ) < 4 or len( data['password']) > 12 :
            return{'error' : '비밀번호 길이를 확인하세요', 'error_no' : 2 }, 400
        
        #4. 비밀번호 암호화 작업
        hashed_password = hash_password( data['password'] )

        #5. 데이터베이스에 저장한다.
        try :
            # 데이터 insert 
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''insert into user
                    (email,password,username,gender)
                    values
                    (%s, %s , %s,%s);'''
            
            record = (data['email'], hashed_password,data['username'],data['gender'])

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 5-1. 디비에 저장된 아이디값 가져오기.
            user_id = cursor.lastrowid

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e), 'error_no' : 3}, 503
    
        #6. jwt 억세스 토큰을 생성해서, 클라이언트에 응답해준다.
        access_token = create_access_token(user_id)


        return {'result' : 'success', 'access_token' : access_token}, 200