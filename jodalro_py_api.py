from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
db = client["mydb"]
collection1 = db["testdata"]
collection2 = db["testdata2"]

yesterday = datetime.now() - timedelta(days=1)
yesterday_str = yesterday.strftime("%Y-%m-%d")

hardcoded_agencies = ["한국사회보장정보원", "대검찰청", "한국출판문화산업진흥원", "한국환경산업기술원", "정보통신산업진흥원", "인사혁신처", "소상공인시장진흥공단",
                      "공정거래위원회", "한국공정거래조정원", "한국국토정보공사", "한국여성인권진흥원", "인천공항공사", "산림청",
                      "산림교육원", "문화재청", "문화체육관광부", "SBA", "서울산업진흥원", "축산물품질평가원", "질병관리본부",
                      "기초과학연구원", "연구개발특구진흥재단", "서울신용보증재단", "방송통신위원회", "한국관광공사", "법무부",
                      "여성가족부", "국회사무처", "국방정보본부", "태권도진흥재단", "보건복지부", "외교부"
                      ]

@app.route('/api/collection1', methods=['GET'])
#GFC 기관
def prest_call():



    # MongoDB 쿼리 생성
    query = {
        "startDate": {"$regex": yesterday_str},
        "demandAgency": {"$in": hardcoded_agencies}
    }
    # MongoDB에서 쿼리 실행
    result = list(collection1.find(query, {"_id": 0}))  # "_id" 필드는 반환하지 않음

    return jsonify(result)
@app.route('/api/collection2', methods=['GET'])
#GFC 기관
def prest_call2():



    # MongoDB 쿼리 생성

    query = {
        "dateAndTime": {"$regex": yesterday_str},
        "demandAgency": {"$in": hardcoded_agencies}
    }

    # MongoDB에서 쿼리 실행
    result = list(collection2.find(query, {"_id": 0, "no": 0, "link2": 0}))  # "_id" 필드는 반환하지 않음

    return jsonify(result)





if __name__ == '__main__':
    app.run(debug=True, port=5002)
