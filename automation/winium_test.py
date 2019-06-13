from selenium import webdriver
import time, sys

# put it in setUp
print('start ....')
driver = webdriver.Remote(command_executor='http://localhost:9999',
                               desired_capabilities={'app': 'C:\Windows\system32\calc.exe'
                                                     , 'debugConnectToRunningApp' : 'false'
                                                     , 'launchDelay' : '2000'})

print('driver:%s' % driver)
# es = driver.find_elements_by_xpath('/node()')
# print('elements:{} - {}'.format(len(es), es))
# for e in es:
#     print('element : {}'.format(e.get_attribute('Name')))

# win = driver.find_element_by_name('계산기')
win = driver.find_element_by_class_name('CalcFrame')
print('win:%s' % win.get_attribute('Name'))
# print('win.parent:{}'.format(win._parent))
# print('win:%s' % dir(win))

# es = win.find_elements_by_xpath('/계산기/node()/node()')
# print('elements:{} - {}'.format(len(es), es))
# for e in es:
#     print('element : {} - {}'.format(e.get_attribute('Id'), e.get_attribute('Name')))

# 
# menu = win.find_element_by_name('응용 프로그램')
# print('menu:%s' % menu)
# 
# view = menu.find_element_by_name('보기(V)')
# print('view:%s' % view)
# 
# time.sleep(2)
# view.click()
# time.sleep(2)
# view.find_element_by_name('공학용(S)    Alt+2').click()

# time.sleep(2)
win.find_element_by_name('1').click()
win.find_element_by_name('0').click()
win.find_element_by_name('0').click()
win.find_element_by_name('더하기').click()
win.find_element_by_name('2').click()
win.find_element_by_name('같음').click()

view = win.find_element_by_name('보기(V)')
view.click()
view.find_element_by_name('공학용(S)').click()

time.sleep(2)

win.find_element_by_name('닫기').click()

print("==============")

mw_btn = driver.find_element_by_name('MirageWorks2 시작')
print('mw_btn : %s' % mw_btn)
mw_btn.click()

mw_win = None
while mw_win is None:
    try:
        driver.find_element_by_name('MirageWorks2')
    except:
         print("Exception : {}".format(sys.exc_info()[0]))
    time.sleep(0.5)
     
mw_win.find_element_by_xpath('./*[6]/*[1]/*[4]').send_keys('aaaaaaaaaaa')

time.sleep(2)

# QTool
driver.close()
print('end ....')

