# importing required libraries
from threading import Thread
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import sys
from pytube import YouTube, Playlist, extract

from message_box import show_critical_messagebox, show_info_messagebox

TUBESOURCE_DOWNLOAD_DIR = None
is_in_processing = False

class PlayListDownloadSettingScreen(QWidget):
    qualityRowCombo = None
    typeRowCombo = None
    currentQuality = None
    currentType = None
    
    def __init__(self):
        super().__init__()
        self.mainContainer = QVBoxLayout()
        self.qualityRow = QHBoxLayout()
        self.qualityRowLabel = QLabel("Quality")
        self.typeRow = QHBoxLayout()
        self.typeRowLabel = QLabel("Type")
        self.saveButton = QPushButton("save")
        
        PlayListDownloadSettingScreen.qualityRowCombo = QComboBox()
        PlayListDownloadSettingScreen.typeRowCombo = QComboBox()
        
        # widgets setting
        self.setLayout(self.mainContainer)
        self.mainContainer.addLayout(self.qualityRow)
        self.mainContainer.addLayout(self.typeRow)
        self.mainContainer.addWidget(self.saveButton)
        self.typeRow.addWidget(self.typeRowLabel)
        self.typeRow.addWidget(PlayListDownloadSettingScreen.typeRowCombo)
        self.qualityRow.addWidget(self.qualityRowLabel)
        self.qualityRow.addWidget(PlayListDownloadSettingScreen.qualityRowCombo)
        self.setWindowTitle("Playlist setting")
        
        self.typeRowCombo.addItems(["complete", "video", "audio"])
        self.qualityRowCombo.addItems(["High", "Medium", "Low"])
        self.saveButton.pressed.connect(self.closeWin)
        
    def closeWin(self):
        self.close()
        t = Thread(target=self.parse_playlist, daemon=True)
        t.start()
        
    def parse_playlist(self):
        global is_in_processing
        start = True if len(MainWindow.download_list) == 0 else False
        PlayListDownloadSettingScreen.currentQuality = PlayListDownloadSettingScreen.qualityRowCombo.currentText()
        PlayListDownloadSettingScreen.currentType = PlayListDownloadSettingScreen.typeRowCombo.currentText()
        MainWindow.working_label.setText("processing...")
        try:
            is_in_processing = True
            for url in MainWindow.current_playlist_object:
                try:
                    MainWindow.current_yt_object_url = url
                    MainWindow.current_yt_object = YouTube(url,on_progress_callback=MainWindow.progress_function,on_complete_callback=MainWindow.complete_function,use_oauth=True,
                allow_oauth_cache=True)
                    if PlayListDownloadSettingScreen.currentType == "complete":
                        t = {}
                        for stream in MainWindow.current_yt_object.streams.filter(progressive=True):
                            t[stream.resolution.split('p')[0]] = stream
                        if PlayListDownloadSettingScreen.currentQuality == "High":
                            stream = t[str(max(t.keys()))]
                        elif PlayListDownloadSettingScreen.currentQuality == "Medium":
                            stream = t[int(len(t.keys())/2)]
                        elif PlayListDownloadSettingScreen.currentQuality == "Low":
                            stream = t[str(min(t.keys()))]
                    elif PlayListDownloadSettingScreen.currentType == "video":
                        t = {}
                        for stream in MainWindow.current_yt_object.streams.filter(adaptive=True):
                            if stream.type != "audio":
                                t[stream.resolution.split('p')[0]] = stream
                        if stream.type != "audio":
                            if PlayListDownloadSettingScreen.currentQuality == "High":
                                stream = t[str(max(t.keys()))]
                            elif PlayListDownloadSettingScreen.currentQuality == "Medium":
                                stream = t[int(len(t.keys())/2)]
                            elif PlayListDownloadSettingScreen.currentQuality == "Low":
                                stream = t[str(min(t.keys()))]
                    elif PlayListDownloadSettingScreen.currentType == "audio":
                        t = {}
                        for stream in MainWindow.current_yt_object.streams.filter(only_audio=True):
                            t[stream.abr.split('kbps')[0]] = stream
                        if PlayListDownloadSettingScreen.currentQuality == "High":
                            stream = t[str(max(t.keys()))]
                        elif PlayListDownloadSettingScreen.currentQuality == "Medium":
                            stream = t[int(len(t.keys())/2)]
                        elif PlayListDownloadSettingScreen.currentQuality == "Low":
                            stream = t[str(min(t.keys()))]
                    DownloadScreen.selected_ressource = f"{PlayListDownloadSettingScreen.currentType} {stream.resolution} [" + "{0:.2f}".format(stream.filesize/1000000) + " MB" + "]"
                    if PlayListDownloadSettingScreen.currentType == "audio":
                        DownloadScreen.selected_ressource = f"audio {stream.mime_type.split('/')[1]} [" + "{0:.2f}".format(stream.filesize/1000000) + " MB" + "]"
                    DownloadScreen.stream_to_download[MainWindow.current_yt_object.title + f" {DownloadScreen.selected_ressource}"] = stream
                    DownloadScreen.is_playlist = True
                    DownloadScreen.get_ressource()
                except:
                    pass
            is_in_processing = False
            MainWindow.working_label.setText("")
            DownloadScreen.is_playlist = False
            if start:
                MainWindow.download_list_view.setCurrentRow(0)
                t = Thread(target=DownloadScreen.stream_down)
                t.start()
        except Exception as e:
            print(e)
            MainWindow.working_label.setText("")
            if start:
                MainWindow.download_list_view.setCurrentRow(0)
                t = Thread(target=DownloadScreen.stream_down)
                t.start()


