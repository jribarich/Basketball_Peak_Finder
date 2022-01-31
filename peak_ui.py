""" 
Basketball Peak Finder:
Finds an individual player's peak in their career

this file specifically holds the GUI design of peakfinder.py

Command line example:
"python3 peak_ui.py"

Created by Jack Ribarich
August 4th, 2020

"""

import sys
import os
import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
import peakfinder as pf

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

b_width = " 5px"  # border width
b_type = " outset" # solid, dashed, inset, outset, groove, ridge
b_color = " #c45002" # orange border color

last_player = None

class Peak_Widget(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        layout = QGridLayout(self)
        layout.setSpacing(10)

        self.peak_label = QLabel('Peak')
        self.peak_label.setAlignment(QtCore.Qt.AlignCenter)
        style = "font-weight: bold; border:" + b_width + b_type + b_color
        self.peak_label.setStyleSheet(style) 

        self.season_label = QLabel('<b>Season: </b>')  # <b> ... </b> Qlabel supports bold
        self.team_label = QLabel('<b>Team: </b>')
        self.PER_label = QLabel('<b>PER:  </b>')
        self.WS_label = QLabel('<b>Win Shares:  </b>')
        self.FG_label = QLabel('<b>FG%: </b>')
        self.PPG_label = QLabel('<b>PPG: </b>')
        self.APG_label = QLabel('<b>APG: </b>')
        self.RPG_label = QLabel('<b>RPG: </b>')

        layout.addWidget(self.peak_label, 0, 0, 1, 2)
        layout.addWidget(self.season_label, 1, 0, 1, 1)
        layout.addWidget(self.team_label, 2, 0, 1, 1)
        layout.addWidget(self.PER_label, 3, 0, 1, 1)
        layout.addWidget(self.WS_label, 4, 0, 1, 1)
        layout.addWidget(self.FG_label, 1, 1, 1, 1)
        layout.addWidget(self.PPG_label, 2, 1, 1, 1)
        layout.addWidget(self.APG_label, 3, 1, 1, 1)
        layout.addWidget(self.RPG_label, 4, 1, 1, 1)

    def update(self, peak):
        self.season_label.setText('<b>Season: </b>' + peak[0])
        self.team_label.setText('<b>Team: </b>' + peak[1])
        self.PER_label.setText('<b>PER: </b>' + str(peak[2]))
        self.WS_label.setText('<b>Win Shares: </b>' + str(peak[3]))
        self.FG_label.setText('<b>FG%: </b>' + str(round(float(peak[4])*100, 1)))
        self.PPG_label.setText('<b>PPG: </b>' + str(peak[5]))
        self.APG_label.setText('<b>APG: </b>' + str(peak[6]))
        self.RPG_label.setText('<b>RPG: </b>' + str(peak[7]))

class Player_Info_Widget(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        layout = QGridLayout(self)
        layout.setSpacing(10)

        player_info_label = QLabel('Player Information')
        player_info_label.setAlignment(QtCore.Qt.AlignCenter)
        style = "font-weight: bold; border:" + b_width + b_type + b_color
        player_info_label.setStyleSheet(style) 

        self.nick_label = QLabel('<b>Nickname: </b>') # <b> ... </b> Qlabel supports bold
        self.name_label = QLabel('<b>Name: </b>')
        self.pos_label = QLabel('<b>Position: </b>')
        self.height_label = QLabel('<b>Height: </b>')
        self.hand_label = QLabel('<b>Shoots: </b>')
        self.college_label = QLabel('<b>College: </b>')
        self.pic_label = QLabel()
        self.pixmap = QtGui.QPixmap('bball_logo.png').scaled(150, 150, QtCore.Qt.KeepAspectRatio,
                                                              QtCore.Qt.SmoothTransformation)
        self.pic_label.setPixmap(self.pixmap)
        self.pic_label.setAlignment(QtCore.Qt.AlignCenter)
    
        layout.addWidget(player_info_label, 0, 0, 1, 2)
        layout.addWidget(self.pic_label, 1, 0, 1, 2)
        layout.addWidget(self.pos_label, 3, 0, 1, 1)
        layout.addWidget(self.height_label, 4, 0, 1, 1)
        layout.addWidget(self.name_label, 2, 0, 1, 1)
        layout.addWidget(self.nick_label, 2, 1, 1, 1)
        layout.addWidget(self.college_label, 3, 1, 1, 1)
        layout.addWidget(self.hand_label, 4, 1, 1, 1)

    def update(self, p):
        name = (p.name.split(' ')[0].capitalize() + 
                ' ' + p.name.split(' ')[1].capitalize())  # capitalizes player name

        self.nick_label.setText('<b>Nickname: </b>' + p.nicknames)
        self.name_label.setText('<b>Name: </b>' + name)
        self.pos_label.setText('<b>Position: </b>' + p.position)
        self.height_label.setText('<b>Height: </b>' + p.height)
        self.hand_label.setText('<b>Shoots: </b>' + p.hand)
        self.college_label.setText('<b>College: </b>' + p.college)
        
        if os.path.isfile(p.ext + '.jpg'):
            self.pixmap = QtGui.QPixmap(p.ext + '.jpg').scaled(150, 150, QtCore.Qt.KeepAspectRatio,
                                                              QtCore.Qt.SmoothTransformation)

        else:
            self.pixmap = QtGui.QPixmap('bball_logo.png').scaled(150, 150, QtCore.Qt.KeepAspectRatio,
                                                              QtCore.Qt.SmoothTransformation)

        self.pic_label.setPixmap(self.pixmap)
        self.pic_label.setAlignment(QtCore.Qt.AlignCenter)


class MplCanvas(FigureCanvasQTAgg):
    
    def __init__(self, parent=None, width=7, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.subplots_adjust(top = .93, hspace=.5)
        self.peak_graph = self.fig.add_subplot(211)
        self.peak_graph.set_title('Peak')
        self.stats = self.fig.add_subplot(212)
        self.stats.set_title('Stats Per Game')
        super(MplCanvas, self).__init__(self.fig)

    def redraw(self, peak):
        # seasons = peak[1], peak sum = peak[2], ppg/apg/rpg = peak[3,4,5]
        x = peak[1]
        idx = np.arange(len(peak[1]))  # turns season into a list of indices
        peak_sum = peak[2]
        max_idx = peak[2].index(max(peak[2])) 
        ppg = peak[3]
        apg = peak[4]
        rpg = peak[5]

        self.peak_graph.cla()  # clears frame
        self.stats.cla()  # clears frame
        self.fig.canvas.draw_idle()  # clears canvas
        
        self.peak_graph.set_title('Peak')
        self.peak_graph.set_xticks(idx)
        self.peak_graph.set_xticklabels(peak[1], rotation = 70)
        self.peak_graph.plot(idx, peak_sum)  # peak sum
        self.peak_graph.axvspan(max_idx, max_idx, color='C1')  # highlights peak


        self.stats.set_title('Stats Per Game')
        self.stats.set_xticks(idx)
        self.stats.set_xticklabels(peak[1], rotation=70)
        # self.stats.set_yticks(np.arange(0, max(ppg) + 1, 1))
        self.stats.plot(idx, ppg, color = 'green')  # points
        self.stats.plot(idx, apg, color = 'blue')   # assists
        self.stats.plot(idx, rpg, color = 'red')  # rebounds
        self.stats.axvspan(max_idx, max_idx, color='C1') # highlights peak

        self.stats.legend(['Points', 'Assists', 'Rebounds'])


class Search_Options_Widget(QWidget):
    
    def __init__(self, info_widg = None, peak_widg = None, graph_widg = None, name= None, parent=None):
        QWidget.__init__(self, parent=parent)

        layout = QGridLayout(self)
        layout.setSpacing(10)   

        self.info_widg = info_widg
        self.peak_widg = peak_widg
        self.graph_widg = graph_widg
        self.name = None
        self.prev_name = None  # previous name
        self.player = pf.Player()
        self.peak_data = None

        # Creates search button
        self.search_button = QPushButton('Find Peak')
        self.search_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.search_button.clicked.connect(self.button_clicked)
        self.search_button.setAutoDefault(True)

        # Creates Search Bar with placeholder text
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Enter Player Name")
        self.search_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.search_box.returnPressed.connect(self.search_button.click)

        self.reg_button = QRadioButton('Regular Season')
        self.reg_button.setChecked(True)
        self.reg_button.toggled.connect(self.button_clicked)
        self.playoff_button = QRadioButton('Playoffs')
        self.playoff_button.toggled.connect(self.button_clicked)

        self.search_label  = QLabel('Search')
        self.search_label.setAlignment(QtCore.Qt.AlignCenter)
        style = "font-weight: bold; border:" + b_width + b_type + b_color
        self.search_label.setStyleSheet(style)

        layout.addWidget(self.search_label, 0, 0, 1, 2)
        layout.addWidget(self.search_box, 1, 0, 1, 1)
        layout.addWidget(self.search_button, 2, 0, 1, 1)
        layout.addWidget(self.reg_button, 1, 1)
        layout.addWidget(self.playoff_button, 2, 1)


    def button_clicked(self):
        global last_player
        remove_flag = 0

        if self.player.ext != None:
            self.prev_name = self.player.ext

        if (self.name != self.search_box.text() and
            self.search_box.text() != '' and
            self.name != None and 
            self.prev_name != None):

            remove_flag = 1

        if (self.name == None or 
            (self.name != self.search_box.text() and
            self.search_box.text() != '')):

            self.name = self.search_box.text()
            self.player, self.peak_data = pf.retrieve(self.name)

        if self.player == None:
            QMessageBox.about(self, "Information", "Invalid Player: check spelling")
            self.player = pf.Player()
            return

        if remove_flag == 1:
            pf.remove_pic(self.prev_name)

        last_player = self.player.ext

        if self.playoff_button.isChecked() == False:
            peak = self.peak_data[0]  # peak_data holds both regular season and playoffs
            self.search_box.clear()  # if player is spelled correctly

        else:
            peak = self.peak_data[1]  # only executes if playoff box selected

            if peak == None:
                QMessageBox.about(self, "Information", self.name + " has never made the playoffs")
                return

            else:
                self.search_box.clear()  # if player is spelled correctly 

        Player_Info_Widget.update(self.info_widg, self.player)

        Peak_Widget.update(self.peak_widg, peak[0])  # peak[0] is peak list with essential info

        MplCanvas.redraw(self.graph_widg, peak)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        graph_widg = MplCanvas(self, width=7, height=5, dpi=100)
        graph_widg.peak_graph.plot([0,0], [0,0])
        graph_widg.stats.plot([0,0], [0,0])

        # the .addWidget has params of (widget, row, col, rowspan, colspan)
        layout = QGridLayout()
        layout.setSpacing(10)

        pw = Peak_Widget()
        piw = Player_Info_Widget()
        sow = Search_Options_Widget(piw, pw, graph_widg)

        layout.addWidget(pw, 0, 0, 1, 2)
        layout.addWidget(piw, 1, 0, 1, 2)
        layout.addWidget(sow, 4, 0, 1, 2)
        layout.addWidget(graph_widg, 0, 3, 10, 10)

        # Creates toolbar, passing canvas as first parament, parent (self, the MainWindow) as second
        # toolbar = NavigationToolbar(table, self)
        # layout.addWidget(toolbar, 11, 3, 1, 1)

        # Create a placeholder widget to hold our subwidgets
        widget = QWidget()
        widget.setLayout(layout)
        self.setObjectName("window")
        main_style = "QWidget#window {border-bottom:" + b_width + b_type + b_color + "}"
        self.setStyleSheet(main_style)
        self.setCentralWidget(widget)
        self.setWindowTitle("Basketball Peak Finder")
        self.show()

def main():
    app = QApplication([])

    if sys.platform == 'darwin':
        app.setStyle('Macintosh')  # Fusion, Macintosh, Windows
    else:
        app.setStyle('Fusion') 

    path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'bball_logo.png')
    app.setWindowIcon(QtGui.QIcon(path))
    w = MainWindow()
    app.exec_()

    try:
        os.remove(last_player + '.jpg')

    except:
        pass  # do nothing if last player didnt have a pic

    sys.exit()

if __name__ == '__main__':
    main()