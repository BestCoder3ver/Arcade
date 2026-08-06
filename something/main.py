import sys
from urllib.parse import quote_plus

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QTabWidget,
    QToolBar,
)
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView


HOME_URL = "https://www.google.com"


def make_url(text):
    text = text.strip()
    if not text:
        return QUrl(HOME_URL)
    if "://" in text:
        return QUrl(text)
    if "." in text and " " not in text:
        return QUrl("https://" + text)
    return QUrl("https://www.google.com/search?q=" + quote_plus(text))


class BrowserPage(QWebEnginePage):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

    def createWindow(self, _type):
        return self.window.add_tab(HOME_URL).page()


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python Browser")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.currentChanged.connect(self.update_url_bar_from_tab)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        nav = QToolBar("Navigation")
        nav.setMovable(False)
        self.addToolBar(nav)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.go_home)
        nav.addAction(home_btn)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        nav.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        nav.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        nav.addAction(reload_btn)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.triggered.connect(lambda: self.add_tab(HOME_URL))
        nav.addAction(new_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search Google or enter a URL")
        self.url_bar.returnPressed.connect(self.go_to_url)
        nav.addWidget(self.url_bar)

        go_btn = QAction("Go", self)
        go_btn.triggered.connect(self.go_to_url)
        nav.addAction(go_btn)

        self.add_tab(HOME_URL)
        self.show()

    def add_tab(self, url):
        browser = QWebEngineView()
        browser.setPage(BrowserPage(self))
        browser.setUrl(make_url(url))

        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda qurl, view=browser: self.update_tab_url(view, qurl))
        browser.titleChanged.connect(lambda title, view=browser: self.update_tab_title(view, title))

        return browser

    def current_browser(self):
        return self.tabs.currentWidget()

    def close_tab(self, index):
        if self.tabs.count() == 1:
            self.current_browser().setUrl(QUrl(HOME_URL))
            return
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        widget.deleteLater()

    def go_home(self):
        self.current_browser().setUrl(QUrl(HOME_URL))

    def go_to_url(self):
        self.current_browser().setUrl(make_url(self.url_bar.text()))

    def update_tab_url(self, browser, qurl):
        if browser == self.current_browser():
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

    def update_tab_title(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title[:24] or "New Tab")

    def update_url_bar_from_tab(self, index):
        browser = self.tabs.widget(index)
        if browser:
            self.url_bar.setText(browser.url().toString())
            self.url_bar.setCursorPosition(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    sys.exit(app.exec())
