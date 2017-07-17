#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import urllib2
from HTMLParser import HTMLParser

class Downloader():
  def __init__(self):
    if sys.platform == 'win32' and os.environ['COMPUTERNAME'] == 'CV0020832N0':
      proxy_handler = urllib2.ProxyHandler({'http': 'http://127.0.0.1:3128', 'https':'https://127.0.0.1:3128'})
      self.opener = urllib2.build_opener(proxy_handler)
    else:
      self.opener = urllib2.build_opener()
    #self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]

  def open(self, url, tmo=10):
    try:
      f = self.opener.open(url, timeout=tmo)
    except IOError,e:
      print IOError
      sys.exit(1)
    return f

class DOM():
  def __init__(self, parent, tag, attrs):
    self.tag = tag
    self.attrs = attrs
    self.data = None
    self.childidx = 0
    self.parent = parent
    if parent: parent.insert_child(self)
    if not parent:
      self.depth = 1
    else:
      self.depth = parent.depth + 1
    self.children = list()

  def add_data(self, data):
    self.data = data

  def insert_child(self, child):
    self.children.append(child)
    child.childidx = len(self.children) - 1

  def do_print(self):
    print ''.join([' ' for i in range(self.depth)]) + self.tag + str(self.attrs)
    for child in self.children:
      child.do_print()

class DOMHTMLParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.cur = None
    self.domtree = None

  def handle_starttag(self, tag, attrs):
    dom = DOM(self.cur, tag, attrs)
    if tag not in ['meta', 'link', 'br']:
      self.cur = dom
    if not self.domtree: self.domtree = dom

  def handle_endtag(self, tag):
    if tag not in ['meta', 'link', 'br']:
      self.cur = self.cur.parent

  def handle_startendtag(self, tag, attrs):
    dom = DOM(self.cur, tag, attrs)
    if not self.domtree: self.domtree = dom

  def handle_data(self, data):
    self.cur.add_data(data)


class HNItem():
  def __init__(self):
    self.id = None
    self.rank = None
    self.title = None
    self.href = None
    self.score = None
    self.comments = None

class HNParser():
  def __init__(self, domtree):
    self.domtree = domtree
    self.items = self.find_items(domtree)
  
  def find_table(self, domtree):
    if domtree.tag == 'table':
      for attr in domtree.attrs:
        if attr[0] == 'class' and attr[1] == 'itemlist':
          return domtree
    for child in domtree.children:
      table = self.find_table(child)
      if table: return table
    return None

  def find_items(self, domtree):
    items = list()
    table = self.find_table(domtree)
    if not table:
      print 'table not found'
      return
    num = len(table.children)/3
    for i in range(num):
      #table.children[i*3+1].do_print()
      item = HNItem()
      item.rank = table.children[i*3].children[0].children[0].data
      item.title = table.children[i*3].children[2].children[1].data.decode('utf-8')
      item.href = table.children[i*3].children[2].children[1].attrs[0][1]
      item.score = table.children[i*3+1].children[1].children[0].data
      if len(table.children[i*3+1].children[1].children) > 3:
        item.comments = table.children[i*3+1].children[1].children[3].data
        item.id = re.sub(r'\D+(\d+)', r'\1', table.children[i*3+1].children[1].children[3].attrs[0][1])
      items.append(item)
    return items

  def print_items(self, items):
    for item in items:
      print item.rank, item.title.encode(sys.getfilesystemencoding())
      print item.href
      print item.id, item.score, item.comments
    

if __name__ == '__main__':
  downloader = Downloader()
  #print downloader.open('http://coolshell.cn').read().decode('utf-8').encode(sys.getfilesystemencoding())
  parser = DOMHTMLParser()
  parser.feed(downloader.open('https://news.ycombinator.com/').read())
  parser.close()
  hn = HNParser(parser.domtree)
  hn.print_items(hn.items)