class DownloadScreen(QWidget):
    selected_ressource = None
    streams_dic = {}
    stream_to_download = {}
    is_playlist = False
    
    def __init__(self):
        super().__init__()
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
        self.playList_Download_Setting_Screen = None

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
        self.download_btn.clicked.connect(DownloadScreen.get_ressource)
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
        DownloadScreen.selected_ressource = str(self.audio_list_view.currentItem().text())
        self.video_list_view.clearSelection()
        self.all_in_one_list_view.clearSelection()

    def normalize_video_list_views_click(self):
        DownloadScreen.selected_ressource = str(self.video_list_view.currentItem().text())
        self.audio_list_view.clearSelection()
        self.all_in_one_list_view.clearSelection()
        
    def normalize_all_in_one_list_views_click(self):
        DownloadScreen.selected_ressource = str(self.all_in_one_list_view.currentItem().text())
        self.audio_list_view.clearSelection()
        self.video_list_view.clearSelection()

    def get_ressource():
        global is_in_processing
        start = False
        try:
            MainWindow.download_window.close()
            if not DownloadScreen.is_playlist:
                is_in_processing = True
                DownloadScreen.stream_to_download[MainWindow.current_yt_object.title + f" {DownloadScreen.selected_ressource}"] = DownloadScreen.streams_dic[DownloadScreen.selected_ressource]
            if len(MainWindow.download_list) == 0:
                start = True
            down_itm = {"title": MainWindow.current_yt_object.title, "id":extract.video_id(MainWindow.current_yt_object_url), "type": DownloadScreen.selected_ressource}
            if down_itm not in MainWindow.download_list:
                MainWindow.download_list.append(down_itm)
                MainWindow.download_list_len.setText(f"Total: {str(len(MainWindow.download_list))}")
                QListWidgetItem(MainWindow.current_yt_object.title + f" {DownloadScreen.selected_ressource}", MainWindow.download_list_view)
            if not DownloadScreen.is_playlist:
                is_in_processing = False
            if start and not DownloadScreen.is_playlist:
                t = Thread(target=DownloadScreen.stream_down)
                t.start()
        except Exception as e:
            print(e)

    def pick_streams(self):
        try:
            self.streams = MainWindow.current_yt_object.streams
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
                resource_name = f"complete {stream.resolution} [" + "{0:.2f}".format(stream.filesize/1000000) + " MB" + "]"
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
        except Exception as e:
            MainWindow.download_window.close()
            show_critical_messagebox("age restriction")
        

    def download(self, p):
        if not p:
            t = Thread(target=self.pick_streams)
            t.start()
        else:
            self.playList_Download_Setting_Screen = PlayListDownloadSettingScreen()
            self.playList_Download_Setting_Screen.setWindowModality(Qt.ApplicationModal)
            self.playList_Download_Setting_Screen.show()
            
    def stream_down():
        global TUBESOURCE_DOWNLOAD_DIR
        try:
            ob = MainWindow.download_list[0]
            MainWindow.current_download_title.setText(f"{ob['title']} {ob['type']}")
            DownloadScreen.stream_to_download[f"{ob['title']} {ob['type']}"].download(output_path=TUBESOURCE_DOWNLOAD_DIR,skip_existing=False)
        except Exception as e:
            print(e)

 
