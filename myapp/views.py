from django.shortcuts import render
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch

# def chat(request):
#     return render(request, 'home.html')

# ================================================================
# pip install transformers => cmd창에서 install
# pip install pandas => cmd창에서 install
# pip install torch => cmd창에서 install
import torch
from transformers import pipeline
import pandas as pd
from transformers import TapexTokenizer, BartForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForTokenClassification

import sqlite3

import json

from django.http import JsonResponse

count = 1
userResultInfo={}

# 좋아하는 것 순서대로 뽑는 함수
def printFor(list) :

  result = ''
  count = 0

  for i in list :
    if count == 0 :
      result = i
    else :
      result = result + ', ' + i
    count = count + 1

  return result



def home(request):
    return render(request, 'home.html',{'count':count})



# '네'선택 시 작동되는 함수
def yesAnswerFn(request) :
  # 모델 세팅
  tokenizer = AutoTokenizer.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  model = AutoModelForTokenClassification.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  ner = pipeline("ner", model=model, tokenizer=tokenizer)
  
  count = 2

  # 글로벌 변수로 설정
  global uniData
  global conData
  global userUniInfo
  global userConInfo
  global userResultInfo

  # 좋아하는 과목
  subjectList = []
  # 좋아하는 것
  hobbyList = []
  # 처음인지 아닌지
  first = True

      

  connection = sqlite3.connect('db.sqlite3')  # db.sqlite3 파일의 경로
  cursor = connection.cursor()



  userMsg = request.GET.get('userMsg')
  ner_userAnswer = ner(userMsg)
  
  for i in ner_userAnswer :
    subjectList.append(i['word'])
    if first == True :
      cursor.execute("SELECT * FROM uniInfoTable where 학과 like '%"+i['word']+"%'")
      userResultInfo = cursor.fetchall()
      # userResultInfo = uniData[uniData['1'].str.contains(i['word'], na = False)]
      userResultInfo = pd.DataFrame(userResultInfo)
      first = False
    else :
      # data = uniData[uniData['학과'].str.contains(i['word'], na = False)]
      cursor.execute("SELECT * FROM uniInfoTable where 학과 like '%"+i['word']+"%'")
      data = cursor.fetchall()
      userResultInfo = pd.concat([userResultInfo,data])

  userResultInfo.columns = ['학교', '학과', '등록금', '위치', '과목', '백분위']
  userResultInfo['백분위'].astype(float)

  # 변수 초기화
  first = True

  # if userResultInfo.empty == True :
  #   killProcessMsg()

  return render(request, 'home.html', {'count': count})

  

# 성적
def scoreFn(request) :

  global userResultInfo

  tokenizer = AutoTokenizer.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  model = AutoModelForTokenClassification.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  ner = pipeline("ner", model=model, tokenizer=tokenizer)
  

  userMsg = request.GET.get('userMsg')
  ner_userAnswer = ner(userMsg)

  num = float(ner_userAnswer[0]['word'])
  userResultInfo = userResultInfo[userResultInfo['백분위'] > num]

  # if userResultInfo.empty == True :
  #   print("학생의 성적으로는 갈 수 있는 대학이 없어요 😱")
  #   time.sleep(1)
  #   print("조금 더 공부하고 오세요 😱")
  #   time.sleep(1)
  #   sys.exit()

  print(userResultInfo)
  return render(request, 'home.html')


# 등록금
def moneyFn(request) :

  global userResultInfo

  tokenizer = AutoTokenizer.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  model = AutoModelForTokenClassification.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  ner = pipeline("ner", model=model, tokenizer=tokenizer)
    

  userMsg = request.GET.get('userMsg')
  ner_userAnswer = ner(userMsg)

  list = []
  for i in ner_userAnswer :
    if ('##' in i['word']) == False:
      list.append(i['word'])

  money = int(list[0] + "0000")
  userResultInfo['등록금'] = userResultInfo['등록금'].str.replace(',', '')

  if list[1] == '이상' :
    userResultInfo = userResultInfo[(userResultInfo['등록금'].astype(int) >= money)]
  elif list[1] == '이하' :
    userResultInfo = userResultInfo[(userResultInfo['등록금'].astype(int) <= money)]
  elif list[1] == '초과' :
    userResultInfo = userResultInfo[(userResultInfo['등록금'].astype(int) > money)]
  elif  list[1] == '미만' :
    userResultInfo = userResultInfo[(userResultInfo['등록금'].astype(int) < money)]


  # if userResultInfo.empty == True :
  #   print("조건에 적합한 학교가 없어요 😱")
  #   time.sleep(1)
  #   sys.exit()

  data = userResultInfo.to_json(orient='records')

  return JsonResponse(data, safe=False)
    


