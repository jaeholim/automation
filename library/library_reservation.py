#-*- coding: utf-8 -*-
'''
Created on 2019. 5. 28.

@author: user
'''
import time

from datetime import datetime
from os.path import sys
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException,\
    UnexpectedAlertPresentException, NoAlertPresentException

class Reservation:

    def __init__(self,
                 section,
                 loop_count,
                 login_id, login_pw, 
                 content_no, user_agent):
        self.section = section
        self.loop_count = loop_count
        self.login_id = login_id
        self.login_pw = login_pw
        self.content_no = content_no
        self.user_agent = user_agent
        
        print("Setting Data : \n{}".format(" \n".join(["<< {} = {} >>".format(mem_var, getattr(self, mem_var)) for mem_var in dir(self) if not mem_var.startswith('__') and not callable(getattr(self, mem_var))])))
        
        print("START...")
        options = webdriver.ChromeOptions()
#         options.add_argument('headless')
#         options.add_argument('window-size=1920x1080')
#         options.add_argument("disable-gpu")
        options.add_argument("user-agent=%s"%self.user_agent)
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.maximize_window()
        self.main_window_handler = self.driver.current_window_handle
        self.popup_handler = None

    def __del__(self):
        self.driver.close()
        print("END...")
        
    
    # 로그인 처리
    def login(self, uid, upw):
        self.driver.find_element_by_id("id").send_keys(uid)
        self.driver.find_element_by_id("pw").send_keys(upw)
        self.driver.find_element_by_xpath('//*[@id="loginForm"]/button').click()
        print("로그인 완료 : {}".format(uid))
        return None
    
    # popup handler 조회 
    def get_popup_handler(self):
        popup_handler = None
        for win_handler in self.driver.window_handles:
            if win_handler != self.main_window_handler:
                popup_handler = win_handler
        return popup_handler
        
    
    # 날짜 자리 선택
    def date_seat_select(self, rd, rdur):
        is_complete = False
        # 날짜 선택
        print("캠핑 날짜  : {}, 캠필 기간 : {}".format(rd, rdur))
        date_link = self.driver.find_element_by_link_text(rd)
    #     print("date_link element : {} - {}".format(date_link, type(date_link)))
        date_link.click()
        
        try:
            # 날짜 선택시 이미 예매 했다는 Alert이 뜨면서 에러 발생할 수 있음
            checkin_select = Select(self.driver.find_element_by_id("SelectCheckIn"))
            checkin_select.select_by_visible_text(rdur)
        except UnexpectedAlertPresentException:
            alert = self.driver.switch_to.alert
            print("이미 예매를 함 : {}".format(alert.text))
            alert.accept();
            return is_complete
        except:
            print("Exception : {}".format(sys.exc_info()[0]))
        
        
        # 자리 선택
        self.driver.switch_to.frame("ifrmSeat")
        for sn in self.seat_nominees:
            try:
                seat = self.driver.find_element_by_xpath("//*[contains(@title,'{}') and @class='stySeat']".format(sn))
                print("캠핑 자리 : {}".format(sn))
                seat.click()
                
