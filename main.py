import urllib.request
import datetime
import requests
import json
import urllib.parse

from bs4 import BeautifulSoup

from flask import Flask, request
from slack import WebClient
from slack import WebClient
from slack.web.classes import extract_json
from slack.web.classes.blocks import *
from slack.web.classes.elements import *
from slack.web.classes.interactions import MessageInteractiveEvent
from slackeventsapi import SlackEventAdapter
SLACK_TOKEN = ''
SLACK_SIGNING_SECRET = ''

app=Flask(__name__)

# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)

#STATION={1:'TO_INDONG',2:'TO_SAMSUNG',3:'FROM_INDONG_SAGEORI',4:'FROM_MEGABOX'}
TO_INDONG ='TO_INDONG' #'*구미역* :arrow_right: 인동정류장 방면'
TO_SAMSUNG ='TO_SAMSUNG' #구미역 -> 삼성전자후문
FROM_INDONG_SAGEORI ='FROM_INDONG_SAGEORI' # 인동정류장->구미역
FROM_MEGABOX ='FROM_MEGABOX' #메가박스->구미역
EXPECT='EXPECT' #출발예정

BUS_LIST = [
   [['890', '883-1', '881', '885', '884', '883', '184', '890', '884-1', '184'], 32],
   [['187', '891-1', '891', '180'], 33],
   [['5100'], 22],
   [['382-2'], 62],
   [['188'], 41],
   [['185'], 35],
   [['380-3'], 68],
   [['182'], 44],
   [['90,', '110', '10'], 10]
]

timeTable={}
# string 을 리턴합니다.
# [temperature:string, text:string] # 22˚, 비, 어제보다 4˚ 낮아요
# 사용: ' '.join(getWeather())
def getWeather():
    WEATHER_URL = 'https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=%EA%B5%AC%EB%AF%B8%EB%82%A0%EC%94%A8'

    source_code = urllib.request.urlopen(WEATHER_URL).read()
    soup = BeautifulSoup(source_code, "html.parser")
    temperature = soup.find('span', class_='todaytemp').getText() +'˚'
    text=soup.find('p',class_='cast_txt').getText()
    return [temperature, text]

def callingTimeTable():
    global timeTable
    with open('gumiTimetable.txt', 'r') as file:
        for line in file:
            templist = line.strip().split()
            key = templist[0]
            value = sorted(templist[1].split(','))
            timeTable[key] = value



def bus_expect(time_table):
    now_time = datetime.datetime.now()
    now_hour = now_time.hour
    now_minute = now_time.minute
    expect_string=''

    global BUS_LIST
    bus_list=[]
    for buses in BUS_LIST:
        bus_list+=buses[0]

    print(bus_list)
    for key,value in time_table.items():
        if key in bus_list:
            for time_value in value:
                temp = time_value.split(':')
                if (0 < (int(temp[0]) * 60 + int(temp[1]) - (now_hour * 60 + now_minute)) < 45):
                    expect_string+="{0}번 버스\t{1}에 출발예정\n".format(key, time_value)
                    break
                elif ((int(temp[0]) * 60 + int(temp[1]) - (now_hour * 60 + now_minute)) >= 45):
                    break
    return expect_string

# 버스 있는지 찾기:
# find_bus(bus_name:string)
def find_bus(bus_name):
   global BUS_LIST
   time = -1

   for buses in BUS_LIST:
      if bus_name in buses[0]:
         time=buses[1]

   return time

# busInfo(direction:str)
# return arrive_content:list [['187', '8정거장 전  ', '8분후도착예정', 33]]
def busInfo(direction):
    urls={
      'TO_INDONG':"http://bis.gumi.go.kr/moMap/mBusStopResult.do?station_id=80&route_id=18620&searchType=N&searchKeyword=10080&serivce_id=&searchType=N",
      'TO_SAMSUNG':"http://bis.gumi.go.kr/moMap/mBusStopResult.do?station_id=80&route_id=18620&searchType=N&searchKeyword=10080&serivce_id=&searchType=N",
      'FROM_INDONG_SAGEORI':'http://bis.gumi.go.kr/moMap/mBusStopResult.do?station_id=708&route_id=18620&searchType=N&searchKeyword=10708&serivce_id=&searchType=N',
      'FROM_MEGABOX':'http://bis.gumi.go.kr/moMap/mBusStopResult.do?station_id=704&route_id=18620&searchType=N&searchKeyword=10704&serivce_id=&searchType=N'
    }
    url=urls[direction]
    arrive_content = []
    bus_numbers = []
    left_bus_stops = []
    left_times = []
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    for arrive in soup.find_all("div", class_="con_view01"):  # 버스 번호 받아오기
      temp = arrive.getText().strip('\n')
      temp = re.findall("\d+", temp)  # ['180'] ['180','2']
      if len(temp) == 1:
         temp = temp[0]
      else:
         temp = '-'.join(temp)
      bus_numbers.append(temp)

    for arrive in soup.find_all("div", class_="con_view02"):  # 몇 정거장 전인지 받아오기
      temp = arrive.getText().strip('\n')
      left_bus_stops.append(temp)

    for arrive in soup.find_all("div", class_="con_view03"):  # 몇 분후 도착 예정인지 받아오기
      temp = arrive.getText().strip('\n')
      left_times.append(temp)

    for i in range(len(left_bus_stops)):
        if(left_bus_stops[i] == '도착정보가 없습니다.' or left_bus_stops[i] == '도착정보가없습니다.'):
            continue
        else:
            time=find_bus(bus_numbers[i])
            newtime=0
            if time>0 :
                if direction =='TO_INDONG' or direction== 'FROM_INDONG_SAGEORI':
                    time+=1
                    newtime=int(left_times[i].replace('분후도착예정','').strip())+time
                else:
                    newtime=int(left_times[i].replace('분후도착예정','').strip())+time
                arrive_content.append([bus_numbers[i], left_bus_stops[i], left_times[i], str(newtime)])

    arrive_content.sort(key=lambda x: int(x[2].replace('분후도착예정', '').strip()))
    arrive_content.sort(key=lambda x: int(x[-1]))

    return arrive_content

