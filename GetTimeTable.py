import urllib.request
import re
import requests
import json
import urllib.parse

from bs4 import BeautifulSoup


def getFile():
    url = 'http://bis.gumi.go.kr/city_bus/city_time_service.do'
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    tbody = soup.find('tbody')

    with open('myfile.txt', 'w') as file:
        for tr in tbody.find_all('tr'):
            mystring = ''
            href = 'http://bis.gumi.go.kr'
            for td in tr.find_all('td'):
                try:
                    temp_href = td.find('a')['href']
                    if temp_href[1] == 'c':
                        href += temp_href + '&remark='
                except TypeError:
                    pass

                mystring += td.getText() + '\t'
            file.write(mystring.strip() + '\t' + href + '\n')
    print('done')


def getStart_gumiStation():
    start_gumiStation = []

    with open('myfile.txt', 'r') as file:
        for line in file:
            mylist = line.strip().split('\t')

            if mylist[2].startswith('구미역'):
                mylist[-1]+=mylist[1]
                start_gumiStation.append(mylist)
                print(mylist)

    with open('gumifile.txt','w') as file:
        for item in start_gumiStation:
            file.write('\t'.join(item))
            file.write('\n')

def get_go_indong():
    tBUS_LIST = [
        [['890', '883-1', '881', '885', '884', '883', '184', '890', '884-1', '184'], 32],
        [['187', '891-1', '891', '180'], 33],
        [['5100'], 22],
        [['382-2'], 62],
        [['188'], 41],
        [['185'], 35],
        [['380-3'], 68],
        [['182'], 44]
    ]

    start_gumiStation=[]
    indong_buslist=[]

    for buses, time in tBUS_LIST:
        start_gumiStation+=buses

    with open('gumifile.txt','r') as file:
        for line in file:
            mybus=line.strip().split('\t')
            if mybus[0] in start_gumiStation:
                indong_buslist.append(mybus)

    for item in indong_buslist:
        print(item)

def getTimetable():
    timeTable = {}
    with open('gumifile.txt','r') as file:
        for line in file:
            mybus=line.strip().split('\t')
            print(mybus)
            url = urllib.parse.urlparse(mybus[-1])
            query = urllib.parse.parse_qs(url.query)
            url='http://bis.gumi.go.kr/city_bus/time_table.do?'+urllib.parse.urlencode(query, doseq=True)

            source_code = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(source_code, "html.parser")
            td=soup.find('table',class_='common_tb').find_all('td',class_='cntr')

            for item in td:
                time = item.getText()
                try:
                    int(time)
                except ValueError:
                    if mybus[0] in timeTable:
                        timeTable[mybus[0]].append(time)
                    else:
                        timeTable[mybus[0]]=[time]
    # print(timeTable)
    with open('gumiTimetable.txt','w') as file: #휴일까지 들고오면 안됨.
        for busNumber, times in timeTable.items():
            string=str(busNumber)+'\t'+','.join(times)+'\n'
            file.write(string)

def gumiTimetable_sort():
    timeTable = {}
    with open('gumiTimetable.txt','r') as file:
        for line in file:
            templist=line.strip().split()
            key=templist[0]
            value=sorted(templist[1].split(','))
            timeTable[key]=value

    print(timeTable['11'])

    with open('gumiTimetable.txt','w') as file:
        for busNumber, times in timeTable.items():
            string=str(busNumber)+'\t'+','.join(times)+'\n'
            file.write(string)



if __name__ == '__main__':
    gumiTimetable_sort()