#                 # 테스트용 코드 - 원하는 시간이 될때까지 기다림
#                  while time.gmtime().tm_sec != 55:
#                      print("기다림........")
#                      time.sleep(0.2)
                
                self.driver.find_element_by_class_name("btn_next_step").click()
                # "다음" 버튼 클릭시 Alert창이 발생하면 Accept 처리 하고 다음 자리로 넘어가도록 처리
                try:
                    alert = self.driver.switch_to.alert
                    print("Alert창이 뜸 : seat - {}, msg - {}".format(sn, alert.text))
                    alert.accept()
                    # 이미 선택된 자리를 다시 한번 클릭하여 선택 해제 함
                    seat = self.driver.find_element_by_xpath("//*[contains(@title,'{}') and @class='stySelectSeat']".format(sn))
                    seat.click()
                    continue
                except NoAlertPresentException:
                    print("자리가 정상적으로 선택됨 : {}".format(sn))
                
                is_complete = True
                break
            except NoSuchElementException:
                continue
        return is_complete
    
    # 가격 선택
    def price_select(self):
        self.driver.switch_to.window(self.popup_handler)
        self.driver.switch_to.frame("ifrmBookStep")
        self.driver.find_element_by_xpath("//*[@id='PriceType' and contains(@pricegradename,'{}')]".format(self.percent_str)).click() 
        print("캠핑 할인율 : {}".format(self.percent_str))
        self.driver.find_element_by_id("NextStepImage").click()
        return None
    
    
    # 정보 입력 및 결제 수단 
    def input_payment_info(self):
        self.driver.find_element_by_id("YYMMDD").send_keys(self.birth_ymd)
        input_field = self.driver.find_element_by_xpath("//*[@id='Payment' and @kindofsettle='22004']")
        if not input_field.is_enabled():
            print("무통장 비활성화 되어 있음 : {}".format(input_field.is_enabled()))
            self.driver.execute_script('arguments[0].removeAttribute("disabled");', input_field)
        input_field.click()
        time.sleep(0.5)
        bank_select = Select(self.driver.find_element_by_id("BankCode"))
        bank_select.select_by_visible_text(self.bank_name)
        print("생년월일 : {}, 은행 : {}".format(self.birth_ymd, self.bank_name))
        self.driver.find_element_by_id("NextStepImage").click()
        return None
        
    # 결제 완료
    def payment_complete(self):
        self.driver.find_element_by_id("CancelAgree").click()
        self.driver.find_element_by_id("CancelAgree2").click()
        self.driver.find_element_by_id("NextStepImage").click()
        print("예약 완료 =========================================")
        return None
    
    
    def process_reservation(self):
        # 인터파크 티켓 페이지로 이동
        self.driver.get("https://lib.ansan.go.kr/main.do")
        self.login(self.login_id, self.login_pw)
        time.sleep(0.2)
        
        
        idx = 1
        while self.loop_count <= 0 or ( self.loop_count > 0 and idx <= self.loop_count):
            print("=======================================================================")
            print("===== {}/{} 번째 시도 ".format(idx, "∞" if self.loop_count <= 0 else self.loop_count))
            print("=======================================================================")
            idx+=1
            
            self.driver.get('https://lib.ansan.go.kr/culturalclass.do?sitekey=5')
            
            try:
                ## 문화 강좌 데이터 확인 및 열기
                content_div = self.driver.find_element_by_xpath('//div[@class="pa30 t_center requContent_%d"]' % self.content_no)
                content_link = None
                try:
                    content_link = content_div.find_element_by_tag_name('a')
                except NoSuchElementException:
                    pass
                print(' content link elelment : {}'.format(content_link))
                if content_link is not None:
                    content_div.find_element_by_xpath('parent::div/preceding-sibling::div').click()
                    while not content_div.is_displayed():
                        time.sleep(0.5)
                    content_link.click()
                    while not self.driver.find_element_by_xpath('//div[@class="bx pa0 cultRequDiv_%d"]' % self.content_no).is_displayed():
                        time.sleep(0.5)
                    name_input = self.driver.find_element_by_id('name_%d' % self.content_no)
                    name_input.clear()
                    name_input.send_keys('임예은 외 3명')
                    
                    self.driver.find_element_by_xpath('//div[@class="pa30 t_center cultRequDiv_%d"]' % self.content_no).find_element_by_xpath('a[@class="btn lg blue"]').click()
                    
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    time.sleep(1)
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    print("등록 완료")
                    # 정보 입력
#                     time.sleep(30)
                    break;
            except Exception as e:
                print("예약 중 에러가 발생하여 다시 시작 : {}".format(e))
                # self.driver.switch_to.window(self.main_window_handler)
