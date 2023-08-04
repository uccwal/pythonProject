import json

import requests
from bs4 import BeautifulSoup
from urllib import parse
from datetime import date, timedelta


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
    # 업무
    task_cl_cds = input("업무 코드 (숫자 1 ~ 8) : ")

    # 공고명
    bid_nm = input("공고명 : ")

    # 공고 게시 시작일
    one_month = timedelta(days=30)
    from_bid_dt = (today - one_month).strftime("%Y/%m/%d")

    # 공고 게시 종료일
    to_bid_dt = today.strftime("%Y/%m/%d")

    # 기관명
    inst_nm = input("기관명 : ")

    url = "https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidSearchType=1&taskClCds={}&bidNm={}&searchDtType=1&fromBidDt={}&toBidDt={}&fromOpenBidDt=&toOpenBidDt=&radOrgan=2&instNm={}&instSearchRangeType=&refNo=&area=&areaNm=&strArea=&orgArea=&industry=&industryCd=&upBudget=&downBudget=&budgetCompare=&detailPrdnmNo=&detailPrdnm=&procmntReqNo=&intbidYn=&regYn=Y&recordCountPerPage=100".format(
        parse.quote(task_cl_cds, encoding='cp949'),
        parse.quote(bid_nm, encoding='cp949'),
        parse.quote(from_bid_dt, encoding='cp949'),
        parse.quote(to_bid_dt, encoding='cp949'),
        parse.quote(inst_nm, encoding='cp949')

    )  # 크롤링할 웹사이트 URL을 입력

    print(bid_nm, from_bid_dt, to_bid_dt, inst_nm)
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
        for tr_tag in tr_tags:
            first_td = tr_tag.find_all('td')
            if first_td:
                data_json = {}

                for i, element in enumerate(first_td):
                    # div 태그 안의 텍스트를 추출
                    text = element.find('div').text

                    # 임시로 지정한 키값
                    keys = ["task", "date", "order", "orderSet", "tas5k", "da1te", "o3rder", "orderSe1t", "tas2k",
                            "date3"]
                    if i < len(keys):
                        data_json[keys[i]] = text

                send_data.append(data_json)
                print(json.dumps(send_data, ensure_ascii=False, indent=4))
            else:
                print("Error.")

        # tr 태그 안에서 첫 번째 td 태그

        print(url)
        print("send_data : ", send_data)

# https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType={search_type}&bidSearchType={bidSearch_type}&taskClCds={task_cl_cds}&bidNm={bid_nm}&searchDtType={search_dt_type}&fromBidDt={from_bid_dt}&toBidDt={to_bid_dt}&fromOpenBidDt={from_open_bid_dt}&toOpenBidDt={to_open_bid_dt}&radOrgan={rad_organ}&instNm={inst_nm}&instSearchRangeType={inst_search_range_type}&refNo={ref_no}&area={area}&areaNm={area_nm}&strArea={str_area}&orgArea={org_area}&industry={industry}&industryCd={industry_cd}&upBudget={up_budget}&downBudget={down_budget}&budgetCompare={budget_compare}&detailPrdnmNo={detail_prdnm_no}&detailPrdnm={detail_prdnm}&procmntReqNo={procmnt_req_no}&intbidYn={intbid_yn}&regYn={reg_yn}&recordCountPerPage=30
# https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType={search_type}&bidSearchType={bidSearch_type}&taskClCds={task_cl_cds}&bidNm={bid_nm}&searchDtType={search_dt_type}&fromBidDt={from_bid_dt}&toBidDt={to_bid_dt}&fromOpenBidDt={from_open_bid_dt}&toOpenBidDt={to_open_bid_dt}&radOrgan={rad_organ}&instNm={inst_nm}&instSearchRangeType={inst_search_range_type}&refNo={ref_no}&area={area}&areaNm={area_nm}&strArea={str_area}&orgArea={org_area}&industry={industry}&industryCd={industry_cd}&upBudget={up_budget}&downBudget={down_budget}&budgetCompare={budget_compare}&detailPrdnmNo={detail_prdnm_no}&detailPrdnm={detail_prdnm}&procmntReqNo={procmnt_req_no}&intbidYn={intbid_yn}&regYn=Y&recordCountPerPage=30
# https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType={search_type}&bidSearchType={bid_search_type}&taskClCds=3&bidNm={bid_nm}&searchDtType=1&fromBidDt={from_bid_dt}&toBidDt={to_bid_dt}&fromOpenBidDt=&toOpenBidDt=&radOrgan=2&instNm={inst_nm}&instSearchRangeType=&refNo=&area=&areaNm=&strArea=&orgArea=&industry=&industryCd=&upBudget=&downBudget=&budgetCompare=&detailPrdnmNo=&detailPrdnm=&procmntReqNo=&intbidYn=&regYn=Y&recordCountPerPage=30
