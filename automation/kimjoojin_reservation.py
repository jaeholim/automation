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

login_id = "shjcoa81"
login_pw = "joojin1129!"
reserve_date = {"15":"1박 2일", "22":"1박 2일", "29":"1박 2일"}
# reserve_date = {"27":"1박 2일", "19":"1박 2일"}
## J4, CAR-3, L4
seat_nominees = ["L5", "L6", "L7", "L8", "L-5", "L-6", "L-7", "L-8","L4", "L3", "L-4", "L-3", "J6", "J7", "J8","I1", "I2", "I3","I4", "H5", "H6", "H7", "E4", "E5"]
# seat_nominees = ["L4", "L3", "L-4", "L-3","J1", "J2", "J3", "H1", "H2","A3", "A4", "C4", "C5", "E4", "E5"]
percent_str = "50%"
birth_ymd = "810226"
bank_name = "신한은행"

select_month = "2019년 6월"


is_next_month = False


driver = webdriver.Chrome()
driver.maximize_window()
main_window_handler = driver.current_window_handle
popup_handler = None
# 로그인 처리
def login(uid, upw):
    driver.find_element_by_id("imgLogin").click()
    driver.find_element_by_id("UID").send_keys(uid)
    driver.find_element_by_id("PWD").send_keys(upw)
    driver.find_element_by_class_name('loginBtn').find_element_by_tag_name("button").click()
    return None

# popup handler 조회 
def get_popup_handler():
    popup_handler = None
    for win_handler in driver.window_handles:
        if win_handler != main_window_handler:
            popup_handler = win_handler
    return popup_handler
    

# 날짜 자리 선택
def date_seat_select(rd, rdur):
    is_complete = False
    # 날짜 선택
    print("캠핑 날짜  : {}, 캠필 기간 : {}".format(rd, rdur))
    date_link = driver.find_element_by_link_text(rd)
#     print("date_link element : {} - {}".format(date_link, type(date_link)))
    date_link.click()
    checkin_select = Select(driver.find_element_by_id("SelectCheckIn"))
    checkin_select.select_by_visible_text(rdur)
    
    # 자리 선택
    driver.switch_to.frame("ifrmSeat")
    for sn in seat_nominees:
        try:
            seat = driver.find_element_by_xpath("//*[contains(@title,'{}') and @class='stySeat']".format(sn))
            print("캠핑 자리 : {}".format(sn))
            seat.click()
            driver.find_element_by_class_name("btn_next_step").click()
            is_complete = True
            break
        except NoSuchElementException:
            continue
    return is_complete

# 가격 선택
def price_select():
    driver.switch_to.window(popup_handler)
    driver.switch_to.frame("ifrmBookStep")
    driver.find_element_by_xpath("//*[@id='PriceType' and contains(@pricegradename,'{}')]".format(percent_str)).click() 
    print("캠핑 할인율 : {}".format(percent_str))
    driver.find_element_by_id("NextStepImage").click()
    return None


# 정보 입력 및 결제 수단 
def input_payment_info():
    driver.find_element_by_id("YYMMDD").send_keys(birth_ymd)
    input_field = driver.find_element_by_xpath("//*[@id='Payment' and @kindofsettle='22004']")
    if not input_field.is_enabled():
        print("무통장 비활성화 되어 있음 : {}".format(input_field.is_enabled()))
        driver.execute_script('arguments[0].removeAttribute("disabled");', input_field)
    input_field.click()
    time.sleep(0.5)
    bank_select = Select(driver.find_element_by_id("BankCode"))
    bank_select.select_by_visible_text(bank_name)
    print("생년월일 : {}, 은행 : {}".format(birth_ymd, bank_name))
    driver.find_element_by_id("NextStepImage").click()
    return None
    
# 결제 완료
def payment_complete():
    driver.find_element_by_id("CancelAgree").click()
    driver.find_element_by_id("CancelAgree2").click()
    driver.find_element_by_id("NextStepImage").click()
    print("예약 완료 =========================================")
    return None
    

# ============================================================================================================        
#   main logic
# ============================================================================================================       
# 인터파크 티켓 페이지로 이동
driver.get("http://ticket.interpark.com/?smid1=header&smid2=ticket")
login(login_id, login_pw)
time.sleep(0.5)

driver.get("http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?GoodsCode=18007398")
# 예약 페이로 이동
for rd, rdur in reserve_date.items():
    
    booking_b = driver.find_element_by_class_name("btn_booking")
    booking_b.click()

    print("window handlers : {}".format(driver.window_handles))

    # 예약을 위한 popup        
    popup_handler = get_popup_handler()
    driver.switch_to.window(popup_handler)

    is_possible = False
    while not is_possible:
        print("is_possible = {}".format(is_possible))
        
        time.sleep(0.5)
        is_correct_month = False
        while not is_correct_month:
            # 다음달 선택
            if is_next_month:
                driver.find_element_by_class_name("btn_next").click()
            # 다음달 선택후 데이터를 바로 읽으면 데이터를 잘못읽어서 0.5초 쉼
            time.sleep(0.5)
            current_month = driver.find_element_by_xpath("//*[@id='BookingDateTime']/h3").text
            if current_month == select_month:
                is_correct_month = True
            print("month : {}, is_next_month : {}".format(current_month, is_correct_month))
            
        # 링크가 존재 하는지 확인
        possible_links = driver.find_elements_by_id("CellPlayDate")
        print("possible_links len : {}".format(len(possible_links)))
        
        # 링크가 존재 하면 원하는 날짜를 선택 
        if len(possible_links) > 0:
            # 예매가 가능
            is_possible = True
            # 날짜 자리 선택
            if date_seat_select(rd, rdur):
                # 가격 선택
                price_select()
                # 정보 입력 및 결제 수단 
                input_payment_info()
                # 결제 완료
                payment_complete()
            else:
                print("{} 자리가 하나도 없음".format(seat_nominees))
            driver.close()
            driver.switch_to.window(main_window_handler)
#             time.sleep(10)
        else:
            print("refrsh....................")
            driver.refresh()


        




time.sleep(10)




driver.close()

