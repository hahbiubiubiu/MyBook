jiutian狠狠拯救贫困大学生😭

# 获取token

使用`browsermob-proxy`获取访问页面时收到的数据包（依赖的Java版本较低，使用的是1.8）。

```python
from pprint import pprint
from selenium.common.exceptions import WebDriverException
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from browsermobproxy import Server

account = '***'
pwd = '***'

def waitUntil(browser, by, value, time_limit):
    while True:
        try:
            t = WebDriverWait(browser, time_limit).until(
                EC.presence_of_element_located((by, value))
            )
            return t
        except:
            print(f"[-] Element not found {by}:{value}")
            browser.refresh()

def waitUntilNot(browser, by, value, time_limit):
    while True:
        try:
            WebDriverWait(browser, time_limit).until_not(
                EC.presence_of_element_located((by, value))
            )
            return
        except:
            print(f"[-] Element not found {by}:{value}")
            browser.refresh()


def main():
    target_url = "https://jiutian.10086.cn/auth/realms/TechnicalMiddlePlatform/protocol/openid-connect/token"
    time_limit = 120
    
    server = Server("browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat")
    server.start()
    proxy = server.create_proxy()
    options = Options()
    options.add_argument(f"--proxy-server={proxy.proxy}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("profile-directory=Profile 1")
    browser = webdriver.Edge('./msedgedriver.exe', options=options)
    proxy.new_har("jiutian", options={'captureHeaders': True, 'captureContent': True})
    url = f"https://jiutian.10086.cn/edu/console#/home/control"
    browser.get(url)
    
    # waitUntil(browser, By.CLASS_NAME, "login-btn", time_limit).click()
    waitUntil(browser, By.XPATH, '//li[@class="login-box-select-item"]', time_limit).click()
    waitUntil(browser, By.ID, "username", time_limit).send_keys(account)
    waitUntil(browser, By.ID, "password", time_limit).send_keys(pwd)
    waitUntil(browser, By.ID, "kc-login", time_limit).click()
    print("[+] Login successful")
    sleep(5)

    json_data = proxy.har
    for entry in json_data['log']['entries']:
        # 根据URL找到数据接口
        entry_url = entry['request']['url']
        if entry_url == target_url:
            response = eval(entry['response']['content']['text'])
            print(f"refresh token: {response['refresh_token']}")
            with open('refresh_token.txt', 'w') as f:
                f.write(response['refresh_token'])
            print(f"Authorization: {response['access_token']}")
            with open('access_token.txt', 'w') as f:
                f.write("Bearer " + response['access_token'])
            break
    server.stop()
    browser.quit()

if __name__ == '__main__':
    main()
```

# 检查可用服务器

恼羞成怒使用打电话，强制提醒自己

