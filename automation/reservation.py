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
                 reserve_month, reserve_days, seat_nominees,
                 percent_str, birth_ymd, bank_name, user_agent):
        self.section = section
        self.loop_count = loop_count
        self.login_id = login_id
        self.login_pw = login_pw
        self.reserve_month = reserve_month
        self.reserve_date = datetime.strptime(self.reserve_month, "%Y년 %m월")
        self.reserve_days = reserve_days
        self.seat_nominees = seat_nominees
        self.percent_str = percent_str
        self.birth_ymd = birth_ymd
        self.bank_name = bank_name
        self.user_agent = user_agent
        print("Setting Data : \n{}".format(" \n".join(["<< {} = {} >>".format(mem_var, getattr(self, mem_var)) for mem_var in dir(self) if not mem_var.startswith('__') and not callable(getattr(self, mem_var))])))
        
        print("START...")
        options = webdriver.ChromeOptions()
#         options.add_argument('headless')
#         options.add_argument('window-size=1920x1080')
#         options.add_argument("disable-gpu")
        options.add_argument("user-agent=%s"%self.user_agent)
        self.driver = webdriver.Chrome(executable_path=r"C:\Users\user\IdeaProjects\automation\venv\webdrive\chromedriver.exe",chrome_options=options)
        self.driver.maximize_window()
        self.main_window_handler = self.driver.current_window_handle
        self.popup_handler = None

    def __del__(self):
        self.driver.close()
        print("END...")
        
    
    # 로그인 처리
    def login(self, uid, upw):
        self.driver.find_element_by_id("imgLogin").click()
        iframe = self.driver.find_element_by_xpath("//iframe[@title='login']")
        self.driver.switch_to_frame(iframe)
        self.driver.find_element_by_id("userId").send_keys(uid)
        self.driver.find_element_by_id("userPwd").send_keys(upw)
        self.driver.find_element_by_id('btn_login').click()
        self.driver.switch_to.window(self.main_window_handler)
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
        self.driver.get("http://ticket.interpark.com/?smid1=header&smid2=ticket")
        self.login(self.login_id, self.login_pw)
        time.sleep(0.2)
        
            
