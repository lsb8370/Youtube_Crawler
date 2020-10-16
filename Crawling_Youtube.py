# -*- coding:utf-8 -*-
import winsound as ws

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from konlpy.tag import Okt

# 파라미터
CHROME_PATH = "D:\coopang\chromedriver.exe"
Keyword = '모여봐요 동물의숲'
URL = 'https://www.youtube.com/results?search_query=' + Keyword
ScrollCount = 1000 # 680(어몽어스 검색어 끝) / 400(Among Us 검색어 끝)
                  # 520(동물의숲 검색어 끝)

# OKT 객체 생성(제목에 사용된 단어 빈도수를 분석하기 위함)
okt = Okt()

# 웹드라이버 설정
driver = webdriver.Chrome(CHROME_PATH)
driver_wait = WebDriverWait(driver, 10)

driver.implicitly_wait(300)

# 정해진 URL로 이동
driver.get(URL)

# 스크롤링
count = 0
body = driver.find_element_by_tag_name('body')
for i in range(ScrollCount):
    body.send_keys(Keys.PAGE_DOWN)
    count += 1
    print(count)
# time.sleep(0)

# 동영상 정보를 저장할 파일 만들기("원하는 파일이름.csv"로 저장될 파일명 지정)
save = open("모여봐요 동물의숲.csv", 'w', encoding='utf-8')
save.write('제목,게시자,구독자수,조회수,게시일')
save.write('\n')

# 명사별 개수를 저장할 Dictionary
nounCount = {}

# 정보 크롤링
videos = driver.find_elements_by_id('dismissable')
for video in videos:
    # 동영상 제목
    title = video.find_element_by_id('video-title').text.replace(',','')
    nouns = okt.nouns(title)
    for noun in nouns:
        if len(noun) < 2:
            continue
        if nounCount.get(noun):
            nounCount[noun] += 1
        else:
            nounCount[noun] = 0
            nounCount[noun] += 1

    # 동영상 링크
    link = video.find_element_by_id('video-title')
    link.send_keys(Keys.CONTROL + "\n")
    driver.switch_to.window(driver.window_handles[1])

    # 채널명
    admin = driver.find_element_by_class_name('style-scope ytd-channel-name').text.replace(',','')

    # 구독자수
    subscriber = driver.find_element_by_id('owner-sub-count').text.replace(',','')
    subscriber = subscriber[4:]

    # 조회수
    viewerCount = driver.find_element_by_css_selector('span.view-count.style-scope.yt-view-count-renderer').text.replace(',','')
    if viewerCount[0] == '현': # 실시간 스트리밍 중인 것 빼기(현재 ~명 시청 중)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        continue
    viewerCount = viewerCount[4:]  # 조회수 ~회 에서 '조회수 '을 제외하기 위함
    index = viewerCount.find('회')
    if index == -1:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        continue
    viewerCount = viewerCount[:index]

    # 게시일
    time = driver.find_element_by_css_selector('div#date.style-scope.ytd-video-primary-info-renderer').text
    time = time[1:].replace(' ', '') # 앞의 온점을 빼기 위함
    if time.find(':') != -1:
        time = time[time.find(':') + 1:]
    times = time.split('.')
    if len(times) != 4:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        continue
    time = times[0] + '.' + times[1] +'.' + times[2]

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    save.write(title + ',' + admin + ',' + subscriber + ',' + viewerCount + ',' + time)

    if video != videos[-1]:
        save.write('\n')

save.close()

# 단어별 빈도수를 파일에 저장("원하는 파일이름.csv"로 저장될 파일명 지정)
# 동영상 정보를 저장했던 파일명과 다르게 지정해야 함을 주의!
save = open("모여봐요 동물의숲 단어별 빈도수.csv", 'w', encoding='utf-8')
save.write('단어,사용횟수')
save.write('\n')
for count in nounCount.keys():
    save.write(count + ',' + str(nounCount[count]) + '\n')

# 다 됐으면 삡-! 소리나게
ws.Beep(2000, 1000)