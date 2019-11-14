#-*- coding: utf-8 -*-
'''
Created on 2019. 5. 28.

@author: user
'''

import configparser

from library_reservation import Reservation
from ast import literal_eval
from os.path import sys

config_section = "library"

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
        ,config.getint(config_section, "content_no")
        ,config.get(config_section, "user_agent")
        )
    reserv.process_reservation()
    del reserv
    
def getConfig():
    config = configparser.ConfigParser()
    config.read("library.conf", encoding="utf-8")
    print("config : {}".format(config))
    return config


if __name__ == "__main__":
    main()
