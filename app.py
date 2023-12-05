from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pymongo
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
db = client["mydb"]
DICTIONARY_STANDARD = db["DICTIONARY_STANDARD"]
BIDDING_ANNOUNCEMENT = db["BIDDING_ANNOUNCEMENT"]
Keyword = db["KEYWORD"]

yesterday = datetime.now() - timedelta(days=1)
yesterday_str = yesterday.strftime("%Y-%m-%d")

hardcoded_agencies = ["한국사회보장정보원", "대검찰청", "한국출판문화산업진흥원", "한국환경산업기술원", "정보통신산업진흥원", "인사혁신처", "소상공인시장진흥공단",
                      "공정거래위원회", "한국공정거래조정원", "한국국토정보공사", "한국여성인권진흥원", "인천공항공사", "산림청",
                      "산림교육원", "문화재청", "문화체육관광부", "SBA", "서울산업진흥원", "축산물품질평가원", "질병관리본부",
                      "기초과학연구원", "연구개발특구진흥재단", "서울신용보증재단", "방송통신위원회", "한국관광공사", "법무부",
                      "여성가족부", "국회사무처", "국방정보본부", "태권도진흥재단", "보건복지부", "외교부"
                      ]


# 입찰공고 모두보기
@app.route('/api/BIDDING_ANNOUNCEMENT', methods=['POST'])
def bidding_total():
    data = request.get_json()
    start_date = data.get('startDate', )
    end_date = data.get('endDate', )

    # MongoDB 쿼리 생성
    query = {
        "startDate": {"$gte": start_date, "$lte": f"{end_date}T23:59L:59Z"}
    }
    print(query)
    # MongoDB에서 쿼리 실행
    result = list(BIDDING_ANNOUNCEMENT.find(query, {"_id": 0}))

    return jsonify(result)


# 입찰공고 키워드로 보기
@app.route('/api/BIDDING_ANNOUNCEMENT_KEY', methods=['POST'])
def bidding_keyword():
    try:
        data = request.get_json()
        demand_agency = data.get('demandAgency', [])
        announcement_names = data.get('announcementName', [])
        start_date = data.get('startDate', )
        end_date = data.get('endDate', )

        query = {
            "$and": [
                {"demandAgency": {"$regex": f".*{'|'.join(demand_agency)}.*"}},
                {"announcementName": {"$regex": f".*{'|'.join(announcement_names)}.*"}},
                {"startDate": {"$gte": start_date, "$lte": f"{end_date}T23:59L:59Z"}}
            ]
        }
        print(query)

        result = list(BIDDING_ANNOUNCEMENT.find(query, {"_id": 0}))
        response = {"message": "Success", "data": result}
        return jsonify(result)

    except Exception as e:
        # 예외 로깅
        print(f"An error occurred: {str(e)}")

        # 오류가 발생한 경우 오류 메시지를 JSON 형태로 응답
        response = {"message": "Error", "error": "Bad Request"}
        return jsonify(response), 400


# 사전규격 모두보기
@app.route('/api/DICTIONARY_STANDARD', methods=['POST'])
# GFC 기관
def standard_total():
    data = request.get_json()
    start_date = data.get('startDate', )
    end_date = data.get('endDate', )

    # MongoDB 쿼리 생성
    query = {
        "dateAndTime": {"$gte": start_date, "$lte": f"{end_date}T23:59L:59Z"}
    }
    print(query)
    # MongoDB에서 쿼리 실행
    result = list(DICTIONARY_STANDARD.find(query, {"_id": 0}))  # "_id" 필드는 반환하지 않음

    return jsonify(result)


# 사전규격 키워드로보기
@app.route('/api/DICTIONARY_STANDARD_KEY', methods=['POST'])
def standard_keyword():
    try:
        data = request.get_json()
        demand_agency = data.get('demandAgency', [])
        announcement_names = data.get('announcementName', [])
        start_date = data.get('startDate', )
        end_date = data.get('endDate', )

        query = {
            "$and": [
                {"demandAgency": {"$regex": f".*{'|'.join(demand_agency)}.*"}},
                {"announcementName": {"$regex": f".*{'|'.join(announcement_names)}.*"}},
                {"dateAndTime": {"$gte": start_date, "$lte": f"{end_date}T23:59L:59Z"}}
            ]
        }
        print(query)

        result = list(DICTIONARY_STANDARD.find(query, {"_id": 0}))
        response = {"message": "Success", "data": result}
        return jsonify(result)

    except Exception as e:
        # 예외 로깅
        print(f"An error occurred: {str(e)}")

        # 오류가 발생한 경우 오류 메시지를 JSON 형태로 응답
        response = {"message": "Error", "error": "Bad Request"}
        return jsonify(response), 400


# 키워드 호출
@app.route('/api/MY_KEYWORD', methods=['GET'])
# GFC 기관
def my_keyword():
    result = list(Keyword.find({}, {"_id": 0}))  # "_id" 필드는 반환하지 않음

    for item in result:
        if item.get('field') == 'demandAgency':
            item['field'] = '수요기관'
        elif item.get('field') == 'announcementName':
            item['field'] = '공고명'

    print(result)
    return jsonify(result)

@app.route('/api/MY_KEYWORD_REMOVE', methods=['POST'])
def my_keyword_remove():
    data = request.json

    # 데이터가 리스트인 경우
    if isinstance(data, list):
        for item in data:
            field_name = item.get('field', '')
            key_word = item.get('key', '')
            process_data(field_name, key_word)

    # 데이터가 딕셔너리인 경우
    elif isinstance(data, dict):
        field_name = data.get('field', '')
        key_word = data.get('key', '')
        process_data(field_name, key_word)

    # 데이터 조회 및 수정
    result = list(Keyword.find({}, {"_id": 0}))


    return jsonify(result)

def process_data(field_name, key_word):
    # 특정 조건에 해당하는 데이터를 데이터베이스에서 조회
    items_to_remove = list(Keyword.find({"field": field_name, "key": key_word}))

    # 조회된 데이터 삭제 및 수정
    for item in items_to_remove:
        # 데이터 삭제
        query = {"field": item["field"], "key": item["key"]}
        Keyword.delete_one(query)



@app.route('/api/ADD_KEYWORD', methods=['POST'])
# GFC 기관
def add_keyword():
    data = request.get_json()

    if isinstance(data, list):  # data가 리스트인 경우
        for item in data:
            field_date = item.get('field', '')
            key_date = item.get('key', '')
            query = {
                "id": "gfc",
                "field": field_date,
                "key": key_date
            }
            Keyword.insert_one(query)

    elif isinstance(data, dict):  # data가 딕셔너리인 경우
        field_date = data.get('field', '')
        key_date = data.get('key', '')
        query = {
            "id": "gfc",
            "field": field_date,
            "key": key_date
        }
        Keyword.insert_one(query)

    # 추가한 데이터 조회
    result = list(Keyword.find(query, {"_id": 0}))
    print(result)

    return jsonify(result)


@app.route('/')
def home():  # put application's code here
    return render_template("index.html")


@app.route('/keyword')
def main():  # put application's code here
    return render_template("keyword.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
