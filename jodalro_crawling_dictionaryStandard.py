import json
from bson import ObjectId  # 추가
from flask import Flask
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib import parse
from datetime import date, timedelta
from datetime import datetime
import pymongo
import schedule
import time
import threading

app = Flask(__name__)
CORS(app)

# MongoDB에 연결
client = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
db = client["mydb"]
collection = db["DICTIONARY_STANDARD"] #사전규격

# 이전 스크래핑 결과를 저장하는 리스트
previous_data = []


# 공고 정보 스크래핑 함수
def scrape_bid_info_page(page_num):
    today = date.today()

    # 공고 게시 시작일
    one_month = timedelta(days=30)
    fromRcptDt = (today - one_month).strftime("%Y/%m/%d")

    # 공고 게시 종료일
    toRcptDt = today.strftime("%Y/%m/%d")

    url = "https://www.g2b.go.kr:8081/ep/preparation/prestd/preStdPublishList.do?taskClCd=5&orderbyItem=1&searchType" \
          "=1&supplierLoginYn=N&instCl=2&instNm=&dminstCd=&taskClCds=5&prodNm=&swbizTgYn=&searchDetailPrdnmNo" \
          "=&searchDetailPrdnm=&fromRcptDt={}&toRcptDt={}&recordCountPerPage=100&currentPageNo={}".format(
        parse.quote(fromRcptDt, encoding='cp949'),
        parse.quote(toRcptDt, encoding='cp949'),
        page_num
    )  # 크롤링할 웹사이트 URL을 입력

    page_contents = get_page_contents(url)
    if page_contents:
        soup = extract_data_from_page(page_contents)
        send_data = parse_bid_data(soup)
        #print(url)
        return send_data
    else:
        return None


# 웹 페이지 내용을 가져오는 함수
def get_page_contents(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("페이지를 가져오는데 실패했습니다.")
        return None


# 웹 페이지에서 데이터를 추출하는 함수
def extract_data_from_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup


# 공고 데이터를 파싱하는 함수
# parse_bid_data 함수 수정
def parse_bid_data(soup):
    results_div = soup.find('div', class_='results')
    tbody_tag = results_div.find('tbody')
    tr_tags = tbody_tag.find_all('tr')
    send_data = []

    key_list = ["link1", "link2", "link3", "link4"]
    base_url = "https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo="

    for tr_tag in tr_tags:
        a_tags = tr_tag.find_all('a')
        link_list = {}  # 각 항목에 대한 새로운 link_list 생성

        for j, a in enumerate(a_tags):
            if j < len(key_list):
                key = key_list[j]
                # href 속성을 사용하여 URL 생성
                value = base_url + a.get('href').split("'")[1]
                link_list[key] = value

        first_td = tr_tag.find_all('td')

        if first_td:
            data_json = {}
            for i, element in enumerate(first_td):
                text = element.find('div').text
                keys = ["no", "registrationNumber", "referenceNumber", "announcementName", "demandAgency", "dateAndTime",
                        "companyRegistration"]

                if i < len(keys):
                    if keys[i] in ["announcementName", "demandAgency"]:
                        text = ' '.join(text.split()).strip()
                    elif keys[i] == "dateAndTime":
                        date_time_obj = datetime.strptime(text, "%Y/%m/%d %H:%M")
                        text = date_time_obj.strftime("%Y-%m-%d %H:%M")

                    data_json[keys[i]] = text

            data_json.update(link_list)
            send_data.append(data_json)

    return send_data

# periodic_task 함수 수정
def periodic_task():
    global previous_data

    #print("Scheduled task started")

    # 스크래핑 및 데이터 추가
    all_data = []
    for page_num in range(1, 20):
        scraped_data = scrape_bid_info_page(page_num)
        if scraped_data:
            all_data.extend(scraped_data)

    if all_data:
        #print("API 호출 성공")
        new_data = []

        # 스크래핑한 데이터를 MongoDB에 추가 또는 업데이트
        for data in all_data:
            # 중복 데이터 여부를 확인하기 위해 조건을 설정합니다.
            condition = {
                "referenceNumber": data["referenceNumber"],
                "announcementName": data["announcementName"]
            }
            existing_data = collection.find_one(condition)

            if existing_data:
                # 이미 존재하는 경우, 해당 문서를 업데이트
                update_data = {
                    "$set": data  # 새로운 데이터로 업데이트
                }
                collection.update_one(condition, update_data, upsert=True)
                print("데이터 업데이트:", data)
            else:
                # 존재하지 않는 경우, 새로운 문서를 추가
                data["_id"] = str(ObjectId())
                collection.insert_one(data)
                print("데이터 추가:", data)
                new_data.append(data)

        if new_data:
            new_data_json = [item for item in new_data if "_id" not in item]
            print("새로 추가된 데이터:", json.dumps(new_data_json, indent=4))

        previous_data = all_data

        print("데이터 추가 및 업데이트 완료")
    else:
        print("API 호출 실패")

    #print("Scheduled task completed")

#periodic_task()

# 스케줄링을 설정합니다. 10초마다 함수를 실행하도록 설정합니다.
schedule.every(2).seconds.do(periodic_task)
#schedule.every().hour.do(periodic_task)


# 스케줄링 작업을 백그라운드에서 실행합니다.
def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)  # 1초마다 스케줄링을 확인합니다.


# Flask 애플리케이션을 시작하기 전에 스케줄링 스레드를 시작합니다.
if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=schedule_loop)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    app.run(debug=True)
