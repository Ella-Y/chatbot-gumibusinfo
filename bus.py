# from flask import Flask
import urllib.request
import re
from bs4 import BeautifulSoup

# from slackeventsapi import SlackEventAdapter

# app = Flask(__name__)

# SLACK_TOKEN = "xoxb-678240847346-678241561554-0Z5pQnGul0be8Lv9RFKyealf"
# SLACK_SIGNING_SECRET = "6d1d113208d4603711b35b02dd84e270"
#
# app = Flask(__name__)
# # /listening 으로 슬랙 이벤트를 받습니다.
# slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
# slack_web_client = WebClient(token=SLACK_TOKEN)

# @app.route('/')

bus_list = [
   [[890, 883-1, 881, 885, 884, 883, 184, 890, 884-1, 184], 32],
   [[187, 891-1, 891, 180], 33],
   [[5100], 22],
   [[382-2], 62],
   [[188], 41],
   [[185], 35],
   [[380-3], 68],
   [[182], 44]
]

# 버스 있는지 찾기:
# find_bus(bus_name:int)
def find_bus(bus_name):
   global bus_list
   time = -1

   for buses in bus_list:
      if bus_name in buses[0]:
         time=buses[1]

   return time



def businfo10704to10080(): #메가박스에서 구미역
   arrive_content = []
   mylist0 = []
   mylist1 = []
   mylist2 = []
   url = "http://bis.gumi.go.kr/moMap/mBusStopResult.do?station_id=704&route_id=18620&searchType=N&searchKeyword=10704&serivce_id=&searchType=N"
   source_code = urllib.request.urlopen(url).read()
   soup = BeautifulSoup(source_code, "html.parser")

   for arrive in soup.find_all("div", class_="con_view01"): #버스 번호 받아오기
      temp = arrive.getText().strip('\n')
      temp = re.findall("\d+", temp) # ['180'] ['180','2']
      if len(temp)==1:
         temp=temp[0]
      else:
         temp='-'.join(temp)
      mylist0.append(temp)

   for arrive in soup.find_all("div", class_="con_view02"): #몇 정거장 전인지 받아오기
      temp = arrive.getText().strip('\n')
      mylist1.append(temp)

   for arrive in soup.find_all("div", class_="con_view03"): #몇 분후 도착 예정인지 받아오기
      temp = arrive.getText().strip('\n')
      mylist2.append(temp)

   for i in range(len(mylist1)):
      if(mylist1[i] != "도착정보가없습니다." and mylist1[i] != "도착정보가 없습니다."):

         time=find_bus(int(mylist0[i]))
         if time>0:
            arrive_content.append([mylist0[i], mylist1[i], mylist2[i], time])
   return arrive_content

def businfo10708to10080(): #인동정류장에서 구미역
   arrive_content = []
   mylist0 = []
   mylist1 = []
   mylist2 = []

   url = "http://bis.gumi.go.kr/moMap/mBusStopResult.do?station_id=708&route_id=18620&searchType=N&searchKeyword=10708&serivce_id=&searchType=N"
   source_code = urllib.request.urlopen(url).read()
   soup = BeautifulSoup(source_code, "html.parser")

   for arrive in soup.find_all("div", class_="con_view01"):
      temp = arrive.getText().strip('\n')
      temp = re.findall("\d+", temp) # ['180'] ['180','2']
      if len(temp)==1:
         temp=temp[0]
      else:
         temp='-'.join(temp)
      mylist0.append(temp)

   for arrive in soup.find_all("div", class_="con_view02"):
      temp = arrive.getText().strip('\n')
      mylist1.append(temp)

   for arrive in soup.find_all("div", class_="con_view03"):
      temp = arrive.getText().strip('\n')
      mylist2.append(temp)

   for i in range(len(mylist1)):
      if(mylist1[i] != "도착정보가없습니다." and mylist1[i] != "도착정보가 없습니다."):
         arrive_content.append([mylist0[i], mylist1[i], mylist2[i]])
   return arrive_content

def businfo10080to10708(): #구미역에서 인동정류장
   arrive_content = []
   mylist0 = []
   mylist1 = []
   mylist2 = []

   url = "http://bis.gumi.go.kr/moMap/mBusStopResult.do?station_id=80&route_id=18620&searchType=N&searchKeyword=10080&serivce_id=&searchType=N"
   source_code = urllib.request.urlopen(url).read()
   soup = BeautifulSoup(source_code, "html.parser")

   for arrive in soup.find_all("div", class_="con_view01"):
      temp = arrive.getText().strip('\n')
      temp = re.findall("\d+", temp) # ['180'] ['180','2']
      if len(temp)==1:
         temp=temp[0]
      else:
         temp='-'.join(temp)
      mylist0.append(temp)

   for arrive in soup.find_all("div", class_="con_view02"):
      temp = arrive.getText().strip('\n')
      mylist1.append(temp)


   for arrive in soup.find_all("div", class_="con_view03"):
      temp = arrive.getText().strip('\n')
      mylist2.append(temp)

   for i in range(len(mylist1)):
      if(mylist1[i] != "도착정보가없습니다." and mylist1[i] != "도착정보가 없습니다."):
         arrive_content.append([mylist0[i], mylist1[i], mylist2[i]])
   return arrive_content

def businfo10080to10383(): #구미역에서 메가박스
   arrive_content = []
   mylist0 = []
   mylist1 = []
   mylist2 = []

   url = "http://bis.gumi.go.kr/moMap/mBusStopResult.do?station_id=80&route_id=18620&searchType=N&searchKeyword=10080&serivce_id=&searchType=N"
   source_code = urllib.request.urlopen(url).read()
   soup = BeautifulSoup(source_code, "html.parser")

   for arrive in soup.find_all("div", class_="con_view01"):
      temp = arrive.getText().strip('\n')
      temp = re.findall("\d+", temp) # ['180'] ['180','2']
      if len(temp)==1:
         temp=temp[0]
      else:
         temp='-'.join(temp)
      mylist0.append(temp)

   for arrive in soup.find_all("div", class_="con_view02"):
      temp = arrive.getText().strip('\n')
      mylist1.append(temp)


   for arrive in soup.find_all("div", class_="con_view03"):
      temp = arrive.getText().strip('\n')
      mylist2.append(temp)

   for i in range(len(mylist1)):
      if(mylist1[i] != "도착정보가없습니다." and mylist1[i] != "도착정보가 없습니다."):
         arrive_content.append([mylist0[i], mylist1[i], mylist2[i]])
   return arrive_content

def main():
   print("인동정류장 to 구미역", end=' '); print(businfo10704to10080())
   print("메가박스 to 구미역",   end='   '); print(businfo10708to10080())
   print("구미역 to 인동정류장", end=' '); print(businfo10080to10708())
   print("구미역 to 메가박스", end='   '); print(businfo10080to10383())

if __name__ == '__main__':
    main()
    timetable={'460',['07:05'],

               }