```python
import json
import time
import logging
import requests
import urllib3
import sched
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

notice = True
with open('refresh_token.txt', 'r') as f:
    refresh = f.read()
with open('access_token.txt', 'r') as f:
    authorization = f.read()

def send_email():
    try:
        my_sender = SENDER
        my_pass = SENDPASSWD
        my_user = RECEIVER
        msg = MIMEText("有资源了, 冲冲冲!!!", 'plain', 'utf-8')
        msg['From'] = formataddr(["robot", my_sender])
        msg['To'] = formataddr(["user", my_user])
        msg['Subject'] = "JiuTian Resource OK"

        server = smtplib.SMTP_SSL("smtp.163.com", 465)
        server.login(my_sender, my_pass)
        server.sendmail(my_sender, [my_user, ], msg.as_string())
        server.quit()
    except Exception:
        return False
    return True

def send_phonecall():
    try:
        number = YOUR_PHONE_NUMBER
        for _ in range(10):
            # 使用adb打电话
            call = os.popen('adb shell am start -a android.intent.action.CALL -d tel:%s' % number)
            # 这里的sleep时间基本就是你想让通话保持的时间了
            time.sleep(60)
            #挂断电话
            end = os.popen('adb shell input keyevent 6') # code6是挂断
            time.sleep(5)
    except Exception as e:
        logging.error(e)

def refresh_():
    try:
        if os.system("python get_token.py") == 0:
            logging.info('refresh success')
            global refresh, authorization, fail_time
            with open('refresh_token.txt', 'r') as f:
                refresh = f.read()
            with open('access_token.txt', 'r') as f:
                authorization = f.read()
            fail_time = 0
        else: 
            logging.error('refresh failed')
    except Exception as e:
        logging.error(e)

def send_():
    send_phonecall()
    send_email()

urllib3.disable_warnings()
scheduler = sched.scheduler(time.time, time.sleep)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='JiuTian.log',
    filemode='w'
)
fail_time = 0

# 重试5次
def send_request(args):
    success = False
    r = None
    for i in range(20):
        if success:
            break
        try:
            r = requests.request(**args)
            success = True
        except Exception as e:
            logging.error(str(e))
            logging.error('Request failed.')
            time.sleep(30)
    if r is None:
        logging.error('Connection failed.')
        exit(0)
    return r


def turn_notice():
    global notice
    notice = True


def check_resource():
    global authorization
    global notice
    r = send_request({
        'method': 'get',
        'url': 'https://jiutian.10086.cn/edu/dp_platform/resource/index/spec',
        'headers': {'Authorization': authorization},
        'verify': False,
    })
    try:
        res = json.loads(r.text)
        status = res['data']['specShow']['2']
        if  str(status).startswith('52'):
            logging.info("!!!8 core 32G is available!!! status :" + str(status))
            if notice:
                send_()
                notice = False
                scheduler.enter(3 * 60, 2, turn_notice)
        elif not str(status).startswith('5'):
            logging.info("!!!8 core 32G is available!!! status :" + str(status))
            if notice:
                send_()
                notice = False
                scheduler.enter(3 * 60, 2, turn_notice)
        else:
            logging.info("status: " + str(status) + " not available qwq")
    except Exception as e:
        logging.error(str(e))
        logging.error(r.text)
            
    scheduler.enter(3 * 60, 2, check_resource)


# 5min刷新一次token
def refresh_token():
    global refresh
    global authorization
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh,
        'client_id': 'dlp-train-front',
    }
    r = send_request({
        'method': 'post',
        'url': 'https://jiutian.10086.cn/auth/realms/TechnicalMiddlePlatform/protocol/openid-connect/token',
        'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
        'data': data,
        'verify': False
    })
    try:
        res = json.loads(r.text)
        refresh = res['refresh_token']
        authorization = 'Bearer ' + res['access_token']
        logging.info('Refresh token success.')
    except Exception as e:
        logging.error(str(e))
        logging.error(r.text)
        logging.error('Refresh token failed.')
        global fail_time
        fail_time += 1
        if fail_time >= 3:
            logging.error('Failed 3 times, get token.')
            refresh_()
    scheduler.enter(5 * 60, 1, refresh_token)


if __name__ == '__main__':
    scheduler.enter(1, 1, refresh_token)
    scheduler.enter(3, 2, check_resource)
    scheduler.run()
```

# 学习课程

学习课程获取豆子