# creating main window class
class MainWindow(QMainWindow):
    
    download_list_view = None
    download_list = []
    current_yt_object = None
    curren_playlist_object = None
    current_yt_object_url = None
    progress_bar = None
    download_window = None
    current_download_title = None
    working_label = None
    download_list_len = None
 
    # constructor
    def __init__(self, *args, **kwargs):
        global TUBESOURCE_DOWNLOAD_DIR
        super(MainWindow, self).__init__(*args, **kwargs)
        self.resize(1000, 600)
        self.setWindowTitle("TubeSource")
        self.widget = QWidget()
        self.bottomtoolbar = QWidget()
        self.main_container = QHBoxLayout()
        self.layout = QVBoxLayout()
        self.download_list_view_layout = QVBoxLayout()
        self.browser = QWebEngineView()
        self.progress_container = QHBoxLayout()
        self.bottomtoolbarlayout = QHBoxLayout()
        self.download_btn = QPushButton("Download")
        MainWindow.download_list_len = QLabel("Total: 0")
        self.progress_indicators_layout = QVBoxLayout()
        MainWindow.working_label = QLabel()
        MainWindow.current_download_title = QLabel()
        MainWindow.progress_bar = QProgressBar(self)
        
        MainWindow.current_downloading_label = QLabel("")
        MainWindow.download_list_view = QListWidget()
        
        #TUBESOURCE_DOWNLOAD_DIR = os.environ.get('TUBESOURCE_DOWNLOAD_DIR', None)
        if TUBESOURCE_DOWNLOAD_DIR == None:
            TUBESOURCE_DOWNLOAD_DIR = 'C:'+os.getenv('HOMEPATH')+'\\Downloads'
            os.environ['TUBESOURCE_DOWNLOAD_DIR'] = TUBESOURCE_DOWNLOAD_DIR
 

        # widgets settings
        self.browser.setUrl(QUrl("https://www.youtube.com"))
        MainWindow.progress_bar.setValue(0)
        self.download_list_view_layout.addWidget(MainWindow.download_list_view)
        self.download_list_view_layout.addWidget(MainWindow.download_list_len)
        self.download_list_view.currentRowChanged.connect(lambda: self.normalize_download_list_views_click())
        MainWindow.download_list_view.setMaximumWidth(300)

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
        self.main_container.addLayout(self.layout)
        self.main_container.addLayout(self.download_list_view_layout)
        self.widget.setLayout(self.main_container)
        self.setCentralWidget(self.widget)
        self.bottomtoolbarlayout.setAlignment(Qt.AlignRight)
        self.bottomtoolbarlayout.addLayout(self.progress_indicators_layout)
        self.bottomtoolbarlayout.addWidget(MainWindow.current_downloading_label)
        self.progress_indicators_layout.addWidget(self.progress_bar)
        self.progress_indicators_layout.addWidget(MainWindow.current_download_title)
        self.bottomtoolbarlayout.addWidget(self.download_btn)
        self.bottomtoolbarlayout.addWidget(MainWindow.working_label)
        self.download_btn.clicked.connect(self.download)
        
    def normalize_download_list_views_click(self):
        MainWindow.download_list_view.setCurrentRow(0)
        print(MainWindow.download_list_view.currentRow())
 
    def progress_function(stream, chunk, bytes_remaining):
        filesize = stream.filesize
        current = ((filesize - bytes_remaining)/filesize)
        #MainWindow.progress_bar.setValue(math.floor(current*100))
        
    def complete_function(stream, filepath):
        try:
            MainWindow.download_list.pop(0)
            MainWindow.download_list_len.setText(f"Total: {str(len(MainWindow.download_list))}")
            MainWindow.download_list_view.takeItem(0)
            if len(MainWindow.download_list) != 0:
                #MainWindow.progress_bar.setValue(0)
                t = Thread(target=DownloadScreen.stream_down)
                t.start()
            else:
                MainWindow.current_download_title.setText("")
        except Exception as e:
            print(e)
        
    def download(self):
        global is_in_processing
        if not is_in_processing:
            MainWindow.current_yt_object_url = str(self.browser.url().url())
            try:
                if "playlist" in MainWindow.current_yt_object_url:
                    MainWindow.current_playlist_object = Playlist(MainWindow.current_yt_object_url)
                    self.start_yt_download(True)
                else:
                    MainWindow.current_yt_object = YouTube(MainWindow.current_yt_object_url,on_progress_callback=MainWindow.progress_function,on_complete_callback=MainWindow.complete_function,use_oauth=True,
            allow_oauth_cache=True)
                    self.start_yt_download()
            except Exception as e:
                print(e)
                show_critical_messagebox("can't download")
        else:
            show_info_messagebox("Some task are already running, so please wait!")
            
    def start_yt_download(self, p=False):
        MainWindow.download_window = DownloadScreen()
        if not p:
            MainWindow.download_window.setWindowModality(Qt.ApplicationModal)
            MainWindow.download_window.show()
        self.download_window.download(p)

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