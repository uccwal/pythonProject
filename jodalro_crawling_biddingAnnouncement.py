from bson import ObjectId  # 추가
from flask import Flask
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib import parse
from datetime import date, timedelta

import pymongo
import schedule
import time
import threading
import re

app = Flask(__name__)
CORS(app)

# 주기적으로 호출할 엔드포인트 URL
api_url = "http://localhost:5000/api"

# MongoDB에 연결
client = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
db = client["mydb"]
collection = db["BIDDING_ANNOUNCEMENT"] #입찰공고

# 이전 스크래핑 결과를 저장하는 리스트
previous_data = []


# 공고 정보 스크래핑 함수
def scrape_bid_info():
    today = date.today()

    # 공고 게시 시작일
    one_month = timedelta(days=30)
    from_bid_dt = (today - one_month).strftime("%Y/%m/%d")

    # 공고 게시 종료일
    to_bid_dt = today.strftime("%Y/%m/%d")
    # to_bid_dt = (today - timedelta(days=1)).strftime("%Y/%m/%d")

    url = "https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidSearchType=1&taskClCds=&bidNm=&searchDtType" \
          "=1&fromBidDt={}&toBidDt={}&fromOpenBidDt=&toOpenBidDt=&radOrgan=2&instNm=&instSearchRangeType=&refNo=&area" \
          "=&areaNm=&strArea=&orgArea=&industry=&industryCd=&upBudget=&downBudget=&budgetCompare=&detailPrdnmNo" \
          "=&detailPrdnm=&procmntReqNo=&intbidYn=&regYn=Y&recordCountPerPage=100&currentPageNo=1".format(
        parse.quote(from_bid_dt, encoding='cp949'),
        parse.quote(to_bid_dt, encoding='cp949')
    )  # 크롤링할 웹사이트 URL을 입력

    page_contents = get_page_contents(url)
    if page_contents:
        soup = extract_data_from_page(page_contents)
        send_data = parse_bid_data(soup)
        print(url)
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
def parse_bid_data(soup):
    results_div = soup.find('div', class_='results')
    tbody_tag = results_div.find('tbody')
    tr_tags = tbody_tag.find_all('tr')

    send_data = []
    link_list = {}

    key_list = ["link1", "link2", "link3", "link4"]
    for i, links in enumerate(tr_tags):
        a_tags = links.find_all('a')
        for j, a in enumerate(a_tags):
            if j < len(key_list):
                key = key_list[j]
                value = a.get('href')
                link_list[key] = value

    for tr_tag in tr_tags:
        first_td = tr_tag.find_all('td')

        if first_td:
            data_json = {}
            for i, element in enumerate(first_td):
                text = element.find('div').text
                # keys = ["data1", "data2", "data3", "data4", "data5", "data6", "data7", "data8", "data9",
                #       "data10", "data11", "data12"]
                keys = ["work", "announcementNumber", "classification", "announcementName", "announcementAgency",
                        "demandAgency", "contractMethod", "dateOfEntry", "data9",
                        "data10", "data11", "data12"]
                if i < len(keys):
                    if keys[i] == "dateOfEntry":
                        # Extract start and end dates
                        start_date, end_date = extract_dates(text)
                        if start_date and end_date:
                            data_json["startDate"] = start_date
                            data_json["endDate"] = end_date
                    else:
                        data_json[keys[i]] = text

            data_json.update(link_list)
            send_data.append(data_json)

    return send_data


def extract_dates(date_string):
    # Using regular expression to extract dates inside parentheses
    match = re.match(r'.*?(\d{4}/\d{2}/\d{2} \d{2}:\d{2})\((\d{4}/\d{2}/\d{2} \d{2}:\d{2})\)', date_string)
    if match:
        start_date, end_date = match.group(1), match.group(2)

        # Replace '/' with '-'
        start_date = start_date.replace('/', '-')
        end_date = end_date.replace('/', '-')

        return start_date, end_date

    # Return None if the format doesn't match
    return None, None


# 주기적으로 호출할 함수를 정의합니다.
def periodic_task():
    global previous_data  # 전역 변수로 이전 데이터 리스트를 사용

    print("Scheduled task started")

    # 스크래핑 및 데이터 추가
    scraped_data = scrape_bid_info()

    if scraped_data:
        print("API 호출 성공")
        new_data = []  # 새로운 데이터를 저장할 리스트

        # 스크래핑한 데이터를 MongoDB에 추가
        for data in scraped_data:
            # 중복 데이터 여부를 확인하기 위해 조건을 설정합니다.
            condition = {
                # "data1": data["data1"],  # 중복을 확인할 필드 1
                # "data2": data["data2"],  # 중복을 확인할 필드 2
                "work": data["work"],
                "announcementNumber": data["announcementNumber"]
                # 필요한 다른 중복 확인 필드들을 추가할 수 있습니다.
            }
            existing_data = collection.find_one(condition)

            if not existing_data:
                # ObjectId를 문자열로 변환하여 추가
                data["_id"] = str(ObjectId())  # ObjectId를 문자열로 변환
                collection.insert_one(data)
                print("데이터 추가:", data)
                new_data.append(data)  # 새로 추가된 데이터를 저장

        # 새로 추가된 데이터만 로그로 출력
        if new_data:
            # ObjectId 필드를 제거하고 JSON으로 직렬화
            new_data_json = [item for item in new_data if "_id" not in item]
            # print("새로 추가된 데이터:", json.dumps(new_data_json, indent=4))

        # 이전 데이터를 현재 스크래핑 결과로 업데이트
        previous_data = scraped_data

        print("데이터 추가 완료")
    else:
        print("API 호출 실패")

    print("Scheduled task completed")


# 스케줄링을 설정합니다. 10초마다 함수를 실행하도록 설정합니다.
schedule.every(2).seconds.do(periodic_task)


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

    app.run(debug=True, port=5001)
