from PyQt4 import QtGui, QtCore, Qt
from pygaze import eyetracker, libtime
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from .pygaze_framework import MyEvent
from .stuff import encapsulate_text
import sys
import datetime
import threading


class EyeTrackerSetupWindow(QtGui.QWidget):

    class Plotter(threading.Thread):

        def __init__(self, call_function, interval=1000):
            super(EyeTrackerSetupWindow.Plotter, self).__init__(name='Plotter')
            self.call_function = call_function
            self.interval = interval

        def run(self):
            while True:
                self.call_function()
                libtime.pause(self.interval)

    class LCDWatch(QtGui.QLCDNumber):

        def __init__(self, app, parent=None):
            super(EyeTrackerSetupWindow.LCDWatch, self).__init__(parent=parent)
            self.timer = QtCore.QTimer(self)
            app.connect(self.timer, Qt.SIGNAL('timeout()'), self.show_time)
            self.display('00:00')
            self.started = False

        def show_time(self):
            if self.started:
                time_passed = datetime.datetime.now() - self.time_started
                seconds_passed = int(time_passed.total_seconds())
                self.display('{:02}:{:02}'.format(seconds_passed/60, seconds_passed % 60))

        def start(self):
            self.time_started = datetime.datetime.now()
            self.timer.start(1000)
            self.started = True

        def stop(self):
            self.timer.stop()

    def __init__(self, app, subject_data_event, agent_data_event, calibrate_event, start_event, agent_list, block_list,
                 age_groups=None, windowtitle='Eyetracker Setup Window'):
        super(EyeTrackerSetupWindow, self).__init__()
        self.app = app
        self.eyetracker = None
        self.subject_data_event = subject_data_event
        self.agent_data_event = agent_data_event
        self.calibrate_event = calibrate_event
        self.start_event = start_event
        self.setWindowTitle(windowtitle)
        self.resize(1000, 1000)
        self.move(2000, 100)

        self.pos_x_hist = []
        self.pos_y_hist = []

        self.grid = QtGui.QGridLayout(self)

        # Create participant data input
        self.subject_data_box = QtGui.QGroupBox('Subject Data')
        subject_data_layout = QtGui.QGridLayout(None)

        subject_code_label = QtGui.QLabel('subject code')
        self.subject_code_text = QtGui.QLineEdit()
        # subject_name_label = QtGui.QLabel('name')
        # self.subject_name_text = QtGui.QLineEdit()
        # subject_first_name_label = QtGui.QLabel('first name')
        # self.subject_first_name_text = QtGui.QLineEdit()
        subject_date_label = QtGui.QLabel('date of birth')
        self.subject_date_year = QtGui.QLineEdit()
        self.subject_date_year.setPlaceholderText('YEAR')
        self.subject_date_month = QtGui.QLineEdit()
        self.subject_date_month.setPlaceholderText('MONTH')
        # self.subject_date_day = QtGui.QLineEdit()
        # self.subject_date_day.setPlaceholderText('DAY')
        subject_sex_label = QtGui.QLabel('sex')
        subject_sex_box = QtGui.QGroupBox()
        subject_sex_layout = QtGui.QHBoxLayout()
        self.subject_sex_radio_f = QtGui.QRadioButton('female')
        self.subject_sex_radio_m = QtGui.QRadioButton('male')
        subject_sex_layout.addWidget(self.subject_sex_radio_f)
        subject_sex_layout.addWidget(self.subject_sex_radio_m)
        subject_sex_box.setLayout(subject_sex_layout)
        subject_group_label = QtGui.QLabel('group')
        subject_group_box = QtGui.QGroupBox()
        subject_group_layout = QtGui.QHBoxLayout()
        self.subject_group_radio_autistic = QtGui.QRadioButton('autistic')
        self.subject_group_radio_control = QtGui.QRadioButton('control')
        subject_group_layout.addWidget(self.subject_group_radio_autistic)
        subject_group_layout.addWidget(self.subject_group_radio_control)
        subject_group_box.setLayout(subject_group_layout)
        self.create_subject_button = QtGui.QPushButton('Create Subject')

        subject_data_layout.addWidget(subject_code_label, 0, 0)
        subject_data_layout.addWidget(self.subject_code_text, 0, 1, 1, 2)
        # subject_data_layout.addWidget(subject_name_label, 1, 0)
        # subject_data_layout.addWidget(self.subject_name_text, 1, 1, 1, 3)
        # subject_data_layout.addWidget(subject_first_name_label, 2, 0)
        # subject_data_layout.addWidget(self.subject_first_name_text, 2, 1, 1, 3)
        subject_data_layout.addWidget(subject_date_label, 3, 0)
        subject_data_layout.addWidget(self.subject_date_year, 3, 1)
        subject_data_layout.addWidget(self.subject_date_month, 3, 2)
        # subject_data_layout.addWidget(self.subject_date_day, 3, 3)
        subject_data_layout.addWidget(subject_sex_label, 4, 0)
        subject_data_layout.addWidget(subject_sex_box, 4, 1, 1, 2)
        # subject_data_layout.addWidget(subject_group_label, 5, 0)
        # subject_data_layout.addWidget(subject_group_box, 5, 1, 1, 2)
        subject_data_layout.addWidget(self.create_subject_button, 6, 0, 1, 3)

        self.subject_data_box.setLayout(subject_data_layout)

        # Create system buttons
        system_button_box = QtGui.QGroupBox('System Functions')
        system_button_layout = QtGui.QVBoxLayout(None)

        self.start_button = QtGui.QPushButton('start')
        self.start_button.setDisabled(True)
        quit_button = QtGui.QPushButton('quit')

        system_button_layout.addWidget(self.start_button)
        system_button_layout.addWidget(quit_button)

        system_button_box.setLayout(system_button_layout)

        # Create age selection
        self.age_selection_box = QtGui.QGroupBox('Age Selection')
        age_selection_layout = QtGui.QGridLayout(None)
        self.age_selection_box.setDisabled(True)
        self.age_selection_box.setLayout(age_selection_layout)

        if age_groups:
            age_list_unsorted = [[ages[0], ages[1], group_name] for group_name, ages in age_groups.items()]
            age_list_sorted = []
            for i in range(len(age_list_unsorted)):
                n = 0
                for j in range(len(age_list_unsorted)):
                    if age_list_unsorted[n][0] > age_list_unsorted[j][0]:
                        n = j
                age_list_sorted.append(age_list_unsorted.pop(n))
            self.age_groups = {}
            for age_group in age_list_sorted:
                self.age_groups[age_group[2]] = QtGui.QRadioButton(
                        age_group[2]+' ('+str(age_group[0])+' - '+str(age_group[1])+')')
                age_selection_layout.addWidget(self.age_groups[age_group[2]])
        else:
            self.age_groups = None

        # Agent control
        self.agent_control_box = QtGui.QGroupBox('Agent Control')
        self.agent_control_box.setEnabled(False)
        agent_control_layout = QtGui.QVBoxLayout(None)

        self.agent_list = QtGui.QListWidget(None)
        self.agent_select_button = QtGui.QPushButton('Select Agent')

        for agent in agent_list:
            QtGui.QListWidgetItem(agent, self.agent_list)
        self.agent_list.sortItems()

        experiment_block_box = QtGui.QGroupBox('Experiment Blocks')
        experiment_block_layout = QtGui.QVBoxLayout()
        self.block_button_dict = {}
        for block in block_list:
            block_radio_button = QtGui.QRadioButton(str(block))
            experiment_block_layout.addWidget(block_radio_button)
            self.block_button_dict[str(block)] = block_radio_button
        experiment_block_box.setLayout(experiment_block_layout)

        agent_behavior_box = QtGui.QGroupBox('Agent Behavior')
        self.agent_behavior_radio_pilot = QtGui.QRadioButton('Pilotstudie')
        self.agent_behavior_radio_base1 = QtGui.QRadioButton('Basisstudie 1')
        self.agent_behavior_radio_base1.setChecked(True)
        agent_behavior_layout = QtGui.QVBoxLayout()
        agent_behavior_layout.addWidget(self.agent_behavior_radio_pilot)
        agent_behavior_layout.addWidget(self.agent_behavior_radio_base1)
        agent_behavior_box.setLayout(agent_behavior_layout)

        agent_control_layout.addWidget(self.agent_list)
        agent_control_layout.addWidget(experiment_block_box)
        agent_control_layout.addWidget(agent_behavior_box)
        agent_control_layout.addWidget(self.agent_select_button)

        self.agent_control_box.setLayout(agent_control_layout)

        # eyetracker control
        eyetracker_control_box = QtGui.QGroupBox('Eyetracker Control')
        eyetracker_control_layout = QtGui.QGridLayout(None)

        self.calibrate_button = QtGui.QPushButton('calibrate')
        self.calibrate_button.setDisabled(True)
        self.skip_calibrate_button = QtGui.QPushButton('skip calibration')
        self.skip_calibrate_button.setDisabled(True)
        self.start_recording_button = QtGui.QPushButton('start recording')
        self.start_recording_button.setDisabled(True)

        eyetracker_control_layout.addWidget(self.start_recording_button)
        eyetracker_control_layout.addWidget(self.calibrate_button)
        eyetracker_control_layout.addWidget(self.skip_calibrate_button)

        eyetracker_control_box.setLayout(eyetracker_control_layout)

        # create eye position info
        eye_position_graph_box = QtGui.QGroupBox('eye position')
        eye_position_graph_layout = QtGui.QGridLayout(None)

        self.eye_position_button = QtGui.QPushButton('None')
        color = self.color_gradient(None, None, None, None, None)
        # self.eye_position_button.setPalette(QtGui.QPalette(QtGui.QColor(0, 255, 0)))
        self.eye_position_button.setStyleSheet('background_colour: red')

        eye_position_graph_layout.addWidget(self.eye_position_button)
        eye_position_graph_box.setLayout(eye_position_graph_layout)

        # create progress bar
        progress_bar_box = QtGui.QGroupBox('Progress')
        progress_bar_layout = QtGui.QGridLayout(None)

        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)

        progress_bar_layout.addWidget(self.progress_bar)
        progress_bar_box.setLayout(progress_bar_layout)

        # create eye tracker status window
        eyetracker_status_box = QtGui.QGroupBox('Eyetracker Status')
        eyetracker_status_layout = QtGui.QGridLayout(None)

        self.stimtracker_status_button = QtGui.QPushButton('Stimtracker status')
        self.stimtracker_status_button.setDisabled(True)
        # self.stimtracker_status_button.setPalette(QtGui.QPalette(QtGui.QColor(255, 255, 0)))
        self.stimtracker_status_button.setStyleSheet('background-color:yellow')

        self.watch_overall = self.LCDWatch(self.app)
        self.watch_overall.start()

        self.watch_experiment = self.LCDWatch(self.app)

        eyetracker_status_layout.addWidget(self.stimtracker_status_button)
        eyetracker_status_layout.addWidget(self.watch_overall)
        eyetracker_status_layout.addWidget(self.watch_experiment)

        eyetracker_status_box.setLayout(eyetracker_status_layout)

        # add everything to the main grid
        if age_groups:
            self.grid.addWidget(self.subject_data_box, 0, 0)
            self.grid.addWidget(self.age_selection_box, 1, 0)
        else:
            self.grid.addWidget(self.subject_data_box, 0, 0, 2, 1)
        self.grid.addWidget(self.agent_control_box, 0, 1, 2, 1)
        self.grid.addWidget(eyetracker_control_box, 0, 2, 2, 1)
        self.grid.addWidget(system_button_box, 0, 3, 2, 1)
        self.grid.addWidget(eyetracker_status_box, 0, 4, 2, 1)
        # self.grid.addWidget(eye_position_graph_box, 2, 0, 1, 1)
        self.grid.addWidget(progress_bar_box, 2, 0, 1, 5)

        self.setLayout(self.grid)

        # Connect GUI fields to funcitons
        self.app.connect(quit_button, Qt.SIGNAL('pressed()'), self.quit)
        self.app.connect(self.create_subject_button, Qt.SIGNAL('pressed()'), self.create_subject)
        self.app.connect(self.calibrate_button, Qt.SIGNAL('pressed()'), lambda: self.calibrate(True))
        self.app.connect(self.skip_calibrate_button, Qt.SIGNAL('pressed()'), lambda: self.calibrate(False))
        self.app.connect(self.start_button, Qt.SIGNAL('pressed()'), self.start)
        self.app.connect(self.eye_position_button, Qt.SIGNAL('pressed()'), self.plot_eye_position)
        self.app.connect(self.start_recording_button, Qt.SIGNAL('pressed()'), self.start_recording)
        self.app.connect(self.agent_select_button, Qt.SIGNAL('pressed()'), self.create_agent)

        self.show()

    def quit(self):
        self.app.quit()

    def set_eyetracker(self, eyetracker):
        self.eyetracker = eyetracker
        self.calibrate_button.setEnabled(True)
        # self.start_recording_button.setEnabled(True)
        self.skip_calibrate_button.setEnabled(True)
        print(self.eyetracker)

    def start_recording(self):
        # self.start_recording_button.setDisabled(True)
        self.eyetracker.start_recording()
        self.plotter = self.Plotter(self.plot_eye_position, 1000)
        self.plotter.start()

    def color_gradient(self, value, minimum, maximum, min_color, max_color):
        return (0, 255, 0)

    def plot_eye_position(self):
        eye_position = self.eyetracker.controller.gazeData[-1].LeftEyePosition3DRelative
        eye_position_z = eye_position.z
        self.eye_position_button.setText(str(eye_position_z))

    def start(self):
        self.start_event.set()
        self.start_button.setDisabled(True)
        self.agent_behavior_radio_pilot.setDisabled(True)
        self.agent_behavior_radio_base1.setDisabled(True)

    def create_subject(self):
        self.subject = {}
        if self.subject_code_text.text() == '':
            QtGui.QMessageBox(3, 'No subject code given!', 'Please enter a subject code.').exec_()
            return
        else:
            self.subject['code'] = str(self.subject_code_text.text())
        if self.subject_date_year.text() == '':
            QtGui.QMessageBox(3, 'No year of birth given!', 'Please enter a year of birth.').exec_()
            return
        else:
            try:
                year = int(self.subject_date_year.text())
            except ValueError:
                QtGui.QMessageBox(3, 'Invalid year of birth!', 'Please enter a valid year of birth.').exec_()
                return
        if self.subject_date_month.text() == '':
            QtGui.QMessageBox(3, 'No month of birth given!', 'Please enter a month of birth.').exec_()
            return
        else:
            try:
                month = int(self.subject_date_month.text())
            except ValueError:
                QtGui.QMessageBox(3, 'Invalid month of birth!', 'Please enter a valid month of birth.').exec_()
                return
        try:
            self.subject['date'] = datetime.date(year, month, 1)
        except ValueError:
            QtGui.QMessageBox(3, 'Invali date of birth!', 'Please enter a valid date of birth.' +
                              '\nThe year must be between 1 and 9999.\nThe month must be between 1 and 12.').exec_()
            return
        age = datetime.date.today() - self.subject['date']
        if age.days > 365.25*60 or age.days < 365.25*3:
            message = QtGui.QMessageBox(2, 'Age out of range.',
                                        'The subjects age is out of the set range of 3 to 60 years.',
                                        QtGui.QMessageBox.Ignore | QtGui.QMessageBox.Ok)
            resp = message.exec_()
            if resp == 1024:
                return
        if not (self.subject_sex_radio_f.isChecked() or self.subject_sex_radio_m.isChecked()):
            QtGui.QMessageBox(3, 'No sex selected!', 'Please select either female or male.').exec_()
            return
        else:
            if self.subject_sex_radio_f.isChecked():
                self.subject['sex'] = 'f'
            else:
                self.subject['sex'] = 'm'
        # if not (self.subject_group_radio_autistic.isChecked() or self.subject_group_radio_control.isChecked()):
        #     QtGui.QMessageBox(3, 'No group selected!', 'Please select either autistic or control.').exec_()
        #     return
        # else:
        #     if self.subject_group_radio_autistic.isChecked():
        #         self.subject['group'] = 'a'
        #     else:
        #         self.subject['group'] = 'c'

        self.subject_data_box.setEnabled(False)
        self.agent_control_box.setEnabled(True)
        self.subject_data_event.set()

    def create_agent(self):
        self.agent_selection = {}
        self.agent_selection['block'] = None
        for button_text, button in self.block_button_dict.items():
            if button.isChecked():
                self.agent_selection['block'] = button_text
        if self.agent_behavior_radio_pilot.isChecked():
            self.agent_selection['agent_behavior'] = str(self.agent_behavior_radio_pilot.text())
        elif self.agent_behavior_radio_base1.isChecked():
            self.agent_selection['agent_behavior'] = str(self.agent_behavior_radio_base1.text())
        else:
            self.agent_selection['agent_behavior'] = None
        if self.agent_list.currentItem():
            self.agent_selection['agent'] = str(self.agent_list.currentItem().text())
        else:
            self.agent_selection['agent'] = str(self.agent_list.item(0).text())
        self.agent_control_box.setEnabled(False)
        if self.age_groups:
            for age_group, button in self.age_groups.items():
                if button.isChecked():
                    self.agent_selection['age_group'] = age_group
                    break
            self.age_selection_box.setEnabled(False)
        else:
            self.agent_selection['age_group'] = None
        self.agent_data_event.set()

    def calibrate(self, do_calibrate):
        self.calibrate_button.setEnabled(False)
        self.skip_calibrate_button.setEnabled(False)
        self.calibrate_event.set(msg=do_calibrate)
        print(do_calibrate)
        self.calibrate_event.clear()
        self.start_button.setEnabled(True)