# 거리
def localFn(request) :

  global userResultInfo

  tokenizer = AutoTokenizer.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  model = AutoModelForTokenClassification.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  ner = pipeline("ner", model=model, tokenizer=tokenizer)
    

  userMsg = request.GET.get('userMsg')
  ner_userAnswer = ner(userMsg)

  userResultInfo = userResultInfo[userResultInfo['위치'].str.contains(ner_userAnswer[0]['word'], na = False)]

  # if userResultInfo.empty == True :
  #   print("조건에 적합한 학교가 없어요 😱")
  #   time.sleep(1)
  #   sys.exit()

  userResultInfo = userResultInfo.drop_duplicates()
  data = userResultInfo.to_json(orient='records')

  return JsonResponse(data, safe=False)



def likeQuestion(request) : 

  # 모델 세팅
  tokenizer = AutoTokenizer.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  model = AutoModelForTokenClassification.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  ner = pipeline("ner", model=model, tokenizer=tokenizer)

  # 글로벌 변수로 설정
  global uniData
  global conData
  global userUniInfo
  global userConInfo
  global userResultInfo

  # 좋아하는 과목
  subjectList = []
  # 좋아하는 것
  hobbyList = []
  # 처음인지 아닌지
  first = True

  connection = sqlite3.connect('db.sqlite3')  # db.sqlite3 파일의 경로
  cursor = connection.cursor()

  userMsg = request.GET.get('userMsg')
  ner_userAnswer = ner(userMsg)

  for i in ner_userAnswer :
    subjectList.append(i['word'])
    if first == True :
      cursor.execute("SELECT * FROM uniInfoTable where 과목 like '%"+i['word']+"%'")
      userUniInfo = cursor.fetchall()
      userUniInfo = pd.DataFrame(userUniInfo)
      first = False
    else :
      cursor.execute("SELECT * FROM uniInfoTable where 과목 like '%"+i['word']+"%'")
      data = cursor.fetchall()
      data = pd.DataFrame(data)
      userUniInfo = pd.concat([userUniInfo,data])

  userUniInfo.columns = ['학교', '학과', '등록금', '위치', '과목', '백분위']
  userUniInfo['백분위'].astype(float)

  # 변수 초기화
  first = True

  json_data = json.dumps(subjectList)

  return JsonResponse(json_data, safe=False)


def hobbyFn(request) : 

  # 모델 세팅
  tokenizer = AutoTokenizer.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  model = AutoModelForTokenClassification.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  ner = pipeline("ner", model=model, tokenizer=tokenizer)

  # 글로벌 변수로 설정
  global uniData
  global conData
  global userUniInfo
  global userConInfo
  global userResultInfo

  # 좋아하는 과목
  subjectList = []
  # 좋아하는 것
  hobbyList = []
  # 처음인지 아닌지
  first = True

  connection = sqlite3.connect('db.sqlite3')  # db.sqlite3 파일의 경로
  cursor = connection.cursor()

  userMsg = request.GET.get('userMsg')
  ner_userAnswer = ner(userMsg)

  cursor.execute("SELECT * FROM conInfoTable where 상담내역 like '%"+ ner_userAnswer[0]['word']+"%'")
  userConInfo = cursor.fetchall()
  
      
  userConInfo = pd.DataFrame(userConInfo)
  userConInfo.columns = ['학과', '상담내역']
  if userConInfo.empty == False :
    list = userConInfo['학과'].to_list()
    for i in list :
      if first == True :
        cursor.execute("SELECT * FROM uniInfoTable where 학과 like '%"+ i +"%'")
        userResultInfo = cursor.fetchall()
        userResultInfo = pd.DataFrame(userResultInfo)
        first = False
      else :
        cursor.execute("SELECT * FROM uniInfoTable where 학과 like '%"+ i +"%'")
        data = cursor.fetchall()
        data = pd.DataFrame(data)
        userResultInfo = pd.concat([userResultInfo,data])

    # 변수 초기화
    first = True
    userResultInfo.columns = ['학교', '학과', '등록금', '위치', '과목', '백분위']
    userResultInfo = pd.concat([userResultInfo,userUniInfo])
    print(userResultInfo)

  else :
    userResultInfo = userUniInfo

  userResultInfo['백분위'].astype(float)

  # 변수 초기화
  first = True

  return render(request, 'home.html')


def orderByFn(request) : 

  global userUniInfo
  global userConInfo
  global userResultInfo

  # 모델 세팅
  tokenizer = AutoTokenizer.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  model = AutoModelForTokenClassification.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
  ner = pipeline("ner", model=model, tokenizer=tokenizer)


  userMsg = request.GET.get('userMsg')
  ner_userAnswer = ner(userMsg)

  if ner_userAnswer[0]['word'] != '등록금' and ner_userAnswer[0]['word'] != '백분위' :
    #userResultInfo = pd.read_json(userResultInfo)
    userResultInfo = userResultInfo.sort_values('백분위')
  else :
    #userResultInfo = pd.read_json(userResultInfo)
    userResultInfo = userResultInfo.sort_values(ner_userAnswer[0]['word'])

  userResultInfo = userResultInfo.drop_duplicates()
  data = userResultInfo.head()
  data = data.to_json(orient='records')

  return JsonResponse(data, safe=False)