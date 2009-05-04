#!/usr/bin/python

import sys
import os
import time

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import storm.locals as storm
import simplejson

import codecs

class SartreStore(QtCore.QObject):
    def __init__(self, store):
        """Represents a view to JS
        
        Arguments:
        - `self`:
        """
        QtCore.QObject.__init__(self)
        self.store = store
        self.statuses = []

    @pyqtSignature("done()")
    def done(self):
        print "done"
        self.emit(QtCore.SIGNAL("polled()"))
    
    @pyqtSignature("add(QVariantMap)")
    def add(self, data):
        print "add:" + str(data)
        status = Status()
        status.screen_name = unicode(data.get(QString('screen_name'))
                                     .toString())
        status.text = unicode(data.get(QString('text')).toString())
        self.store.add(status)


class Status(object):
    __storm_table__ = "status"
    id = storm.Int(primary=True)
    screen_name = storm.Unicode()
    text = storm.Unicode()

# start to go
class Poll(QtCore.QThread):
    def __init__(self, store, page, parent = None):
        """Poll accounts for new entries, insert into db
        
        Arguments:
        - `self`:
        - `parent`:
        """
        QtCore.QThread.__init__(self, parent)
        self.store = SartreStore(store)
        self.page = page
        self.frame = page.mainFrame()

        self.connect(self.frame, QtCore.SIGNAL("javaScriptWindowObjectCleared()"), self.reset)

        self.exiting = False

    def reset(self):
        print "resetting"
        self.frame.addToJavaScriptWindowObject("sartrestore", self.store)

    def __del__(self):
        """Ensure we cleanup/stop when destroyed
        
        Arguments:
        - `self`:
        """
        self.exiting = True
        self.wait()

    def run(self):
        """Poll
        
        Arguments:
        - `self`:
        """
        while not self.exiting:
            print "Poll.run"
            self.emit(QtCore.SIGNAL("poll()"))
            #self.frame.evaluateJavaScript("twitter_poll(sartrestore)")

            #self.frame.evaluateJavaScript("sartrestore.add({'screen_name':'test','text':'test1'})")
            #self.frame.evaluateJavaScript("sartrestore.done()")
            
            time.sleep(5)


class Sartre(QtGui.QMainWindow):
    """Sartre main window
    """

    def __init__(self):
        """
        """
        QtGui.QMainWindow.__init__(self)

        self.resize(800, 600)
        self.setWindowTitle('Sartre')
        
        self.wid = QtGui.QWidget()
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self.wid.setLayout(self.vbox)

        #self.statusBar().showMessage('Ready')

        #menubar = self.menuBar()
        #file = menubar.addMenu('&File')

        #self.fileToolBar = self.addToolBar(self.tr("File"))
        #self.editToolBar = self.addToolBar(self.tr("Edit"))

        self.menu = QtWebKit.QWebView()
        self.menu.load(QtCore.QUrl("menu.html"))
        self.menu.setFixedHeight(24)
        self.menu.page().mainFrame().setScrollBarPolicy(
            QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff )
        self.vbox.addWidget(self.menu)

        self.toolbar = QtWebKit.QWebView()
        self.toolbar.load(QtCore.QUrl("toolbar.html"))
        self.toolbar.setFixedHeight(24)
        self.toolbar.page().mainFrame().setScrollBarPolicy(
            QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff )
        self.vbox.addWidget(self.toolbar)

        self.hbox = QtGui.QHBoxLayout()

        self.c1 = QtWebKit.QWebView()
        self.c1.page().settings().setAttribute(
            QtWebKit.QWebSettings.JavascriptEnabled, True)

        self.c1.load(QtCore.QUrl("col.html"))
        self.hbox.addWidget(self.c1)

        self.web = QtWebKit.QWebView()
        #self.web.load(QtCore.QUrl("test.html"))
        self.web.load(QtCore.QUrl("col.html"))
        #self.web.load(QtCore.QUrl("sar.col1.html"))
        self.hbox.addWidget(self.web)

        self.web = QtWebKit.QWebView()
        self.web.load(QtCore.QUrl("col.html"))
        self.hbox.addWidget(self.web)
        
        self.vbox.addLayout(self.hbox)

        self.status = QtWebKit.QWebView()
        self.status.load(QtCore.QUrl("status.html"))
        self.status.setFixedHeight(24)
        self.status.page().mainFrame().setScrollBarPolicy(
            QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff )
        self.vbox.addWidget(self.status)

        self.setCentralWidget(self.wid)

        self.load_extensions()
        
        self.db = storm.create_database("sqlite:")
        self.store = storm.Store(self.db)
        
        self.store.execute("CREATE TABLE status "
                           "(id INTEGER PRIMARY KEY, screen_name VARCHAR, "
                           "text VARCHAR)")

        self.updateView()
        
        self.poller = Poll(self.store, self.c1.page())
        self.connect(self.poller.store, QtCore.SIGNAL("polled()"), self.updateView)
        self.connect(self.poller, QtCore.SIGNAL("poll()"), self.poll)

        self.poller.start()

    def poll(self):
        print "poll"
        self.c1.page().mainFrame().evaluateJavaScript("twitter_poll(sartrestore)")

    def load_extensions(self):
        """Read the manifest files and register the particular scripts
        """
        self.accountscripts = {}
        self.accountscripts['twitter'] = []
        self.viewscripts = {}
        self.viewscripts['twitter'] = []
        for dirname, dirnames, filenames in os.walk('extensions'):
            for subdirname in dirnames:
                path = os.path.join(dirname, subdirname, 'manifest.js')
                try:
                    f = open(path)
                except:
                    print "unable to load " + path
                else:
                    manifest = simplejson.load(f)
                    f.close()
                    print "loading views " + path
                    for key, value in manifest.get('views', {}).items():
                        for s in value:
                            spath =  os.path.join(dirname, subdirname, s)
                            self.viewscripts.get(key,[]).append(spath)
                            print "  " + key + "->" + spath
                    for key, value in manifest.get('account', {}).items():
                        for s in value:
                            spath =  os.path.join(dirname, subdirname, s)
                            self.accountscripts.get(key,[]).append(spath)
                            print "  " + key + "->" + spath

    def updateView(self):
        """Update the list of statuses
        """
        print "updating view"
        q = self.store.find(Status)
        html = []
        html.append('<html><head>')
        html.append('<link rel=StyleSheet href="style.css" type="text/css">')
        html.append('<script type="text/javascript" src="jquery-1.3.2.js"></script>')
        for s in self.accountscripts.get('twitter'):
            html.append('<script type="text/javascript" src="'
                        + s + '"></script>')
        for s in self.viewscripts.get('twitter'):
            html.append('<script type="text/javascript" src="'
                        + s + '"></script>')
        html.append('</head><body>')
        for s in q.order_by(storm.Desc(Status.id)):
            html.append('<div class="sn">')
            html.append(s.screen_name)
            html.append('</div> <div class="tx">')
            html.append(s.text)
            html.append('</div>')
        html.append("</body></html>")
        content = ''.join(html)
        f = codecs.open('/tmp/sar.col1.html', 'w', "utf-8")
        f.write(content)
        f.close()
        self.c1.setHtml(content, QtCore.QUrl(os.getcwd() + '/'))

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Sartre()
    main.show()
    sys.exit(app.exec_())