#         ## 검색하여 원하는 달을 예매 할 수 있는 링크 클릭
#         self.driver.get("http://ticket.interpark.com/search/ticket.asp?search=%uC548%uC0B0%uD654%uB791%uC624%uD1A0%uCEA0%uD551%uC7A5")
# #         self.driver.get("http://ticket.interpark.com/search/ticket.asp?search=%uC548%uC0B0%20%uD654%uB791%uC624%uD1A0%uCEA0%uD551%uC7A5%20%285%uC6D4%7E%29")
#
#         # 예약 페이로 이동
#         if self.driver.find_element_by_id("tickettype1_result").is_displayed():
#             self.driver.find_element_by_xpath('//*[@id="tickettype1_result"]/div/div/div[3]/a[1]/img').click()
#         else:
#             info_dates = self.driver.find_elements_by_xpath("//*[@id='play_list']/*/td[@class='info_Date']")
#             idx = 1
#             for info_date in info_dates:
#                 print("Row Num : {}, available date : {}".format(idx, info_date.text))
#                 sdate, edate = info_date.text.split("~")
#                 if datetime.strptime(sdate.strip(), "%Y.%m.%d") <= self.reserve_date and self.reserve_date <= datetime.strptime(edate.strip(), "%Y.%m.%d"):
#                     self.driver.find_element_by_xpath("//*[@id='play_list']/tr[{}]/td[@class='btnArea']/a[1]".format(idx)).click()
#                     break
#                 idx+=1


        self.driver.get("https://tickets.interpark.com/goods/20004246")

        # 테스트용 코드 - 원하는 시간이 될때까지 기다림
        wait_datetime = datetime.strptime("2021-05-21 23:59:50", "%Y-%m-%d %H:%M:%S")
        # wait_datetime = datetime.strptime("2021-05-21 16:37:50", "%Y-%m-%d %H:%M:%S")
        refresh_idx = 1
        while datetime.now() <= wait_datetime:
            print("{} - 기다림........{} - {}".format(self.login_id, datetime.now(), wait_datetime))
            if refresh_idx%10 == 0: 
                self.driver.execute_script("location.reload()")
            refresh_idx += 1
            time.sleep(1)

        # 예매 페이지를 여러번 재시도 할 수 있도록 처리 
        idx = 1
        end_datetime = datetime.strptime("2021-05-22 01:00:00", "%Y-%m-%d %H:%M:%S")
        # end_datetime = datetime.strptime("2021-05-21 16:38:00", "%Y-%m-%d %H:%M:%S")
        while self.loop_count <= 0 or ( self.loop_count > 0 and idx <= self.loop_count):
            if datetime.now() > end_datetime:
                print("{} - 시간이 되어 자동 종료........{} - {}".format(self.login_id, datetime.now(), end_datetime))
                break;

            print("=======================================================================")
            print("===== {} - {}/{} 번째 시도 ".format(self.login_id, idx, "∞" if self.loop_count <= 0 else self.loop_count))
            print("=======================================================================")
            idx+=1       

            for rd, rdur in self.reserve_days.items():
                print("-----------------------------------------------------------------------")
                try:
                    booking_b = self.driver.find_element_by_class_name("sideBtnWrap").find_element_by_tag_name("a");
                except Exception:
                    print("예매 버튼이 활성화 되지 않음...")
                    self.driver.switch_to.window(self.main_window_handler)
                    print("refrsh....................")
                    self.driver.refresh()
                    time.sleep(0.5)                    
                    continue
            
                booking_b.click()
            
                print("window handlers : {}".format(self.driver.window_handles))
            
                try:
                    # 예약을 위한 popup        
                    self.popup_handler = self.get_popup_handler()
                    self.driver.switch_to.window(self.popup_handler)

                    # 팝업이 활성화 되기 전에
                    time.sleep(0.2)

                    print("BookNotice display = {}".format(self.driver.find_element_by_id("divBookNotice")))

                    if self.driver.find_element_by_id("divBookNotice").is_displayed():
                        self.driver.find_element_by_id("divBookNotice").find_element_by_class_name("btn02").click()

                    is_possible = False
                    while not is_possible:
                        print("is_possible = {}".format(is_possible))
                       
                        # time.sleep(0.2)
                        is_correct_month = False
                        while not is_correct_month:
                            # current_month = self.driver.find_element_by_xpath("//*[@id='BookingDateTime']/h3").text
                            current_month = self.driver.find_element_by_id("BookingDateTime").find_element_by_tag_name("h3").text
                            if current_month == self.reserve_month:
                                is_correct_month = True
                            else:
                                # 다음달 선택
                                self.driver.find_element_by_class_name("btn_next").click()
                                # 다음달 선택후 데이터를 바로 읽으면 데이터를 잘못읽어서 0.5초 쉼
                                time.sleep(0.5)
                            print("month : {}, is_correct_month : {}".format(current_month, is_correct_month))            
                            
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
                                time.sleep(0.5)    
                                # 결제 완료
                                self.payment_complete()
                                time.sleep(0.5)
                            else:
                                print("{} 자리가 하나도 없거나 이미 예를 했음".format(self.seat_nominees))
                            time.sleep(1)    
                            # popup을 닫고 예매하기 버튼을 다시 클릭하기 위해 메인 윈도우로 이동함
                            self.driver.close()
                            self.driver.switch_to.window(self.main_window_handler)
                        else:
                            print("refrsh....................")
                            self.driver.refresh()
                except Exception as e:
                    print("예매 중 에러 발생 하여 팝업창 부터 다시 시작... : {}".format(e))
                    try:
                        self.driver.close()
                    except Exception:
                        print('[예외]...이미 팝업은 닫혀 있음 ')
                    self.driver.switch_to.window(self.main_window_handler)