```python
import requests
from time import sleep
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


account = '***'
pwd = '***'

def waitUntil(browser, by, value, time_limit):
    while True:
        try:
            t = WebDriverWait(browser, time_limit).until(
                EC.presence_of_element_located((by, value))
            )
            return t
        except:
            print(f"[-] Element not found {by}:{value}")
            browser.refresh()

def waitUntilNot(browser, by, value, time_limit):
    while True:
        try:
            WebDriverWait(browser, time_limit).until_not(
                EC.presence_of_element_located((by, value))
            )
            return
        except:
            print(f"[-] Element not found {by}:{value}")
            browser.refresh()

def courseLearn(courseId, num):
    time_limit = 120
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-gpu")
    options.add_argument("profile-directory=Profile 1")
    options.add_argument("enable-javascript")
    browser = webdriver.Edge('./msedgedriver.exe', options=options)
    url = f"https://jiutian.10086.cn/edu/web#/course/course-detail?num={num}&courseId={courseId}"
    # https://jiutian.10086.cn/edu/web#/course/course-detail?num={109}&courseId={2213}
    browser.get(url)
    waitUntil(browser, By.CLASS_NAME, "login-btn", time_limit).click()
    waitUntil(browser, By.XPATH, '//li[@class="login-box-select-item"]', time_limit).click()
    waitUntil(browser, By.ID, "username", time_limit).send_keys(account)
    waitUntil(browser, By.ID, "password", time_limit).send_keys(pwd)
    waitUntil(browser, By.ID, "kc-login", time_limit).click()
    print("[+] Login successful")
    while True:
        try:
            waitUntil(browser, By.XPATH, '//button[@class="button ant-btn ant-btn-primary"]', time_limit).click()
            print("Join button clicked")
            break
        except:
            print("[-] Join button not found")
            continue
    print("[+] Joining course")
    temp = waitUntil(browser, By.XPATH, '//ul[@class="contents-list"]', time_limit)
    lis = temp.find_elements(By.TAG_NAME, "li")
    courseNum = len(lis)
    for li in lis:
        try:
            # print(li.get_attribute("innerHTML"))
            temp = li.find_elements(By.TAG_NAME, "button")
            temp[3].click()
            # print(temp[3].get_attribute("innerHTML"))
            courseNum -= 1
            break
        except:
            courseNum -= 1
            continue
    else:
        print("[-] No joinable course found, waiting...")
        return
    print("[+] Course begin")
    if courseNum != 0:
        for _ in range(120):
            if (_ + 1) % 24 == 0:
                browser.refresh()
            try:
                sleep(5)
                temp = waitUntil(browser, By.XPATH, '//div[@class="ant-space ant-space-horizontal ant-space-align-center"]', time_limit)
                next_button = temp.find_elements(By.TAG_NAME, "button")[1]
                next_button.click()
                print(f"[+] Next course - 0")
                courseNum -= 1
                break
            except:
                continue
        else:
            print("[-] No next button click")
            return
    
        for _ in range(courseNum + 1):
            print(f"[+] Next course - {_ + 1}")
            for __ in range(10):
                try:
                    temp = waitUntil(browser, By.XPATH, '//div[@class="ant-space ant-space-horizontal ant-space-align-center"]', time_limit)
                    next_button = temp.find_elements(By.TAG_NAME, "button")[1]
                    next_button.click()
                    waitUntilNot(browser, By.XPATH, '//div[@class="ant-spin-text"]', time_limit)
                    break
                except Exception as e:
                    print("Error:", e)
                    sleep(10)
                    continue
            else:
                print("[-] No next button click")
                return
    temps = waitUntil(browser, By.XPATH, '//span[@class="ant-breadcrumb-link"]', time_limit)
    temps = temps.find_elements(By.XPATH, '//span[@class="ant-breadcrumb-link"]')
    for temp in temps:
        if "课程主页" in temp.get_attribute("innerHTML"):
            for _ in range(12):
                try:
                    temp.click()
                    break
                except:
                    sleep(5)
                    continue
            break
    else:
        print("No course home page found")
        return
    print("[+] Course finished")
    waitUntil(browser, By.XPATH, '//div[@class="receive-bean-icon cursor-hover"]', time_limit).click()
    print("[+] Beans received")
    sleep(3)


if __name__ == '__main__':
    url = "https://jiutian.10086.cn/edu/course_model/web/course/list"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = {
        "courseCateCode": "",
        "courseLevelCode": "",
        "courseStatus": "",
        "courseName": "",
        "pageNum": 1,
        "pageSize": 5 * 23,
        "requestId": "uuid"
    }
    response = requests.post(url, headers=headers, json=data)
    course = []
    if response.status_code == 200:
        data = response.json()
        course = data['body']['data']
    else:
        print("Failed to retrieve data from the URL.")
    
    for i in range(41, len(course)):
        item = course[i]
        print(f'{i = }: {item["courseName"]}, {item["courseId"]}, {item["courseStudyNum"]}')
        courseLearn(item["courseId"], item["courseStudyNum"])
```

