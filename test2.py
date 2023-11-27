import json

import app as app
from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib import parse
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

@app.route('/api', methods=['GET'])
def get_test():

    def get_page_contents(url):
        # 웹사이트에서 페이지 내용을 가져옵니다.
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print("페이지를 가져오는데 실패했습니다.")
            return None


    def extract_data_from_page(html_content):
        # BeautifulSoup을 사용하여 웹 페이지의 HTML을 파싱합니다.
        soup = BeautifulSoup(html_content, 'html.parser')

        return soup


    if __name__ == "__main__":
        today = date.today()

        # 공고 게시 시작일
        one_month = timedelta(days=30)
        from_bid_dt = (today - one_month).strftime("%Y/%m/%d")

        # 공고 게시 종료일
        to_bid_dt = today.strftime("%Y/%m/%d")


        url = "https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidSearchType=1&taskClCds=&bidNm=&searchDtType=1&fromBidDt={}&toBidDt={}&fromOpenBidDt=&toOpenBidDt=&radOrgan=2&instNm=&instSearchRangeType=&refNo=&area=&areaNm=&strArea=&orgArea=&industry=&industryCd=&upBudget=&downBudget=&budgetCompare=&detailPrdnmNo=&detailPrdnm=&procmntReqNo=&intbidYn=&regYn=Y&recordCountPerPage=100".format(

            parse.quote(from_bid_dt, encoding='cp949'),
            parse.quote(to_bid_dt, encoding='cp949')

        )  # 크롤링할 웹사이트 URL을 입력

        #print(bid_nm, from_bid_dt, to_bid_dt, inst_nm)
        page_contents = get_page_contents(url)
        if page_contents:
            soup = extract_data_from_page(page_contents)

            # 클래스가 "results"인 요소
            results_div = soup.find('div', class_='results')

            # 결과 div 안에서 tbody
            tbody_tag = results_div.find('tbody')

            # tbody 태그 안에서 첫 번째 tr
            tr_tags = tbody_tag.find_all('tr')
            send_data = []
            send_link_data = []
            link_list = {}

            key_list = ["link1", "link2", "link3", "link4"]
            for i, links in enumerate(tr_tags):
                a_tags = links.find_all('a')
                for j, a in enumerate(a_tags):
                    if j < len(key_list):
                        key = key_list[j]
                        value = a.get('href')
                        link_list[key] = value

                        #print(link_list)
                    send_link_data.append(link_list)


            for tr_tag in tr_tags:
                first_td = tr_tag.find_all('td')
                #print(first_td)

                if first_td:
                    data_json = {}

                    for i, element in enumerate(first_td):
                        # div 태그 안의 텍스트를 추출
                        text = element.find('div').text

                        # 임시로 지정한 키값
                        keys = ["data1", "data2", "data3", "data4", "data5", "data6", "data7", "data8", "data9",
                                "data10", "data11", "data12"]

                        if i < len(keys):
                            data_json[keys[i]] = text

                    data_json.update(link_list)
                    send_data.append(data_json)


                else:
                    print("Error.")

            # tr 태그 안에서 첫 번째 td 태그

            result = []
            result_data = {}

            for d in send_data:
                result_data.update(d)


            for d in send_link_data:
                result_data.update(d)

    #print(send_data)
    return jsonify(send_data)

if __name__ == '__main__':
    app.run(debug=True)


