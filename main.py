# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import urllib


class element_has_css_class(object):
  """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, locator, css_class):
    self.locator = locator
    self.css_class = css_class

  def __call__(self, driver):
    element = driver.find_element(*self.locator)   # Finding the referenced element
    if self.css_class in element.get_attribute("class"):
        return element
    else:
        return False


webDriverName = 'Safari'
acceptableWebDriverNames = ('Chrome', 'Safari', 'Firefox', 'Ie', 'Edge')
webDriverToUse = getattr(webdriver, webDriverName)
SoundTitleMap = {}
SoundSrcMap = {}


if len(sys.argv) > 1 and sys.argv[1] in acceptableWebDriverNames:
    webDriverName = sys.argv[1]


def add_sound(id, title):
    if id in SoundTitleMap:
        return
    print('ADD NEW TITLE', id, title)
    SoundTitleMap[id] = title


def add_src(id, src, dirName):
    if id in SoundTitleMap:
        if id in SoundSrcMap:
            return
        print('ADD NEW SRC', id, src)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        name = dirName + "/" + SoundTitleMap[id] + "_" + str(id) + ".mp3"
        urllib.urlretrieve(src, name)
        print(name + " - Downloaded.")
        SoundSrcMap[id] = src


def get_id_from_src(src):
    startPattern = "track-id="
    endPattern = "&play="
    return src[src.find(startPattern) + len(startPattern): src.find(endPattern)]


def get_id_from_link(link):
    # expect "/album/2607596/track/22691625"
    pattern = "/track/"
    return link[link.find(pattern) + len(pattern):]


def load_from_radio(url, dirName, count):
    driver = webDriverToUse()
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(element_has_css_class((By.CLASS_NAME, 'player-controls__title'), ""))
        # Depends on your internet connection. Change it if need.
        time.sleep(5)
        driver.execute_script("externalAPI.play()")
        # Depends on your internet connection. Change it if need.
        time.sleep(5)
        for n in range(count):
            id = get_id_from_link(driver.execute_script("return externalAPI.getCurrentTrack().link"))
            title = unicode(driver.execute_script("return externalAPI.getCurrentTrack().title")).decode("utf8")
            add_sound(id, title)
            # Depends on your internet connection. Change it if need.
            time.sleep(1)
            files = driver.execute_script(
                "return window.performance.getEntries().filter(element=> element.name.includes('storage.yandex.net/get-mp3')).map(e => e.name)")
            print len(files)
            fileIds = []
            for src in files:
                srcId = get_id_from_src(src)
                fileIds.append(srcId)
                add_src(srcId, src, dirName)
            print fileIds
            if n % 10 == 0:
                driver.execute_script("performance.clearResourceTimings()")
            driver.execute_script("externalAPI.next()")
            # Depends on your internet connection. Change it if need.
            time.sleep(3)
    finally:
        driver.quit()


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    #Add link to radio station, directory name and count.
    load_from_radio('https://radio.yandex.ru/activity/run', 'run', 10)

