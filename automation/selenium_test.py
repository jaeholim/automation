#-*- coding: utf-8 -*-
'''
Created on 2019. 5. 28.

@author: user
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from selenium.common.exceptions import NoSuchElementException


driver = webdriver.Chrome()
driver.maximize_window()
driver.get("http://ticket.interpark.com/?smid1=header&smid2=ticket")

# 로그인 처리
driver.find_element_by_id("imgLogin").click()

driver.find_element_by_id("UID").send_keys("hahajjang03")
driver.find_element_by_id("PWD").send_keys("navyblue03")
driver.find_element_by_class_name('loginBtn').find_element_by_tag_name("button").click()

time.sleep(2)

driver.get("http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?GoodsCode=18007398")

booking_b = driver.find_element_by_class_name("btn_booking")
booking_b.click()

print("window handlers : {}".format(driver.window_handles))
popup_handler = None
for win_handler in driver.window_handles:
    if win_handler != driver.current_window_handle:
        popup_handler = win_handler

# 예약을 위한 popup        
driver.switch_to.window(popup_handler)

# 예약 날짜 선택 
# 다음달 선택
# driver.find_element_by_class_name("btn_next").click()

# 날짜에 링크가 없는 경우에는 selenium.common.exceptions.NoSuchElementException 발생

reserve_date = [{"25":"1박 2일"}, {"11":"1박 2일"}, {"20":"1박 2일"}, {"27":"1박 2일"}]

is_pass = False
while not is_pass:
    print("bbbbbbbb")
    for rd_dict in reserve_date:
        print("aaaaaaaaaaaaa")
        rd_key, rd_value = rd_dict.items()[0]
        print("rd_key = {}, rd_value = {}".format(rd_key, rd_value))
        try:
            date_link = driver.find_element_by_link_text(rd_key)
            print("date_link element : {} - {}".format(date_link, date_link.tag_name))
            if date_link.tag_name == "td":
                break
            date_link.click()
        except NoSuchElementException:
            break
        # 예매가 가능
#         is_pass = True
        checkin_select = Select(driver.find_element_by_id("SelectCheckIn"))
        checkin_select.select_by_visible_text(rd_value)
        
    # 예매가 불가능한 날짜인 경우 - 날짜에 링크정보가 없음
    if not is_pass:
        driver.refresh()
        

# 자리 선택
driver.switch_to.frame("ifrmSeat")
seat_nominees = ["J4", "J5", "K4"]
for sn in seat_nominees:
    try:
        seat = driver.find_element_by_xpath("//*[@title='[오토캠핑사이트] -{}' and @class='stySeat']".format(sn))
        print("seat element : {}".format(seat))
        seat.click()
    except NoSuchElementException:
        continue
        
# driver.find_element_by_class_name("btn_next_step").click()



time.sleep(10)




driver.close()

