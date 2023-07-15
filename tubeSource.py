# importing required libraries
import math
from threading import Thread
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import sys
from pytube import YouTube

from message_box import show_critical_messagebox

global TUBESOURCE_DOWNLOAD_DIR

class DownloadScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.youtube_obj = None
        self.download_url = None
        self.streams_dic = {}
        self.selected_ressource = ""
        self.streams = None
        self.layout = QVBoxLayout()
        self.video_ctn = QVBoxLayout()
        self.audio_ctn = QVBoxLayout()
        self.all_in_one_ctn = QVBoxLayout()
        self.download_btn = QPushButton("Get")
        self.video_ctn_title = QLabel("Videos")
        self.audio_ctn_title = QLabel("Audios")
        self.all_in_one_ctn_title = QLabel("All in one")
        self.video_list_view = QListView()
        self.audio_list_view = QListView()
        self.all_in_one_list_view = QListView()
        self.loading_title = QLabel("Loading...")

        # widgets setting
        self.layout.addWidget(self.loading_title)
        self.setWindowTitle("download window")

        # list views
        self.video_list_view = QListWidget()
        self.audio_list_view = QListWidget()
        self.all_in_one_list_view = QListWidget()
        # --------------

        self.video_ctn.addWidget(self.video_ctn_title)
        self.audio_ctn.addWidget(self.audio_ctn_title)
        self.all_in_one_ctn.addWidget(self.all_in_one_ctn_title)
        self.setLayout(self.layout)
        self.download_btn.clicked.connect(self.get_ressource)
        self.all_in_one_list_view.currentRowChanged.connect(lambda: self.normalize_all_in_one_list_views_click())
        self.video_list_view.currentRowChanged.connect(lambda: self.normalize_video_list_views_click())
        self.audio_list_view.currentRowChanged.connect(lambda: self.normalize_audio_list_views_click())

        # styles
        self.video_ctn_title.setStyleSheet("background-color: PaleGreen;")
        self.audio_ctn_title.setStyleSheet("background-color: PaleGreen;")
        self.all_in_one_ctn_title.setStyleSheet("background-color: PaleGreen;")
        self.video_ctn.addWidget(self.video_list_view)
        self.audio_ctn.addWidget(self.audio_list_view)
        self.all_in_one_ctn.addWidget(self.all_in_one_list_view)

    def normalize_audio_list_views_click(self):
        self.selected_ressource = str(self.audio_list_view.currentItem().text())
        self.video_list_view.clearSelection()
        self.all_in_one_list_view.clearSelection()

    def normalize_video_list_views_click(self):
        self.selected_ressource = str(self.video_list_view.currentItem().text())
        self.audio_list_view.clearSelection()
        self.all_in_one_list_view.clearSelection()
        
    def normalize_all_in_one_list_views_click(self):
        self.selected_ressource = str(self.all_in_one_list_view.currentItem().text())
        self.audio_list_view.clearSelection()
        self.video_list_view.clearSelection()

    def stream_down(self):
        global TUBESOURCE_DOWNLOAD_DIR
        self.streams_dic[self.selected_ressource].download(output_path=TUBESOURCE_DOWNLOAD_DIR,skip_existing=True)

    def get_ressource(self):
        try:
            t = Thread(target=self.stream_down)
            t.start()
        except:
            pass
        self.close()

    def pick_streams(self):
        self.streams = self.youtube_obj.streams
        progressive_streams = self.streams.filter(progressive=True)
        videos_streams = self.streams.filter(only_video=True)
        audios_streams = self.streams.filter(only_audio=True)
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()
        self.layout.addLayout(self.all_in_one_ctn)
        self.layout.addLayout(self.video_ctn)
        self.layout.addLayout(self.audio_ctn)
        self.layout.addWidget(self.download_btn)
        
        for stream in progressive_streams:
            resource_name = f"full {stream.resolution} [" + "{0:.2f}".format(stream.filesize/1000000) + " MB" + "]"
            self.streams_dic[resource_name] = stream
            QListWidgetItem(resource_name, self.all_in_one_list_view)
        
        for stream in videos_streams:
            resource_name = f"video {stream.resolution} [" + "{0:.2f}".format(stream.filesize/1000000) + " MB" + "]"
            self.streams_dic[resource_name] = stream
            QListWidgetItem(resource_name, self.video_list_view)
            
        for stream in audios_streams:
            resource_name = f"audio {stream.mime_type.split('/')[1]} [" + "{0:.2f}".format(stream.filesize/1000000) + " MB" + "]"
            self.streams_dic[resource_name] = stream
            QListWidgetItem(resource_name, self.audio_list_view)
        

    def download(self, url, yt):
        self.download_url = url
        self.youtube_obj = yt
        self.pick_streams()

 
