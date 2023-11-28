from flask import Flask, jsonify
import pymongo

app = Flask(__name__)

# MongoDB 연결 정보
client = pymongo.MongoClient("mongodb://mongo:mongo@localhost:27017/")
db = client["mydb"]
collection = db["testdata"]

# 쿼리 실행
query = {
    "work": "공사",
    "$or": [
        {"announcementAgency": {"$regex": "교육청|국무조정실"}}
    ]
}

result = list(collection.find(query))  # 결과를 리스트로 변환

# GET 요청에 대한 핸들러
@app.route('/api', methods=['GET'])
def get_data():
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