class EyeTrackerGui(threading.Thread):

    def __init__(self, subject_data_event, agent_data_event, agent_list, block_list, age_groups=None):
        super(EyeTrackerGui, self).__init__(name='EyeTrackerGui')
        self.subject_data_event = subject_data_event
        self.agent_data_event = agent_data_event
        self.agent_list = agent_list
        self.block_list = block_list
        self.age_groups = age_groups
        self.start_event = threading.Event()
        self.calibrate_event = MyEvent()

    def run(self):
        app = QtGui.QApplication(sys.argv)
        app.setApplicationName('EyeTrackerGui')
        self.eyetracker_setup_window = EyeTrackerSetupWindow(app, self.subject_data_event, self.agent_data_event,
                                                             self.calibrate_event, self.start_event, self.agent_list,
                                                             self.block_list, self.age_groups)
        # print(self.eyetracker_setup_window)
        sys.exit(app.exec_())

    def set_eyetracker(self, eyetracker):
        self.eyetracker_setup_window.set_eyetracker(eyetracker)

    def get_subject_data(self):
        return self.eyetracker_setup_window.subject

    def get_agent_data(self):
        return self.eyetracker_setup_window.agent_selection

    def preset_age_group(self, age_group):
        if self.eyetracker_setup_window.age_groups:
            self.eyetracker_setup_window.age_selection_box.setEnabled(True)
            self.eyetracker_setup_window.age_groups[age_group].setChecked(True)

    def is_block_button_checked(self):
        for name, button in self.eyetracker_setup_window.block_button_dict.items():
            if button.isChecked():
                return True
        return False
