import subprocess
import json
import requests

# crow.py 실행 및 결과 가져오기
completed_process = subprocess.run(["python", "crawling2.py"], capture_output=True, text=True)
result_output = completed_process.stdout

# JSON 데이터 생성
data = {
    'result': result_output.strip()  # 결과값을 'result' 키로 저장
}

# JSON 데이터를 문자열로 변환
json_data = json.dumps(data, ensure_ascii=False)

# 서버 URL
url = 'http://example.com/api_endpoint'  # 실제 API 엔드포인트 URL을 넣어주세요

# POST 요청 보내기
response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})

# 응답 확인
if response.status_code == 200:
    print("요청이 성공적으로 전송되었습니다.")
    print("응답 데이터:", response.text)
else:
    print("요청이 실패하였습니다.")
    print("응답 코드:", response.status_code)
