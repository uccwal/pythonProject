from datetime import date, timedelta
from urllib.parse import quote
import codecs

today = date.today()
one_month = timedelta(days=30)
from_bid_dt = today - one_month
to_bid_dt = today

print(to_bid_dt.strftime("%Y/%m/%d"))
print(from_bid_dt.strftime("%Y/%m/%d"))

# cp949로 인코딩하기 위해 codecs 모듈을 사용합니다.
encoded_to_bid_dt = codecs.encode(to_bid_dt.strftime("%Y/%m/%d"), 'cp949')
print(quote(encoded_to_bid_dt))
