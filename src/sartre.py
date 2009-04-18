#!/usr/bin/python

import sys
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit

import twitter

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
        
        acnt = twitter.Twitter()
        s = acnt.statuses.public_timeline()
        html = "<html><body>"
        for x in s:
            html += "<p>" + x['user']['screen_name'] + " " + x['text']
        html += "</body></html>"
        self.c1.setHtml(html)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Sartre()
    main.show()
    sys.exit(app.exec_())
