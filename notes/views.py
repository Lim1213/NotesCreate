from django.shortcuts import render
import requests
import cgi
import io
import os
import shutil
import codecs
import urllib
from django.conf import settings
from django.http import HttpResponse,HttpResponseRedirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
# Create your views here.
def content(request):
    checkResult = checkApiKey(request)
    if not checkResult == None:
        return checkResult

    BACKLOG_URL = "https://k-bis.backlog.jp/api/v2/issues/" + request.GET.get('TaskId')

    headers = {'Authorization': 'Bearer ' + request.session['access_token']}
    # データをリクエスト
    backlog_issues = requests.get(BACKLOG_URL, headers=headers).json()

    BACKLOG_URL = "https://k-bis.backlog.jp/api/v2/projects/1073915303/statuses"

    status_list = requests.get(BACKLOG_URL, headers=headers).json()

    d = {
        'title': backlog_issues["issueKey"] + backlog_issues["summary"],
        'description':backlog_issues["description"],
        'taskId':request.GET.get('TaskId'),
        'StatusList':status_list,
        'SelectStatus':backlog_issues["status"]["id"]
    }
    return render(request, 'index.html',d)

def list(request):
    checkResult = checkApiKey(request)

    if not checkResult == None:
        return checkResult
    
    BACKLOG_URL = "https://k-bis.backlog.jp/api/v2/issues"

    # 課題の内容
    BACKLOG_PARAMS = {
        'projectId[]': 1073915303,
        'statusId[]': {1,2},  # 1:未対応,2:処理中,3:処理済み,4:完了
        'sort': 'updated',  # 更新日でソート
    }
    headers = {'Authorization': 'Bearer ' + request.session['access_token']}

    # データをリクエスト
    backlog_issues = requests.get(BACKLOG_URL, params=BACKLOG_PARAMS, headers=headers).json()
    print(backlog_issues)
    d = {
        'TaskList': backlog_issues,
    }
    return render(request, 'list.html',d)

def CreateText(request):
    #ステータスの更新
    BACKLOG_URL = "https://k-bis.backlog.jp/api/v2/issues/" + request.POST.get('TaskId')
    # 課題の内容
    BACKLOG_PARAMS = {
        'statusId': int(request.POST.get('status')),
    }

    headers = {'content-type': 'application/x-www-form-urlencoded','Authorization': 'Bearer ' + request.session['access_token']}
    # データをリクエスト
    backlog_issues = requests.patch(BACKLOG_URL, params=BACKLOG_PARAMS, headers=headers).json()

    if not request.POST.get('commentFlg') == None :

    
        BACKLOG_URL = "https://k-bis.backlog.jp/api/v2/issues/" + request.POST.get('TaskId') + "/comments"
        # 課題の内容
        BACKLOG_PARAMS = {
            'content': str(request.POST.get('taisaku')),
        }

        # データをリクエスト
        backlog_issues = requests.post(BACKLOG_URL, params=BACKLOG_PARAMS, headers=headers).json()

    form = cgi.FieldStorage()
    title = request.POST.get('title')
    filePath = os.getcwd()+'/'+title
    path = os.getcwd()
    if os.path.exists(filePath):
        shutil.rmtree(filePath)
    os.makedirs(filePath)
    wf = open(os.getcwd()+'/template/01.基本情報.txt')
    data1 = wf.read()  # ファイル終端まで全て読んだデータを返す
    wf.close()
    
    data1 = data1.replace("｛案件区分｝",request.POST.get('itemDivision'))
    data1 = data1.replace("｛システム名｝",request.POST.get('systemName'))
    data1 = data1.replace("｛作業場所｝",request.POST.get('workPlace'))
    data1 = data1.replace("｛作業区分｝",request.POST.get('workDivision'))
    data1 = data1.replace("｛作業日｝",request.POST.get('workDate'))
    data1 = data1.replace("｛開始時刻｝",request.POST.get('startTime'))
    data1 = data1.replace("｛終了時刻｝",request.POST.get('endTime'))
    data1 = data1.replace("｛完了日｝",request.POST.get('compDate'))
    data1 = data1.replace("｛依頼者｝",request.POST.get('owner'))
    data1 = data1.replace("｛対応担当者｝",request.POST.get('tantou'))    
    data1 = data1.replace("｛関係者｝",request.POST.get('kankei'))
#    shutil.copy(os.getcwd()+'/template/01.基本情報.txt', title+'/')
    with codecs.open(filePath+'/01.txt','w', encoding='utf-8') as f:
        f.write(data1)
        f.close()    
        
    with codecs.open(filePath+'/02.txt','w', encoding='utf-8') as f2:
        f2.write(request.POST.get('content'))
        f2.close()
        
    if request.POST.get('genin') != "":
        with codecs.open(filePath+'/03.txt','w', encoding='utf-8') as f3:
            f3.write(request.POST.get('genin'))
            f3.close()
            
    with codecs.open(filePath+'/04.txt','w', encoding='utf-8') as f4:
        f4.write(request.POST.get('taisaku'))
        f4.close()

    with codecs.open(filePath+'/05.txt','w', encoding='utf-8') as f5:
        #f5.write(request.POST.get('taisaku'))
        f5.close()        

    shutil.make_archive(title, 'zip', root_dir= filePath)
    
    shutil.rmtree(filePath)
    
    file_path = os.path.join(settings.MEDIA_ROOT, filePath+'.zip')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="{fn}"'.format(fn=urllib.parse.quote(title+'.zip'))
            return response
            
    raise Http404

def checkApiKey(request):
    if not 'access_token' in request.session:
        if not request.GET.get('code') == None:
            BACKLOG_URL = "https://k-bis.backlog.jp/api/v2/oauth2/token"
            BACKLOG_PARAMS = {
                'grant_type': 'authorization_code',
                'code': request.GET.get('code'),
                'client_id':'eZ0LUyGVJ6ZMaV9yIPWweKQ2nnklgHrH',
                'client_secret':'9UJwoMZnPexX70cS9lABSS0F7wEzRMHmzj4eZ150qyZZDnOZeFSzgPHrKYIrQ39X',
            }
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            backlog_issues = requests.post(BACKLOG_URL, params=BACKLOG_PARAMS, headers=headers).json()
            request.session['access_token'] = backlog_issues['access_token']
            request.session['refresh_token'] = backlog_issues['refresh_token']
            return None
        return HttpResponseRedirect('https://k-bis.backlog.jp/OAuth2AccessRequest.action?response_type=code&client_id=eZ0LUyGVJ6ZMaV9yIPWweKQ2nnklgHrH')
    else:
        BACKLOG_URL = "https://k-bis.backlog.jp/api/v2/oauth2/token"
        BACKLOG_PARAMS = {
            'grant_type': 'refresh_token',
            'client_id':'eZ0LUyGVJ6ZMaV9yIPWweKQ2nnklgHrH',
            'client_secret':'9UJwoMZnPexX70cS9lABSS0F7wEzRMHmzj4eZ150qyZZDnOZeFSzgPHrKYIrQ39X',
            'refresh_token':request.session['refresh_token'],
        }
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        backlog_issues = requests.post(BACKLOG_URL, params=BACKLOG_PARAMS, headers=headers).json()
        request.session['access_token'] = backlog_issues['access_token']
        request.session['refresh_token'] = backlog_issues['refresh_token']
        return None