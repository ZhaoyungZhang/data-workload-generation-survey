import requests
from bs4 import BeautifulSoup
 
res = requests.get('http://news.sina.com.cn/c/nd/2017-06-12/doc-ifyfzhac1650783.shtml')
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text,'html.parser')
#取评论数
commentCount = soup.select_one('#commentCount1')
print(commentCount.text)