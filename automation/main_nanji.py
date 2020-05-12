#-*- coding: utf-8 -*-
'''
Created on 2019. 5. 28.

@author: user
'''

import configparser

from reservation_nanji import Reservation
from ast import literal_eval
from os.path import sys

config_section = ""

def main():
    config = getConfig()
    print("===================")
    print("## config section : {}".format(config_section))
    print("===================")
    reserv = Reservation(
        config_section
        ,config.getint(config_section, "loop_count")
        ,config.get(config_section, "login_id")
        ,config.get(config_section, "login_pw")
        ,config.get(config_section, "reserve_month")
        ,literal_eval(config.get(config_section, "reserve_days"))
        ,config.get(config_section, "area")
        ,literal_eval(config.get(config_section, "seat_nominees"))
        ,config.get(config_section, "percent_str")
        ,config.get(config_section, "birth_ymd")
        ,config.get(config_section, "bank_name")
        ,config.get(config_section, "user_agent")
        )
    reserv.process_reservation()
    del reserv
    
def getConfig():
    config = configparser.ConfigParser()
    config.read("reservation.conf", encoding="utf-8")
    print("config : {}".format(config))
    return config


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage : python main.py [Execute Envirenment - limjaeho/kimjoojin]')
        sys.exit(0)
    else:
        print('command line arguments : {}'.format(sys.argv))
        config_section = sys.argv[1]
    main()
