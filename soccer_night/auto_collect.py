# -*- coding: utf-8 -*-

class AutoCollector:
    def __init__(self, driver, wait, option):
#        available options..
#        cleaning policy (which players to practice or sell?)
#        buying policy (only 9000, only 1000, only 9000 when live card season, etc..)
        self.option = options
        self.driver = driver
        self.wait = wait

    def buy_until_possible(self):
#        return with following reasons ..
#        entry full
#        lack of GP
#        unknown error
        pass

    def clean_up_entry(self):
#        return when cleaning is done
#        sell or practice as possible
        pass

    def practice(self, growing_player, victims):
        pass

    def sell(self, targets):
        pass