def calling_button():
    head_section=SectionBlock(
        text='안녕하세요? 좋은하루예요.:grinning:\n:bus:어디에서 출발하나요?\n실시간으로 알려드릴께요!'
    )
    button_actions=ActionsBlock(
        elements=[
            ButtonElement(
                text='*구미역* :arrow_right: 인동정류장 방면',
                action_id=TO_INDONG,
                value=str(1)
            ),
            ButtonElement(
                text='*구미역* :arrow_right: 삼성전자후문(메가박스 앞)',
                action_id=TO_SAMSUNG,
                value=str(1)
            ),
            ButtonElement(
                text='*인동정류장(인동사거리 방면)* :arrow_right: 구미역',
                action_id=FROM_INDONG_SAGEORI,
                style='primary',
                value=str(1)
            ),
            ButtonElement(
                text='*인동사거리(메가박스 맞은편)* :arrow_right: 구미역',
                action_id=FROM_MEGABOX,
                style='primary',
                value=str(1)
            ),
            ButtonElement(
                text='*구미역*에서 출발예정인 버스',
                action_id=EXPECT,
                style='danger',
                value=str(1)
            )
        ]

    )
    return [head_section, button_actions]

def BusSection(): #Todo 버스섹션 만들고 divide 넣기
    head_section = SectionBlock(
        text=':bus:*구미역* :arrow_right: 인동정류장 방면'
    )
    return [head_section]


def processing(*text): #text:string
    message_blocks=calling_button()
    return message_blocks

    #사용예시
    # weather_string=' '.join(getWeather())
    # bus_string=''
    # for bus_info in businfo('인동사거리'):
    #     bus_string+=' '.join(bus_info)
    #     bus_string+='\n'
    #
    # return '\n'.join([weather_string,bus_string])
    # return 'i got it.'

def sendMessage(channel,message):
    if type(message) is str:
        slack_web_client.chat_postMessage(
            channel=channel,
            text=message
        )
    elif type(message) is list and type(message[0]) is SectionBlock:
        slack_web_client.chat_postMessage(
            channel=channel,
            blocks=extract_json(message)
        )
    elif message is None:
        slack_web_client.chat_postMessage(
            channel=channel,
            text='처리해야하는 메세지가 없습니다. 다시 한번 확인해 주세요.'
        )


# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]

    #I want to send message
    message=processing()
    sendMessage(channel,message)


# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

# 사용자가 버튼을 클릭한 결과는 /click 으로 받습니다
# 이 기능을 사용하려면 앱 설정 페이지의 "Interactive Components"에서
# /click 이 포함된 링크를 입력해야 합니다.
@app.route('/click', methods=["GET","POST"])
def on_button_click():
    # 버튼 클릭은 SlackEventsApi에서 처리해주지 않으므로 직접 처리합니다
    payload = request.values["payload"]
    click_event = MessageInteractiveEvent(json.loads(payload))
    channel = click_event.channel.id

    KEY=click_event.action_id

    if KEY == EXPECT:
        sendMessage(channel,bus_expect(timeTable))
    else:
        bus_string = ''
        for bus_info in busInfo(KEY): #[['187', '8정거장 전  ', '8분후도착예정', 33]]
            bus_string += '{0}\t{1}\t{2}\t총 {3}분 소요예정\n'.format(bus_info[0], bus_info[1],
                                                               bus_info[2], bus_info[3])

        if bus_string=='':
            bus_string='현재 해당 지역으로 가는 버스가 없습니다 :sob:'

        sendMessage(channel,bus_string)

    return "OK", 200

if __name__ == '__main__':
    callingTimeTable()
    app.run('0.0.0.0', port=8080)
