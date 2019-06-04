#-*- coding: utf-8 -*-
'''
Created on 2019. 5. 28.

@author: user
'''
from ansan_hwarang_reservation import hwarangReservation

hr = hwarangReservation()


hr.login_id = "shjcoa81"
hr.login_pw = "joojin1129!"
# reserve_date = {"13":"1박 2일", "6":"1박 2일", "20":"1박 2일", "27":"1박 2일"}
hr.reserve_date = {"25":"1박 2일", "12":"1박 2일"}
## J4, CAR-3, L4
hr.seat_nominees = ["L4", "L3", "L-4", "L-3", "J1", "J2", "j3", "H1", "H2","E5", "E1", "E2", "E3"]
hr.percent_str = "50%"
hr.birth_ymd = "820106"
hr.bank_name = "신한은행"

hr.reservation_processing()

del hr