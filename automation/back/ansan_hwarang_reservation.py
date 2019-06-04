#-*- coding: utf-8 -*-
'''
Created on 2019. 5. 28.

@author: user
'''
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class hwarangReservation:
    login_id = None
    login_pw = None
    # reserve_date = {"13":"1박 2일", "6":"1박 2일", "20":"1박 2일", "27":"1박 2일"}
    reserve_date = None
    ## J4, CAR-3, L4
    seat_nominees = None
    percent_str = None
    birth_ymd = None
    bank_name = None
    driver = None
    main_window_handler = None
    popup_handler = None

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.main_window_handler = self.driver.current_window_handle
        self.popup_handler = None
        
    def __del__(self):
        self.driver.close()
        
    # 로그인 처리
    def login(self,uid, upw):
        self.driver.find_element_by_id("imgLogin").click()
        self.driver.find_element_by_id("UID").send_keys(uid)
        self.driver.find_element_by_id("PWD").send_keys(upw)
        self.driver.find_element_by_class_name('loginBtn').find_element_by_tag_name("button").click()
        return None
    
    # popup handler 조회 
    def get_popup_handler(self):
        popup_handler = None
        for win_handler in self.driver.window_handles:
            if win_handler != self.main_window_handler:
                popup_handler = win_handler
        return popup_handler
        
    
    # 날짜 자리 선택
    def date_seat_select(self,rd, rdur):
        is_complete = False
        # 날짜 선택
        print("캠핑 날짜  : {}, 캠필 기간 : {}".format(rd, rdur))
        date_link = self.driver.find_element_by_link_text(rd)
    #     print("date_link element : {} - {}".format(date_link, type(date_link)))
        date_link.click()
        checkin_select = Select(self.driver.find_element_by_id("SelectCheckIn"))
        checkin_select.select_by_visible_text(rdur)
        
        # 자리 선택
        self.driver.switch_to.frame("ifrmSeat")
        for sn in self.seat_nominees:
            try:
                seat = self.driver.find_element_by_xpath("//*[contains(@title,'{}') and @class='stySeat']".format(sn))
                print("캠핑 자리 : {}".format(sn))
                seat.click()
                self.driver.find_element_by_class_name("btn_next_step").click()
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
        
    def reservation_processing(self):
        # ============================================================================================================        
        #   main logic
        # ============================================================================================================       
        # 인터파크 티켓 페이지로 이동
        self.driver.get("http://ticket.interpark.com/?smid1=header&smid2=ticket")
        self.login(self.login_id, self.login_pw)
        time.sleep(0.5)
        
        self.driver.get("http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?GoodsCode=18007398")
        # 예약 페이로 이동
        for rd, rdur in self.reserve_date.items():
            
            booking_b = self.driver.find_element_by_class_name("btn_booking")
            booking_b.click()
        
            print("window handlers : {}".format(self.driver.window_handles))
        
            # 예약을 위한 popup        
            self.popup_handler = self.get_popup_handler()
            self.driver.switch_to.window(self.popup_handler)
        
            is_possible = False
            while not is_possible:
                print("is_possible = {}".format(is_possible))
                time.sleep(0.5)
                # 다음달 선택
                self.driver.find_element_by_class_name("btn_next").click()
                # 다음달 선택후 데이터를 바로 읽으면 데이터를 잘못읽어서 0.5초 쉼
                time.sleep(0.5)
                print("month : {}".format(self.driver.find_element_by_xpath("//*[@id='BookingDateTime']/h3").text))
                
                # 링크가 존재 하는지 확인
                possible_links = self.driver.find_elements_by_id("CellPlayDate")
                print("possible_links len : {}".format(len(possible_links)))
                
                # 링크가 존재 하면 원하는 날짜를 선택 
                if len(possible_links) > 0:
                    # 예매가 가능
                    is_possible = True
                    # 날짜 자리 선택
                    if self.date_seat_select(rd, rdur):
                        # 가격 선택
                        self.price_select()
                        # 정보 입력 및 결제 수단 
                        self.input_payment_info()
                        # 결제 완료
                        self.payment_complete()
                    else:
                        print("{} 자리가 하나도 없음".format(self.seat_nominees))
                    self.driver.close()
                    self.driver.switch_to.window(self.main_window_handler)
        #             time.sleep(10)
                else:
                    print("refrsh....................")
                    self.driver.refresh()
    
   





