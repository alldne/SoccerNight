#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def log(str):
    print bcolors.OKGREEN, str, bcolors.ENDC

def beep(sleep_seconds=0):
    if time:
        time.sleep(sleep_seconds)
    print '\a',

class AutoCollector:
    class NoPlayersLeft(Exception):
        pass
    class ReachedMinimumGP(Exception):
        pass
    class LevelUp(Exception):
        pass
    class PolicyExpired(Exception):
        pass

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
            print 'Collect following teams..'
            for s in self.collectee:
                print '\t', s
            print 'until GP %d'%(self.config['auto-collect']['minimum-gp'],)
            if self.config['auto-collect']['auto-grind']:
                print 'auto grind is ON'
            else:
                print 'auto grind is OFF'
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
        log('buy_until_possible')
        self.driver.get("http://fd.naver.com/gmc/main#recommendation")
        log('go to store')
        time.sleep(2)
        if self.option['buying_policy'] == '1000only':
            elem = self.driver.find_element_by_xpath(self.BUTTON_1000_XPATH)
        elem.click()
        log('buy')

        time.sleep(1)

        elem = self.driver.find_element_by_id(self.BUTTON_AUTO_BUY_ID)
        elem.click()

        while True:
            time.sleep(1)
            try:
                remain_gp = int(self.driver.execute_script("return $('span#my_gp')[0].innerHTML").replace(',', ''))
                if self.config['auto-collect']['minimum-gp'] > remain_gp:
                    raise AutoCollector.ReachedMinimumGP
                elem = self.driver.find_element_by_id(self.POPUP_CONFIRM_ID)
            except AutoCollector.ReachedMinimumGP as e:
                raise e
            except Exception as e:
                pass
            else:
                elem.click()
                log('entry full')
#               entry full
                break


#        return with following reasons ..
#        entry full
# TODO:        lack of GP
#        unknown error
        pass

    def clean_up_entry(self):
        self.driver.get('http://fd.naver.com/gmc/main#manageplayer')
        log('go to manage player')
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
            if team_name in self.config['auto-collect']['collectee']:
                print bcolors.OKBLUE, '\tCOLLECT [%s] %s(lv %s)'%(team_name, player_name, level), bcolors.ENDC
                self.driver.execute_script('arguments[0].click();', tr.find_element_by_css_selector('td._prttYn span.unlock'))
            elif not is_level_over_3 and team_name in self.config['auto-collect']['non-collectee']:
                print 'pass [%s] %s(lv %s)'%(team_name, player_name, level)
            else:
                y_or_n = ''
                while y_or_n.lower() not in ('y', 'yt', 'n', 'nt'):
                    if is_level_over_3:
                        print bcolors.HEADER
                    beep()
                    y_or_n = raw_input('collect? [%s] %s(lv %s) [y/n]'%(team_name.encode('utf8'), player_name.encode('utf8'), level.encode('utf8')))

                    if is_level_over_3:
                        print bcolors.ENDC

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