# creating main window class
class MainWindow(QMainWindow):
 
    # constructor
    def __init__(self, *args, **kwargs):
        global TUBESOURCE_DOWNLOAD_DIR
        super(MainWindow, self).__init__(*args, **kwargs)
        self.resize(1000, 600)
        self.setWindowTitle("TubeSource")
        self.widget = QWidget()
        self.bottomtoolbar = QWidget()
        self.layout = QVBoxLayout()
        self.browser = QWebEngineView()
        self.progress_container = QHBoxLayout()
        self.bottomtoolbarlayout = QHBoxLayout()
        self.download_btn = QPushButton("Download")
        self.download_window = None
        self.current_downloading_label = QLabel("")
        self.current_downloading_remaind_count = 0
        self.progress_bar = QProgressBar(self)
        
        TUBESOURCE_DOWNLOAD_DIR = os.environ.get('TUBESOURCE_DOWNLOAD_DIR', None)
        if TUBESOURCE_DOWNLOAD_DIR == None:
            TUBESOURCE_DOWNLOAD_DIR = 'C:\\Users\\dsidi\\Downloads'
            os.environ['TUBESOURCE_DOWNLOAD_DIR'] = TUBESOURCE_DOWNLOAD_DIR
 

 
        # widgets settings
        self.browser.setUrl(QUrl("https://www.youtube.com"))
        self.progress_bar.setValue(0)

        # adding action when url get changed
        self.browser.urlChanged.connect(self.update_urlbar)

        # creating a status bar object
        self.status = QStatusBar()

        # adding status bar to the main window
        self.setStatusBar(self.status)

        # creating QToolBar for navigation
        navtb = QToolBar("Navigation")

        # adding this toolbar to the main window
        self.addToolBar(navtb)

        # adding actions to the tool bar
        # creating a action for back
        back_btn = QAction("Back", self)

        # setting status tip
        back_btn.setStatusTip("Back to previous page")

        # adding action to the back button
        # making browser go back
        back_btn.triggered.connect(self.browser.back)

        # adding this action to toolbar
        navtb.addAction(back_btn)

        # similarly for forward action
        next_btn = QAction("Forward", self)
        next_btn.setStatusTip("Forward to next page")

        # adding action to the next button
        # making browser go forward
        next_btn.triggered.connect(self.browser.forward)
        navtb.addAction(next_btn)

        # similarly for reload action
        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload page")

        # adding action to the reload button
        # making browser to reload
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)

        # similarly for home action
        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # adding a separator in the tool bar
        navtb.addSeparator()

        # creating a line edit for the url
        self.urlbar = QLineEdit()

        # adding action when return key is pressed
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        # adding this to the toolbar
        navtb.addWidget(self.urlbar)

        # adding stop action to the toolbar
        stop_btn = QAction("Stop", self)
        stop_btn.setStatusTip("Stop loading current page")

        # adding action to the stop button
        # making browser to stop
        stop_btn.triggered.connect(self.browser.stop)
        navtb.addAction(stop_btn)

        self.layout.addWidget(self.browser)
        self.bottomtoolbar.setLayout(self.bottomtoolbarlayout)
        self.bottomtoolbar.setFixedHeight(50)
        self.layout.addWidget(self.bottomtoolbar)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.bottomtoolbarlayout.setAlignment(Qt.AlignRight)
        self.bottomtoolbarlayout.addWidget(self.current_downloading_label)
        self.bottomtoolbarlayout.addWidget(self.progress_bar)
        self.bottomtoolbarlayout.addWidget(self.download_btn)
        self.download_btn.clicked.connect(self.download)
 
 
    def progress_function(self, stream, chunk, bytes_remaining):
        filesize = stream.filesize
        current = ((filesize - bytes_remaining)/filesize)
        self.progress_bar.setValue(math.floor(current*100))
        
    def on_complet(self, stream, filepath):
        pass
        
    def download(self):
        url = str(self.browser.url().url())
        try:
            yt = YouTube(url,on_progress_callback=self.progress_function,on_complete_callback=self.on_complet,use_oauth=False,
        allow_oauth_cache=True)
            self.download_window = DownloadScreen()
            self.download_window.setWindowModality(Qt.ApplicationModal)
            self.download_window.show()
            self.download_window.download(url, yt)
        except Exception as e:
            print(e)
            show_critical_messagebox("can't download")

    # method called by the home action
    def navigate_home(self):
        # open the google
        self.browser.setUrl(QUrl("https://www.youtube.com"))

    # method called by the line edit when return key is pressed
    def navigate_to_url(self):
        # getting url and converting it to QUrl object
        q = QUrl(self.urlbar.text())

        # if url is scheme is blank
        if q.scheme() == "":
            # set url scheme to html
            q.setScheme("http")

        # set the url to the browser
        self.browser.setUrl(q)

    # method for updating url
    # this method is called by the QWebEngineView object
    def update_urlbar(self, q):
        # setting text to the url bar
        self.urlbar.setText(q.toString())

        # setting cursor position of the url bar
        self.urlbar.setCursorPosition(0)
 
 
# creating a pyQt5 application
app = QApplication(sys.argv)
 
# setting name to the application
app.setApplicationName("TubeSource")
 
# creating a main window object
window = MainWindow()
window.show()
 
# loop
app.exec_()