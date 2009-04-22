#!/usr/bin/python

import sys
import os
import time

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit

import twitter
import storm.locals as storm

class Status(object):
    __storm_table__ = "status"
    id = storm.Int(primary=True)
    screen_name = storm.Unicode()
    text = storm.Unicode()

# start to go
class Poll(QtCore.QThread):
    def __init__(self, store, parent = None):
        """Poll accounts for new entries, insert into db
        
        Arguments:
        - `self`:
        - `parent`:
        """
        QtCore.QThread.__init__(self, parent)
        self.store = store
        self.exiting = False

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
            
            acnt = twitter.Twitter()
            s = acnt.statuses.public_timeline()
            for x in s:
                status = Status()
                status.screen_name = x['user']['screen_name']
                status.text = x['text']
                self.store.add(status)
            
            self.emit(QtCore.SIGNAL("polled()"))
            
            time.sleep(10)


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
        self.c1.load(QtCore.QUrl("col.html"))
        self.hbox.addWidget(self.c1)

        self.web = QtWebKit.QWebView()
        self.web.load(QtCore.QUrl("col.html"))
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
        
        self.db = storm.create_database("sqlite:")
        self.store = storm.Store(self.db)
        
        self.store.execute("CREATE TABLE status "
                           "(id INTEGER PRIMARY KEY, screen_name VARCHAR, "
                           "text VARCHAR)")
        
        self.poller = Poll(self.store)
        self.connect(self.poller, QtCore.SIGNAL("polled()"), self.updateView)
        self.poller.start()

    def updateView(self):
        """Update the list of statuses
        """
        q = self.store.find(Status)
        html = "<html><body>"
        for s in q.order_by(storm.Desc(Status.id)):
            html += "<p>" + s.screen_name + " " + s.text
        html += "</body></html>"
        self.c1.setHtml(html)
    

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Sartre()
    main.show()
    sys.exit(app.exec_())
