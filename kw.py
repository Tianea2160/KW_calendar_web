import logging

from selenium import webdriver
import time, re
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.select import Select


def login(browser):
    with open("secret.txt", "r") as f:
        line = f.readline()
        loginId = line.split(':')[-1].replace('\n', '').strip()
        line = f.readline()
        loginPwd = line.split(':')[-1].replace('\n', '').strip()

        # id 입력
        elem = browser.find_element_by_id("loginId")
        elem.clear()
        elem.send_keys(loginId)
        # pwd 입력
        elem = browser.find_element_by_id("loginPwd")
        elem.clear()
        elem.send_keys(loginPwd)
        browser.find_element_by_class_name("btn").click()


def kw_scraping():
    browser = webdriver.Chrome()
    delay = 0.5
    colors = ['#FF9900', '#FFFF99', '#CCFFCC', '#CCFFFF', '#99CCFF', '#CC99FF', '#FF99CC', '#FF99CC', '#666699',
              '#3366FF']

    with open("secret.txt", "r") as f:
        line = f.readline()
        loginId = line.split(':')[-1].replace('\n', '').strip()
        line = f.readline()
        loginPwd = line.split(':')[-1].replace('\n', '').strip()

    def check_exists_by_class():
        try:
            td = browser.find_element_by_tag_name("tbody").find_element_by_tag_name("td")
            if td.text == "출제된 레포트가 없습니다.":
                return True
        except NoSuchElementException:
            return True
        except StaleElementReferenceException:
            return True
        return False

    def login():
        # 학교 홈페이지 과제란 주소
        url = "https://klas.kw.ac.kr/std/lis/evltn/TaskStdPage.do"
        browser.get(url)

        # id 입력
        elem = browser.find_element_by_id("loginId")
        elem.clear()
        elem.send_keys(loginId)
        browser.implicitly_wait(delay)
        # pwd 입력
        elem = browser.find_element_by_id("loginPwd")
        elem.clear()
        elem.send_keys(loginPwd)
        time.sleep(delay)

        # login 버튼 누르기
        browser.find_element_by_class_name("btn").click()
        browser.implicitly_wait(delay)
        time.sleep(delay)

    login()

    # 과목 이름 select버튼을 control하는 부분
    try:
        browser.find_element_by_xpath("//*[@id='appSelectSubj']/div[2]/div/div[2]/select")
    except Exception as error:
        print(error)
        # 로그인을 실패하여 오류가 생길 때 다시 시도하는 코드

    elem = browser.find_element_by_xpath("//*[@id='appSelectSubj']/div[2]/div/div[2]/select")
    select = Select(elem)
    browser.implicitly_wait(delay)

    # 과제에 관한 정보를 담을 dict 생성
    kw_homework = {}
    subjectIndex = 0
    for i in select.options:
        # title
        select.select_by_visible_text(i.text)
        # table info print
        table = browser.find_element_by_class_name("AType")
        # check element is exist
        browser.implicitly_wait(delay)
        if check_exists_by_class():
            continue
        tbodys = table.find_elements_by_tag_name("tbody")

        browser.implicitly_wait(delay)
        kw_homework[i.text] = []
        for index, value in enumerate(tbodys):
            row = value.find_element_by_tag_name("tr")
            th = row.find_elements_by_tag_name("td")
            # 1 is title, index 2 is deadline
            temp = th[2].text
            split_str = temp.split(" ")
            startDate = split_str[0] + "T" + split_str[1]
            endDate = split_str[3] + "T" + split_str[4]
            kw_homework[i.text].append(th[1].text + "///" + startDate + "///" + endDate + "///" + colors[subjectIndex])
            # print(kw_homework[i.text])
            browser.implicitly_wait(delay)
        subjectIndex += 1
    browser.quit()
    return kw_homework


def goToUrl(url):
    browser = webdriver.Chrome()
    browser.get(url)
    try:
        login(browser)
    except Exception as error:
        return


def checkId():
    try:
        with open("secret.txt", "r") as f:
            loginId = f.readline()
            loginPwd = f.readline()
            # id 검사 -> 학번이 10자이고 숫자로 구성되어 있는지 확인
            studentNumCheck = re.compile(r'\d{10}')
            findId = studentNumCheck.search(loginId)
            if len(findId.group()) != 10:
                return False
    except Exception as error:
        print(error)
        return False
    return True