#        return when cleaning is done
#        sell or practice as possible
        if config_dirty:
            import simplejson as json
            f = open(self.CONFIG_PATH, 'w')
            f.write(json.dumps(self.config, ensure_ascii=False, indent=4*' ').encode('utf8'))
            f.close()
        pass

    def practice_a_player(self, policy):
        log('practice player %s'%(policy['name'],))
        growing_player = policy['name']
        target_level = policy.has_key('target-level') and policy['target-level'] or 8
        victim_positions = policy.has_key('position-to-consume') and policy['position-to-consume'] or []
        victim_positions = map(lambda s: s.lower(), victim_positions)
        growth_type = policy.has_key('growth-type') and policy['growth-type'] or ''

        position_map = {
            'fw': ['st', 'lw', 'rw'],
            'mf': ['lm', 'rm', 'cam', 'cm', 'cdm'],
            'df': ['lb', 'rb', 'cb']
        }

        for p in victim_positions[:]:
            if position_map.has_key(p):
                victim_positions.pop(victim_positions.index(p))
                victim_positions += position_map[p]

        self.driver.get('http://fd.naver.com/gmc/main#partner')
        time.sleep(3)

        if self.driver.execute_script("return $('div.lv_bonus_up')"):
            raise AutoCollector.LevelUp

        elems = self.driver.execute_script("return $('div.card:contains(%s)');"%(growing_player,))
        if len(elems) > 1:
            levels = [int(self.driver.execute_script("return $(arguments[0]).find('span.level')[0].className", x).split(' ')[1].split('_')[0][2:]) for x in elems]
            target_index = levels.index(max(levels))
            elem = elems[target_index]
        else:
            elem = self.driver.execute_script("return $('div.card:contains(%s)')[0];"%(growing_player,))

        if elem is None:
            print "Can't find a player", growing_player
            return
        level = self.driver.execute_script("return $(arguments[0]).find('span.level')[0].className", elem)
        level = int(level.split(' ')[1].split('_')[0][2:])


        self.driver.execute_script("arguments[0].click();", elem)
        time.sleep(2)

        percentage = self.driver.execute_script("return $('span.graph_l')[0].style.width;")
        percentage = float(percentage.replace('%', '')) / 100.0

        if level + percentage >= target_level:
            # TODO: print player info
            raise AutoCollector.PolicyExpired

        if growth_type:
            growth = self.driver.execute_script("return $('dd#grow a.p_select:contains(%s)')[0];"%(growth_type.upper(),))
            if growth is not None:
                self.driver.execute_script("arguments[0].click();", growth)
                print 'growth type is set to', growth_type
                time.sleep(1)
            else:
                print 'growth type element is None'

        while True:
            victims = self.get_unlock_players_in_practice(positions=victim_positions)
            if not victims:
                raise AutoCollector.NoPlayersLeft

            for p in victims:
                self.driver.execute_script('arguments[0].click();', p)
                print self.player_description_from_div_photo(p)
                time.sleep(1)


            grind = self.config['auto-collect']['auto-grind']
            if not grind:
                beep()
                confirm = raw_input('grind above players? [Y/n]')
                if confirm == '':
                    confirm = 'y'

                if confirm and confirm.lower() == 'y':
                    grind = True

            if grind:
                self.driver.execute_script("$('a#trainingButton')[0].click()")
                time.sleep(0.5)
                self.driver.execute_script("$('a#a_popup_ok')[0].click()")
                time.sleep(2*len(victims))
                percentage = self.driver.execute_script("return $('span.graph_l')[0].style.width;")
                percentage = float(percentage.replace('%', '')) / 100.0
                print 'level %f'%(level + percentage,)
                if self.driver.execute_script("return $('div.lv_bonus_up')"):
                    raise AutoCollector.LevelUp

                if level + percentage > target_level:
                    raise AutoCollector.PolicyExpired
            else:
                break

    def get_unlock_players_in_practice(self, positions=[], minimum_level=3):
        # ensure self.driver.get('http://fd.naver.com/gmc/main#partner')
        players = []
        elems = self.driver.execute_script("return $('div.photo:has(span.unlock)')")
        if not elems:
            raise AutoCollector.NoPlayersLeft

        for p in elems:
            position = self.driver.execute_script("return $(arguments[0]).find('span.position')[0].className", p)
            position = position.split(' ')[1].split('_')[0]
            level = self.driver.execute_script("return $(arguments[0]).find('span.level')[0].className", p)
            level = int(level.split(' ')[1].split('_')[0][2:])
            if level >= minimum_level:
                if positions and position not in positions:
                    continue
                players += [p]
                if len(players) == 5:
                    return players
        return players


    def sell(self, targets):
        pass

    def practice(self):
        log('practice')
        growth_policy = self.config['auto-collect']['growth-policy']
        policies_copy = growth_policy[:]
        config_dirty = False
        for p in growth_policy:
            try:
                self.practice_a_player(p)

            except AutoCollector.PolicyExpired:
                print 'Policy expired. Remove it from config.json.'
                policies_copy.remove(p)
                config_dirty = True

            except AutoCollector.NoPlayersLeft as e:
                print 'No players for %s to consume'%(p['name'],)
            except AutoCollector.LevelUp as e:
                beep()
                beep(0.2)
                beep(0.2)
                beep(0.2)
                beep(0.2)
                log("Congratulation! It's your turn. Press any key after finished your job.")
                raw_input()
                while self.driver.execute_script("return $('div.lv_bonus_up')"):
                    log("Something wrong? Press any key after finished your job.")
                    raw_input()
                log('Good job!')

        if config_dirty:
            self.config['auto-collect']['growth-policy'] = policies_copy
            import simplejson as json
            f = open(self.CONFIG_PATH, 'w')
            f.write(json.dumps(self.config, ensure_ascii=False, indent=4*' ').encode('utf8'))
            f.close()

        self.sell_all()

    def sell_all(self):
        log('sell all')
        self.driver.get('http://fd.naver.com/gmc/main#manageplayer')
        log('go to manage player')
        time.sleep(3)
        self.driver.execute_script("$('a#a_select_all')[0].click()")
        time.sleep(1)
        if self.driver.execute_script("return $('a#a_release_btn.off')"):
            return
        self.driver.execute_script("$('a#a_release_btn')[0].click()")
        time.sleep(1)
        self.driver.execute_script("$('a#a_popup_ok')[0].click()")
        time.sleep(1)
        self.driver.execute_script("$('a#a_popup_ok')[0].click()")
        time.sleep(3)

    def login(self, id, pw):
        self.driver.get("http://fd.naver.com/gmc/main#home")
        elem = self.driver.find_element_by_id("id")
        elem.send_keys(id)
        elem = self.driver.find_element_by_id("pw")
        elem.send_keys(pw)
        elem.send_keys(Keys.ENTER)

    def player_description_from_div_photo(self, div):
        position = self.driver.execute_script("return $(arguments[0]).find('span.position')[0].className", div)
        position = position.split(' ')[1].split('_')[0]
        level = self.driver.execute_script("return $(arguments[0]).find('span.level')[0].className", div)
        level = level.split(' ')[1].split('_')[0][2:]
        name = self.driver.execute_script("return $(arguments[0].parentElement).find('div.name_area div.name')[0].innerHTML", div)
        return position.upper() + ' ' + name + ' (lv%s)'%level

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
        time.sleep(3)
        try:
            while True:
                a.buy_until_possible()
                time.sleep(3)
                a.clean_up_entry()
                time.sleep(3)
                a.practice()
        except AutoCollector.ReachedMinimumGP:
            print 'Reached minimum GP.. End'
