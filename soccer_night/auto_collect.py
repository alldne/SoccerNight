#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

class AutoCollector:
    BUTTON_1000_XPATH = '//li[@data-prodid="prplr_basic_lv1"]'
    BUTTON_AUTO_BUY_ID = 'auto_buy_button'
    LINK_TEXT_NOT_ENOUGH_SQUAD = '선수관리로 이동'
    POPUP_CONFIRM_ID = 'a_popup_ok'
    ROW_UNLOCK_CSS ='span.unlock'
    CONFIG_PATH = '../config.json'

    def __init__(self, driver, wait, option=None):
        if os.path.isfile(self.CONFIG_PATH):
            import simplejson as json
            self.config = json.loads(open(self.CONFIG_PATH).read())
            self.collectee = self.config['auto-collect']['collectee']
            for s in self.collectee:
                print s
#        available options..
#        cleaning policy (which players to practice or sell?)
#        buying policy (only 9000, only 1000, only 9000 when live card season, etc..)
        self.option = option or {}
        if not self.option.has_key('buying_policy'):
            self.option['buying_policy'] = '1000only';
        self.driver = driver
        self.wait = wait

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
        if hasattr(self, 'driver'):
            self.driver.quit()

    def buy_until_possible(self):
        self.driver.get("http://fd.naver.com/gmc/main#recommendation")
        time.sleep(2)
        if self.option['buying_policy'] == '1000only':
            elem = self.driver.find_element_by_xpath(self.BUTTON_1000_XPATH)
        elem.click()

        time.sleep(1)

        elem = self.driver.find_element_by_id(self.BUTTON_AUTO_BUY_ID)
        elem.click()

        while True:
            time.sleep(1)
            print 1
            try:
                elem = self.driver.find_element_by_id(self.POPUP_CONFIRM_ID)
            except Exception as e:
                print e
                pass
            else:
                elem.click()
#               entry full
                break


#        return with following reasons ..
#        entry full
#        lack of GP
#        unknown error
        pass

    def clean_up_entry(self):
        self.driver.get('http://fd.naver.com/gmc/main#manageplayer')
        time.sleep(2)
        elems = self.driver.find_elements_by_css_selector(self.ROW_UNLOCK_CSS)
#        print len(elems)

        config_dirty = False

        former_input = ''
        for lock_icon in elems:
            tr = lock_icon.find_element_by_xpath('../..')
            team_name = tr.find_element_by_css_selector('td._mteamNo span').get_attribute('innerHTML')
            player_name = tr.find_element_by_css_selector('td._name strong').get_attribute('innerHTML')
            level = tr.find_element_by_css_selector('td._lv span').get_attribute('innerHTML')

            is_level_over_3 = int(level.split(' ')[0]) > 3
#            print '[', team_name, ']'
#            print '[', player_name, ']'
#            print '[', level, ']'
            if team_name in self.config['auto-collect']['collectee']:
                print '\tCOLLECT [%s] %s(lv %s)'%(team_name, player_name, level)
                self.driver.execute_script('console.log(arguments); arguments[0].click();', tr.find_element_by_css_selector('td._prttYn span.unlock'))
            elif not is_level_over_3 and team_name in self.config['auto-collect']['non-collectee']:
                print 'pass [%s] %s(lv %s)'%(team_name, player_name, level)
            else:
                y_or_n = ''
                while y_or_n.lower() not in ('y', 'yt', 'n', 'nt'):
                    y_or_n = raw_input('collect? [%s] %s(lv %s) [y/n]'%(team_name.encode('utf8'), player_name.encode('utf8'), level.encode('utf8')))

                    if y_or_n == '' and former_input != '':
                        y_or_n = former_input
                        print y_or_n

                if y_or_n == 'yt':
                    self.config['auto-collect']['collectee'] += [team_name]
                    config_dirty = True

                if y_or_n == 'nt':
                    self.config['auto-collect']['non-collectee'] += [team_name]
                    config_dirty = True

                if y_or_n in ('y', 'yt'):
                    print '\tCOLLECT [%s] %s(lv %s)'%(team_name, player_name, level)
                    self.driver.execute_script('console.log(arguments); arguments[0].click();', tr.find_element_by_css_selector('td._prttYn span.unlock'))

                former_input = y_or_n
#            print tr.find_element_by_css_selector('td._name strong').get_attribute('innerHTML'),
#            print tr.find_element_by_css_selector('td._curPos span').get_attribute('innerHTML'),
#            print tr.find_element_by_css_selector('td._lv span').get_attribute('innerHTML'),
#            print tr.find_element_by_css_selector('td._mteamNo span').get_attribute('innerHTML')

#        return when cleaning is done
#        sell or practice as possible
        if config_dirty:
            import simplejson as json
            f = open(self.CONFIG_PATH, 'w')
            f.write(json.dumps(self.config, ensure_ascii=False, indent=4*' ').encode('utf8'))
            f.close()
        pass

    def practice(self, growing_player, victims):
        pass

    def sell(self, targets):
        pass

    def login(self, id, pw):
        self.driver.get("http://fd.naver.com/gmc/main#home")
        elem = self.driver.find_element_by_id("id")
        elem.send_keys(id)
        elem = self.driver.find_element_by_id("pw")
        elem.send_keys(pw)
        elem.send_keys(Keys.ENTER)

if __name__ == '__main__':
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from getpass import getpass
    import time

    EXPLICITLY_WAIT_SECONDS = 5

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, EXPLICITLY_WAIT_SECONDS)
    with AutoCollector(driver, wait) as a:
        id = raw_input("Enter id: ")
        pw = getpass()
        a.login(id, pw)
        time.sleep(3)
        a.buy_until_possible()
        time.sleep(3)
        a.clean_up_entry()


        pass
