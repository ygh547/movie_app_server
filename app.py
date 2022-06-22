
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from config import Config
from resources.movie import MovieListResource, MovieResource, MovieratingResource
# from resources.follow import FollowListResource, FollowResource
# from resources.memo import memoListResource, memoResource
from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource,jwt_blacklist


app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)
# JWT 토큰 라이브러리 만들기
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

# 로그아웃 된 유저인지 확인하는 함수 작성
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

# 경로와 resource(API 코드)를 연결한다.
api.add_resource(UserRegisterResource, '/users/register')
api.add_resource(UserLoginResource, '/users/login')
api.add_resource(UserLogoutResource, '/users/logout')
api.add_resource(MovieListResource, '/movie')
api.add_resource(MovieResource, '/movie/<int:movie_id>')
api.add_resource(MovieratingResource, '/movie/rating/<int: movie_id')
if __name__ == '__main__' :
    app.run()