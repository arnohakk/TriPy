#!/usr/bin/python2

# -*- coding: utf-8 -*-

#################################
# Main file to start a paradigm #
#################################

import pygaze
import sys
from pygaze import libtime, libinput, libscreen, eyetracker
from constants import *
try:
    from constants_local import *
except:
    print(sys.exc_info())
from threading import Thread, Event, Lock
from framework import pygaze_framework, eyetracker_gui, jap_pygaze_framework
from framework.stuff import colored_text, encapsulate_text, StopWatch, print_threads
from framework.tools import make_sequence_from_list
import os
import shutil
import time
import datetime
import random
import json
import pprint
import pickle
from numpy.random import choice, uniform
from numpy import asarray, array, repeat
from agents import AgentMacroBehavior, BlinkingAgent_Dict, Passive_Agent_Dict, IJA_Agent_Dict
from agents import RJA_Agent_Dict, Mixed_Agent_Dict
from experiment_parameters import *
try:
    from experiment_parameters_local import *
except:
    print(sys.exc_info())
from framework.stimtracker_test import count_stimtracker_signal_switches
import argparse


class Time(Thread):
    """
    """

    def __init__(self, time_event):
        super(Time, self).__init__()
        self.time = 0
        self.time_event = time_event

    def run(self):
        while True:
            self.time_event.wait()
            time = libtime.get_time()
            print(time - self.time)
            self.time = time
            self.time_event.clear()


class Stimtracker_Test(Thread):
    """ Class running a Thread() performing a test whether StimTacker is working correctly by showing a trigger pixelfield
    on the screen at the stimtracker location. Will show its result in GUI.
    """

    def __init__(self, test_event, dump_file, qbutton=None, verbose=False, name='Stimtracker_Tester'):
        super(Stimtracker_Test, self).__init__(name=name)
        self.test_event = test_event
        self.dump_file = dump_file
        self.qbutton = qbutton
        self.verbose = verbose
        self.is_running = True
        self.daemon = True

    def run(self):
        self.test_event.wait()
        self.test_event.clear()
        if self.verbose:
            print(encapsulate_text('testing stimtracker', color='red'))
        n_signal_switches, last_signal = count_stimtracker_signal_switches(self.dump_file)
        print(self.qbutton)

        # Set StimTracker GUI indicator color
        if n_signal_switches > 0:
            self.qbutton.setStyleSheet('background-color:green')
        else:
            self.qbutton.setStyleSheet('background-color:red')

        if self.verbose:
            if n_signal_switches > 0:
                print(encapsulate_text('Succsess: ' + str(n_signal_switches) + ' signal switches', color='green'))
            else:
                print(encapsulate_text('no signal switches, only signal: ' + str(last_signal), color='red'))


class JAP_Experiment:
    """Class running the actual experiment, for parameter options see documentation of parser arguments. Will import
    corresoping file 'experiment_name' from subdir studies/ with --exp_tpye 'experiment_name'

    """

    def __init__(self,  test=False, fast_forward=False, skip_instructions=False, skip_key_input=False,
                 screenshots=False, code=None, gamify=False, block_name=None, auto_create=False, draw_aois=False,
                 aoi_border_size=5, reload_save=False, delete_test_prob=False):

        #####################################################
        # Initialize and start GUI FOR EXPERIMENTAL CONTROL #
        #####################################################

        # Create events to wait until data is entered
        subject_data_event = pygaze_framework.MyEvent()
        agent_data_event = Event()
        block_name_list = []

        # Get names to select from displayed in GUI
        for block in JAP_BLOCK_LIST:
            block_name_list.append(block['name'])

        # Start GUI
        self.gui = eyetracker_gui.EyeTrackerGui(subject_data_event, agent_data_event, JAP_AGT_DIR.keys(),
                                                block_name_list, JAP_AGE_GROUPS)
        self.gui.start()

        # Initialize Pygaze keyboard and get accepted keys list
        self.keyboard = libinput.Keyboard()
        self.keyboard.set_keylist()
        self.new_screens = True

        # If set (-d), delete test proband 1337_H4x0r data when starting the paradigm
        if delete_test_prob:
            base_path = os.getcwd()
            dir_path = os.path.join(base_path, 'logs/1337_H4x0r')
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        else:
            print('No test data deleted')

        # If set (-r), load last used participant data
        if reload_save:
            with open('save.pickle', 'r') as save_file:
                saved_data = pickle.load(save_file)
            print(saved_data)
            libtime.pause(400)
            self.gui.eyetracker_setup_window.subject_code_text.setText(saved_data['subject']['code'])
            self.gui.eyetracker_setup_window.subject_date_year.setText(str(saved_data['subject']['date'].year))
            self.gui.eyetracker_setup_window.subject_date_month.setText(str(saved_data['subject']['date'].month))
            if saved_data['subject']['sex'] == 'm':
                self.gui.eyetracker_setup_window.subject_sex_radio_m.setChecked(True)
            else:
                self.gui.eyetracker_setup_window.subject_sex_radio_f.setChecked(True)

        # If set(-), create test particiapnt
        if test:
            libtime.pause(400)
            if code:
                self.gui.eyetracker_setup_window.subject_code_text.setText(code)
            else:
                self.gui.eyetracker_setup_window.subject_code_text.setText('1337_H4x0r')
            self.gui.eyetracker_setup_window.subject_date_year.setText('1970')
            self.gui.eyetracker_setup_window.subject_date_month.setText('1')
            self.gui.eyetracker_setup_window.subject_sex_radio_m.setChecked(True)
            # self.gui.eyetracker_setup_window.subject_group_radio_autistic.setChecked(True)
            self.gui.eyetracker_setup_window.create_subject()


        # Wait for particiapnt data input by experimentor
        subject_data_event.wait()
        subject_data = self.gui.get_subject_data()
        # Compute age group
        subject_age = datetime.date.today() - subject_data['date']
        subject_age = subject_age.total_seconds() / (60*60*24*365.25)
        age_group = None
        for group, age in JAP_AGE_GROUPS.items():
            if subject_age >= age[0] and subject_age <= age[1]:
                age_group = group
                self.gui.preset_age_group(age_group)
                break
        # Make sure, correct age group is said
        if reload_save:
            self.gui.preset_age_group(saved_data['agent_data']['age_group'])

        # Allow experimentor to select an experimental block
        if block_name:
            self.gui.eyetracker_setup_window.block_button_dict[block_name].setChecked(True)
        else:
            if os.path.isdir(os.path.join('logs', self.gui.get_subject_data()['code'])):
                block_dir_list = os.listdir(os.path.join('logs', self.gui.get_subject_data()['code']))
                for block_name in block_name_list:
                    if block_name not in block_dir_list:
                        self.gui.eyetracker_setup_window.block_button_dict[block_name].setChecked(True)
                        break
            else:
                self.gui.eyetracker_setup_window.block_button_dict[block_name_list[0]].setChecked(True)

        # IF set(??), set
        if auto_create:
            if not self.gui.eyetracker_setup_window.agent_list.currentItem():
                if subject_data['sex'] == 'f':
                    sex_keyword = 'female'
                else:
                    sex_keyword = 'male'
                n_list_items = self.gui.eyetracker_setup_window.agent_list.count()
                n_item = 0
                for i in range(n_list_items):
                    result = str(self.gui.eyetracker_setup_window.agent_list.item(i).text()).find(sex_keyword)
                    if result == 0:
                        n_item = i
                        break
                self.gui.eyetracker_setup_window.agent_list.setCurrentItem(
                    self.gui.eyetracker_setup_window.agent_list.item(n_item))
            if not self.gui.is_block_button_checked():
                self.gui.eyetracker_setup_window.block_button_dict[
                        random.choice(self.gui.eyetracker_setup_window.block_button_dict.keys())].setChecked(True)
            self.gui.eyetracker_setup_window.create_agent()
        agent_data_event.wait()
        agent_data = self.gui.get_agent_data()
        age_group = agent_data['age_group']

        # Select chosen experimental block information
        block_chosen = None
        for block in JAP_BLOCK_LIST:
            if block['name'] == agent_data['block']:
                block_chosen = block
                break

        # Check if subject data already exists
        if not test:
            if (subject_data['code'] in os.listdir(JAP_LOG_DIR) and
                    agent_data['block'] in os.listdir(os.path.join(JAP_LOG_DIR, subject_data['code']))):
                print(encapsulate_text('Subject code allready in use!', color='red', background='yellow'))
                exit()

            if (subject_data['code'] in os.listdir(JAP_LOG_DIR) and
                    agent_data['block'] in os.listdir(os.path.join(JAP_LOG_DIR, subject_data['code'])) and
                    'H4x0r' not in subject_data['code']):
                print(encapsulate_text('Subject code already used!', color='red', background='yellow'))
                exit()

        # Save subject and agent data
        with open('save.pickle', 'w+') as save_file:
            pickle.dump({'subject': subject_data, 'agent_data': agent_data}, save_file)

        # Initialize EventHandler
        self.event_handler = pygaze_framework.EventHandler()
        # Initialize KeyInputHandler(??)
        # key_input_handler = pygaze_framework.EventHandler.KeyInputHandler()
        # key_input_handler.start()

        # Initialize ObjectPicker to select objects to be presented
        self.object_picker = jap_pygaze_framework.ObjectPicker(JAP_TAR_NAMES, JAP_TAR_DIR_LIST)

        ###############################################################
        # Create sequence from information given in study config file #
        ###############################################################

        if block_chosen['sequence']:
            behavioral_sequence = block_chosen['sequence']
        else:
            while True:
                print('making sequence')
                if args.exp_type == 'ja_nirs':
                    ok, behavioral_sequence = make_sequence_from_list(block_chosen['states'],
                                                                      block_chosen['times_per_state'])
                elif args.exp_type == 'basic':
                    ok, behavioral_sequence = make_sequence_from_list(block_chosen['states'],
                                                                                block_chosen['times_per_state'])
                else:
                    raise Exception('Sequence generation not specified for this study type!')
                if ok:
                    print('made sequence')
                    break
        # If set, shorten sequence below certain age
        if (JAP_AGE_DEPENDENT_SEQUENCE[0] and age[1] <= JAP_AGE_DEPENDENT_SEQUENCE[1] and
            block_chosen['name'][0] != JAP_AGE_DEPENDENT_SEQUENCE[3]):
                behavioral_sequence = behavioral_sequence[:-JAP_AGE_DEPENDENT_SEQUENCE[2]]
                print('Sequence shortened')

        ###########################################
        # SCREEN CREATION & PRESENTATION HANDLING #
        ###########################################

        # Get information which trial type are actually present in current run,
        # only screens for these trial types will be created
        states2draw = []
        if 'trial_type' in behavioral_sequence[0]:
            for i in range(0, len(behavioral_sequence)):
                state = behavioral_sequence[i]['trial_type']

                if state not in states2draw:
                    states2draw.append(state)

        for seq in behavioral_sequence: #(??) Kann das nach oben verschoben werden?
            # Set max macro state duration
            if seq['trial_param'].get('accept_keypress'):
                seq['trial_param']['run_time'] = JAP_BLOCK_DUR_DICT[age_group][0]
            else:
                seq['trial_param']['run_time'] = JAP_BLOCK_DUR_DICT[age_group][1]

            # Set correct aoi of agent as trial parameter
            if seq['trial_type'] is not None:
                seq['trial_param']['correct_aoi'] = JAP_TRIAL_TYPES[seq['trial_type']]['correct_aoi']

        # Initialize ScreenHandler to manage screens to be display
        self.scr_hdlr = jap_pygaze_framework.JAP_ScreenHandler(JAP_AGT_DIR['male_test'], JAP_AGT_SIZE, JAP_AGT_POS,
                                                               JAP_AGT_DICT, JAP_TAR_SIZE, JAP_TAR_POS,
                                                               JAP_STIMTRACKER_PARAMETER, JAP_MUCAP_DICT,
                                                               JAP_INSTR_TEXT[age_group], self.object_picker, DISPSIZE,
                                                               JAP_AGT_START_GAZE, JAP_TRIAL_TYPES, age_group,
                                                               JAP_MIN_INSTR_READ_TIME, JAP_TXT_B1, JAP_WELCOME_TEXT,
                                                               JAP_TAR_DIR_LIST, behavioral_sequence, JAP_NIRS,
                                                               CORRECT_COLOUR, BORDER_WIDTH_CIRCLE, BORDER_WIDTH_AOI,
                                                               SCREENNR, resize_proportional=True)

        self.scr_hdlr.make_fix_cross_screen()  # Make a screen with a fixation cross only
        self.draw = pygaze_framework.MyEvent() # Create an event that is fired when screen needs to be updated on the display.
        draw_lock = Lock()  # Lock to prevent that more than one thread is trying to change the screen to prevent weird agent behavior
        self.draw.msg2 = JAP_AGT_START_GAZE  # Set start gaze for draw message
        self.wait_4_instr = Event()  # Event to wait for key press by participant to continue in experimental flow.
        self.wait_4_instr.clear()

        # Create logger dict
        logger_dict = {
                'screen_recorder': [pygaze_framework.MyEvent(), JAP_SCR_REC_COLS],
                'ija_recorder': [pygaze_framework.MyEvent(), ['time_experiment', 'time_tracker', 'time_agent', 'msg',
                                                              'target']],
                'rja_recorder': [pygaze_framework.MyEvent(), ['time_experiment', 'time_tracker', 'time_agent', 'msg',
                                                              'target']],
                'fixation_recorder': [pygaze_framework.MyEvent(), ['time_experiment', 'time_tracker', 'time_fixation',
                                                                   'pos_fixation', 'AOI']],
                'questionnaire_recorder': [pygaze_framework.MyEvent(), ['time_experiment', 'time_tracker',
                                                                        'time_presented', 'time_key_press', 'agent',
                                                                        'question', 'answer']],
                'score_recorder': [pygaze_framework.MyEvent(), ['time_experiment', 'time_tracker', 'time_event',
                                                                'score']],
                'agent_rating_recorder': [pygaze_framework.MyEvent(), ['time_experiment', 'time_tracker', 'agent',
                                                                       'question', 'rating_history']]}
        # Initialize eyetracker (Only checked for Tobii SDK)
        if JAP_TRACKING:
            self.tracker = eyetracker.EyeTracker(self.scr_hdlr.display)
            self.gui.set_eyetracker(self.tracker)
            if TRACKERTYPE == 'tobii':
                # initialize thread for fixation detection
                fixation_detector = pygaze_framework.EventHandler.Fixation_Detector(
                        self.tracker, logger_dict['fixation_recorder'][0])
                # initialize data logging using pygaze framework routines
                tobii_save_event = Event()
                self.logger = jap_pygaze_framework.JAP_LogManager(JAP_LOG_DIR, agent_data['block'],
                                                                  tracker=self.tracker,
                                                                  participant_data=self.gui.get_subject_data(),
                                                                  age_group=age_group, mucap_dir=JAP_MUCAP_DIR,
                                                                  mucap_marker=JAP_VIDEO_MARKER,
                                                                  mucap_wmv=JAP_VIDEO,
                                                                  fixation_data=fixation_detector.fixation_list,
                                                                  log_dict=logger_dict, screenshots=True,
                                                                  tobii_save_event=tobii_save_event)
                stimtracker_test = Stimtracker_Test(tobii_save_event, self.logger.tobii_dumper.dump_file,
                                                    self.gui.eyetracker_setup_window.stimtracker_status_button, True)
                stimtracker_test.start()
            else:
                print('Using not tested eyetracking system!')
                self.logger = pygaze_framework.LogManager(JAP_LOG_DIR, None, self.gui.get_subject_data(), True,
                                                          screenshots=True)

            self.logger.start()
            self.event_handler.tracker = self.tracker

        # Save sequence
        sequence_path = os.path.join('logs', self.logger.data['code'], 'sequence')
        if os.path.isfile(sequence_path):
            with open(sequence_path, 'r') as sequence_file:
                sequence_dict = json.load(sequence_file)
        else:
            sequence_dict = []
        sequence_dict.append({'name': block_chosen['name'], 'sequence': behavioral_sequence})
        with open(sequence_path, 'w') as sequence_file:
            json.dump(sequence_dict, sequence_file, indent=4)

        self.gui.eyetracker_setup_window.progress_bar.setMaximum(len(behavioral_sequence))  # Scale progress bar in GUI
        block_progress = 0  # Counter for block progress

        # If given, prepare video presentation
        win = pygaze.expdisplay
        movs = {}
        for vid in JAP_VIDS:
            movs[vid] = pygaze_framework.ScreenHandler.Movie(JAP_VIDS[vid], win, self.scr_hdlr.display, JAP_REWIND_VID,
                                                             JAP_PLAY_TIME)
        ##########################
        # EYETRACKER CALIBRATION #
        ##########################

        if JAP_TRACKING:
            calibration_file_path = os.path.join(self.logger.data_dir, self.logger.data['code']+'_calibration')
            if not fast_forward:
                do_calibrate = self.gui.calibrate_event.wait()
                if do_calibrate:
                    draw_time = self.scr_hdlr.make_and_draw_screen(JAP_CALIB_TXT['begin'])
                    self.keyboard.get_key(timeout=None, flush=True)
                    calibration_success = False
                    while not calibration_success:
                        calibration_success = self.tracker.calibrate()
                        if not calibration_success:
                            self.scr_hdlr.make_and_draw_screen(JAP_CALIB_TXT['no_success'], color='red')
                            self.keyboard.get_key(timeout=None, flush=True)

                    blank_screen = libscreen.Screen()
                    blank_screen.clear()
                    self.scr_hdlr.show(blank_screen)

                    # Save calibration parameter
                    calibrated_parameters = {}
                    calibrated_parameters['samplerate'] = self.tracker.samplerate
                    calibrated_parameters['sampletime'] = self.tracker.sampletime
                    calibrated_parameters['accuracy_pix'] = self.tracker.pxaccuracy
                    calibrated_parameters['fixthreshold'] = {}
                    calibrated_parameters['fixthreshold']['deg'] = self.tracker.fixtresh
                    calibrated_parameters['fixthreshold']['pix'] = self.tracker.pxfixtresh
                    calibrated_parameters['speedthreshold'] = {}
                    calibrated_parameters['speedthreshold']['deg'] = self.tracker.spdtresh
                    calibrated_parameters['speedthreshold']['pix'] = self.tracker.pxspdtresh
                    calibrated_parameters['accuracythreshold'] = {}
                    calibrated_parameters['accuracythreshold']['deg'] = self.tracker.accthresh
                    calibrated_parameters['accuracythreshold']['pix'] = self.tracker.pxacctresh
                    calibrated_parameters['distance'] = self.tracker.screendist
                    with open(calibration_file_path, 'w') as calib_file:
                        json.dump(calibrated_parameters, calib_file, indent=4)
                    self.gui.calibrate_event.set()
                    draw_time = self.scr_hdlr.make_and_draw_screen(JAP_CALIB_TXT['end'])

                else:
                    if os.path.isfile(calibration_file_path):
                        with open(calibration_file_path, 'r') as calib_file:
                            calibrated_parameters = json.load(calib_file)
                        pprint.pprint(calibrated_parameters)
                        self.tracker.samplerate = calibrated_parameters['samplerate']
                        self.tracker.sampletime = calibrated_parameters['sampletime']
                        self.tracker.screendist = calibrated_parameters['distance']
                        self.tracker.pxaccuracy = calibrated_parameters['accuracy_pix']
                        self.tracker.fixtresh = calibrated_parameters['fixthreshold']['deg']
                        self.tracker.pxfixtresh = calibrated_parameters['fixthreshold']['pix']
                        self.tracker.spdtresh = calibrated_parameters['speedthreshold']['deg']
                        self.tracker.pxspdtresh = calibrated_parameters['speedthreshold']['pix']
                        self.tracker.accthresh = calibrated_parameters['accuracythreshold']['deg']
                        self.tracker.pxacctresh = calibrated_parameters['accuracythreshold']['pix']
                    else:
                        self.tracker.pxfixtresh = 60.
            else:
                if os.path.isfile(calibration_file_path):
                    with open(calibration_file_path, 'r') as calib_file:
                        calibrated_parameters = json.load(calib_file)
                    pprint.pprint(calibrated_parameters)
                    self.tracker.samplerate = calibrated_parameters['samplerate']
                    self.tracker.sampletime = calibrated_parameters['sampletime']
                    self.tracker.screendist = calibrated_parameters['distance']
                    self.tracker.pxaccuracy = calibrated_parameters['accuracy_pix']
                    self.tracker.fixtresh = calibrated_parameters['fixthreshold']['deg']
                    self.tracker.pxfixtresh = calibrated_parameters['fixthreshold']['pix']
                    self.tracker.spdtresh = calibrated_parameters['speedthreshold']['deg']
                    self.tracker.pxspdtresh = calibrated_parameters['speedthreshold']['pix']
                    self.tracker.accthresh = calibrated_parameters['accuracythreshold']['deg']
                    self.tracker.pxacctresh = calibrated_parameters['accuracythreshold']['pix']
                else:
                    self.tracker.pxfixtresh = 60.

        ########################################################################
        # If set, CONNECTION TO NOLDUS FACEREADER: START ANALYZING AND LOGGING #
        ########################################################################
        print('LOLO')
        if JAP_FACE_READING:
            face_reader = facereader.FaceReader('134.130.12.120', 9090)
            face_reader.start_detailed_log()
            face_reader.start_analyzing()

        # Wait for experimentator to start experiment
        if not fast_forward:
            self.gui.start_event.wait()

        show_rating_scale = False #(??)
        end_on_key_input = False
        print('LOLO1')
        # if self.gui.eyetracker_setup_window.agent_behavior_radio_pilot.isChecked(): (??)
        #     print(encapsulate_text('Pilotstudie', color='red', background='green'))
        # if self.gui.eyetracker_setup_window.agent_behavior_radio_base1.isChecked():
        #     show_rating_scale = True
        #     end_on_key_input = True
        #     print(encapsulate_text('Basisstudie 1', color='red', background='green'))

        fixation_detector.add_multiple_aois(JAP_AGT_AOI)  # Add AOIs for fixation detector
        target_dict = self.object_picker.get_new_targets()  # Get objects to show

        # Create all screen that might be shown in a experiment (only with one set of objects)
        self.scr_hdlr.make_all_screens(target_dict, states2draw, aoi_tol=JAP_AOI_TOL)
        self.event_handler.time = 500 #(??)
        self.cur_agt = JAP_AGT_START_GAZE  #(??) Das ist oben nochma

        agent_finished = Event()  # Event for signaling that time for current macro state is up
        macro_finished = Event()  # Event for signaling macro state sequence end
        self.blinking = Lock()  # Event to check whether agent is currently blinking
        agent_break_event = Event() # (??)
        print('LOLO2')
        # Initialize and state class for gamification (score tracking)
        game_hub = jap_pygaze_framework.GameHub(log_event=logger_dict['score_recorder'][0])
        game_hub.start()

        ################################
        # SETUP AGENT'S MACRO BEHAVIOR #
        ################################
        print('LOLO3')
        blinking_agent = {'screen_handler': self.scr_hdlr, 'draw_event': self.draw, 'draw_lock': draw_lock,
                          'blink_event': self.blinking, 'blink_interval': JAP_AGT_BLINK_INTERVAL, 'blink_duration':
                          JAP_AGT_BLINK_DURATION, 'name': 'BlinkingAgent', 'class': BlinkingAgent_Dict}

        passive_agent_object_oriented = {'cur_agt': self.cur_agt, 'draw_event': self.draw, 'draw_lock': draw_lock,
                                         'blink_event': self.blinking, 'transition_matrix': JAP_A_OO_TRANS_MAT,
                                         'fixation_time': JAP_A_OO_TIMINGS, 'finished_event': agent_finished,
                                         'break_event': agent_break_event, 'show_vid_always': JAP_ALWAYS_SHOW_VID,
                                         'show_points': JAP_SHOW_POINTS, 'questionnaire': JAP_QUESTIONNAIRE, 'name':
                                         'OO_Agent', 'class': Passive_Agent_Dict}

        passive_agent_partner_oriented = {'cur_agt': self.cur_agt, 'draw_event': self.draw, 'draw_lock': draw_lock,
                                          'blink_event': self.blinking, 'transition_matrix': JAP_A_PO_TRANS_MAT,
                                          'fixation_time': JAP_A_PO_TIMINGS, 'finished_event': agent_finished,
                                          'break_event': agent_break_event, 'show_vid_always': JAP_ALWAYS_SHOW_VID,
                                          'show_points': JAP_SHOW_POINTS, 'questionnaire': JAP_QUESTIONNAIRE, 'name':
                                          'PO_Agent', 'class': Passive_Agent_Dict}

        passive_agent_introspective = {'cur_agt': self.cur_agt, 'draw_event': self.draw, 'draw_lock': draw_lock,
                                       'blink_event': self.blinking, 'transition_matrix': JAP_A_INT_TRANS_MAT,
                                       'fixation_time': JAP_A_INT_TIMINGS, 'finished_event': agent_finished,
                                       'break_event': agent_break_event, 'show_vid_always': JAP_ALWAYS_SHOW_VID,
                                       'show_points': JAP_SHOW_POINTS, 'questionnaire': JAP_QUESTIONNAIRE, 'name':
                                       'INT_Agent', 'class': Passive_Agent_Dict}

        ija_agent = {'fixation_detector': fixation_detector, 'cur_agt': self.cur_agt,
                     'draw_event': self.draw, 'draw_lock': draw_lock, 'blink_event': self.blinking,
                     'transition_matrix': JAP_TRANS_MAT_IJA, 'start_gaze': JAP_AGT_START_GAZE,
                     'time_to_bore': JAP_AGT_T_OBJ_IJA, 'agent_straight': JAP_AGT_T_STRAIGHT,
                     'subject_fixation_time': JAP_SUBJ_FIX_T, 'agent_reset_time': JAP_AGT_T_LOOK_S_AGAIN,
                     'ja_init_waiting_time': JAP_INITIAL_JA_WAITING_TIME, 'ja_init_aois':
                     JAP_INITIAL_JA_AOIS, 'translation_dict': JAP_TRANS_DICT, 'p_correct_object':
                     JAP_P_IJA_AGT_CORRECT_CHOICE, 'possible_aois': JAP_AGT_IJA_AOIS, 'break_trial_if_no_mg':
                     JAP_BREAK_TRIAL_IF_NO_MG, 'single_chance': JAP_SINGLE_CHANCE, 'get_attention_parameters':
                     JAP_IJA_GET_ATTENTION_PARAMETERS, 'show_vid': JAP_SHOW_VID_IJA, 'show_vid_always':
                     JAP_ALWAYS_SHOW_VID, 'show_points': JAP_SHOW_POINTS, 'highlight_obj': JAP_HL_OBJ_IJA,
                     'correct_feedback': JAP_P_CORRECT_FEEDBACK, 'questionnaire': JAP_QUESTIONNAIRE, 'log_event':
                     logger_dict['ija_recorder'][0], 'finished_event': agent_finished, 'break_event':
                     agent_break_event, 'game_event': game_hub.event, 'name': 'IJA_Agent', 'class': IJA_Agent_Dict}
        rja_agent = {'fixation_detector': fixation_detector, 'cur_agt': self.cur_agt, 'draw_event': self.draw,
                     'draw_lock': draw_lock, 'blink_event': self.blinking, 'translation_dict': JAP_TRANS_DICT2,
                     'follow_lag': JAP_AGT_FOLLOW_LAG, 'follow_prob': JAP_AGT_FOLLOW_PROB, 'reset_lag':
                     JAP_AGT_RESET_LAG, 'start_gaze': JAP_AGT_START_GAZE, 'wait_eye': JAP_AGT_WAIT_EYE_CONTACT,
                     'ja_init_waiting_time': JAP_INITIAL_RJA_WAITING_TIME, 'gazes_wrong': JAP_AGT_RJA_FOLLOW_WRONG,
                     'possible_aois': JAP_AGT_RJA_FOLLOW_WRONG_AOIS, 'break_trial_if_no_mg':
                     JAP_BREAK_TRIAL_IF_NO_MG, 'single_chance': JAP_SINGLE_CHANCE, 'bored_parameters':
                     JAP_RJA_BORED_PARAMETERS, 'show_vid': JAP_SHOW_VID_RJA, 'show_vid_always': JAP_ALWAYS_SHOW_VID,
                     'show_points': JAP_SHOW_POINTS, 'highlight_obj': JAP_HL_OBJ_RJA, 'correct_feedback':
                     JAP_P_CORRECT_FEEDBACK, 'questionnaire': JAP_QUESTIONNAIRE, 'log_event':
                     logger_dict['rja_recorder'][0], 'finished_event': agent_finished, 'break_event':
                     agent_break_event, 'game_event': game_hub.event, 'name': 'RJA_Agent', 'class': RJA_Agent_Dict}
        agent_dict = {'PO__Agent': passive_agent_partner_oriented, 'PassiveAgent_IO': passive_agent_introspective,
                      'IJA_Agent': ija_agent, 'RJA_Agent': rja_agent}
        mixed_agent = {'agent_dict': agent_dict, 'cur_agt': self.cur_agt, 'draw_event': self.draw,
                       'draw_lock': draw_lock, 'questionnaire': JAP_QUESTIONNAIRE, 'new_objects': True,
                       'new_objects_evnet': self.wait_4_instr, 'finished_event': agent_finished, 'name': 'Mixed_Agent',
                       'class': Mixed_Agent_Dict}
        print('LOLO4')
        # Create thread controlling agent's macro behavioral states
        self.agent_macro_behavior = AgentMacroBehavior(self.wait_4_instr, self.draw, draw_lock, agent_finished,
                                                       macro_finished, JAP_MACRO_ALWAYS_ON, JAP_POINT_SCR_DUR,
                                                       behavioral_sequence, block_chosen['baseline'],
                                                       JAP_AGT_START_GAZE, JAP_AGT_START_GAZE_DUR, JAP_TRANS_DICT2,
                                                       age_group, end_on_key_input,
                                                       self.logger.tobii_dumper.save_trigger, game_hub, JAP_NIRS,
                                                       ['Mixed_Agent'], blinking_agent, ija_agent,
                                                       passive_agent_partner_oriented, passive_agent_introspective,
                                                       passive_agent_object_oriented, rja_agent, mixed_agent)
        # TOCHECK: Kann das weg(??)
        self.logger.log_variable(self.agent_macro_behavior.time_gaze_lag, 'gaze_lag')

        # If set, prepare fNIRS recording
        if JAP_NIRS['use']:
            import serial
            port = serial.Serial('COM1', 9600, timeout=0)

        screen_count = 0  # Counter how many screeens have been shown
        libtime.expstart()  # Reset paradigm clock

        # If set, start fNIRS recording
        if JAP_NIRS['use']:
            if block_chosen == JAP_BLOCK_LIST[JAP_NIRS['block_start']-1]:
                port.write(JAP_NIRS['trigger_start'])
                print('Starting fNIRS recording-')

        # Start eye tracking
        if JAP_TRACKING:
            if not self.tracker.recording:
                self.tracker.start_recording()
            if JAP_PYGAZE_REC:
                self.tracker.start_recording()
            if JAP_SHOW_GAZE_CURSER:
                self.trigger = pygaze_framework.TriggerTimer(self.draw, 100, message='__gaze_cursor__',
                                                             name='GazeCursorTrigger')
                self.trigger.start()
            libtime.pause(50)  # Give tracker some time to get going and find the eyes

        #############################
        # Start screen presentation #
        #############################

        # Welcome and instructions screens (only shown at the beginning of the first block)
        if block_chosen == JAP_BLOCK_LIST[0] and not skip_instructions:

            # 1. Present welcome screen, will trigger mucap to start recording
            draw_event_set_time = libtime.get_time()
            draw_time = self.scr_hdlr.make_and_draw_screen(JAP_WELCOME_TEXT[age_group]['welc'])
            logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'welcome_text', screen_count])
            screen_count += 1
            libtime.pause(JAP_MIN_INSTR_READ_TIME)
            self.keyboard.get_key(timeout=None, flush=True)

            # 2. Present (fake) avatar selection
            if JAP_CHOOSE_AVATAR:
                av_selection_dict = {}
                # Get gender specific agent dir
                if subject_data['sex'] == 'm':
                    agent_select_directory = os.path.join(JAP_AGT_SCLT_DIR, 'male')
                elif subject_data['sex'] == 'f':
                    agent_select_directory = os.path.join(JAP_AGT_SCLT_DIR, 'female')
                draw_event_set_time = libtime.get_time()

                # Create and present selection screen
                av_selection_dict['agent_list'] = self.scr_hdlr.make_agent_selection_screen(
                                                                                        agent_select_directory,
                                                                                        age_group,
                                                                                        JAP_AGT_SEL_TEXT[age_group])
                draw_time = self.scr_hdlr.show_agent_selection_screen()
                logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'agent_selection',
                                                       screen_count])
                screen_count += 1

                # Get and save selection
                av_selection_dict['selection'] = self.keyboard.get_key(
                        keylist=[str(i + 1) for i in range(len(av_selection_dict['agent_list']))],
                        timeout=None, flush=True)
                sequence_path = os.path.join('logs', self.logger.data['code'], 'sequence')
                with open(os.path.join('logs', self.logger.data['code'], 'agent_selection'), 'w') as \
                        agent_selection_file:
                    json.dump(av_selection_dict, agent_selection_file, indent=4)

            # 3. Show general instructions
            for text in range(1, len(JAP_TXT_B1[age_group])+1):
                    draw_event_set_time = libtime.get_time()
                    text = 'inst_' + str(text)
                    screen_count, draw_time = self.scr_hdlr.present_instruction_screen(text, screen_count)
                    logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, text, screen_count])
                    screen_count += 1
                    self.keyboard.get_key(timeout=None, flush=True)

            # Wait for key press until experiment will start
            if not skip_key_input:
                self.keyboard.get_key(timeout=None, flush=True)
            else:
                libtime.pause(500)

        # 6. Create and show welcome screen
        elif not skip_instructions:
            draw_event_set_time = libtime.get_time()
            draw_time = self.scr_hdlr.make_and_draw_screen(JAP_INBTW_TEXT[age_group]['new_block'],
                                                           mucap_stim='start_rec')
            logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'new_block', screen_count])
            screen_count += 1
            self.keyboard.get_key(timeout=None, flush=True)

        # 7. If set, show a wait screen to make to Hi think the partner is getting ready
        if not skip_instructions and JAP_SHOW_INSTR and JAP_SHOW_WAIT_SCR:
            draw_event_set_time = libtime.get_time()
            draw_time = self.scr_hdlr.make_and_draw_screen(JAP_INBTW_TEXT[age_group]['wait'])
            logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'wait_screen', screen_count])
            screen_count += 1
            libtime.pause(uniform(1000, 5000))

        ########################
        # START AGENT BEHAVIOR #
        ########################

        loop_on = True
        draw_event_set_time = None
        answer_key = None
        inital_questionnaire = None
        # Start threads for agent's behavior and fixation detection
        self.agent_macro_behavior.start()  # Start macro state sequence
        fixation_detector.start()  # Start fixation detector

        self.draw.clear()
        self.first_run = True

        #################################
        # LOOP FOR SCREEN PRESENTATIONS #
        #################################
        while loop_on:
            draw_time = None
            self.keyboard.get_key(None, 0, flush=True)  # Clear keyboard input
            # Wait for new agent to draw:
            # If timeout is reached none will be returned and loop will continue
            draw_instruction = self.draw.wait(timeout=.1)

            # ???
            if not self.draw.time == draw_event_set_time:
                draw_event_set_time = self.draw.time

            # if draw_instruction == 'startgaze':
            #     self.time_event.set()
            #     self.time_event.clear()

            # Check for a valid button press
            char = self.keyboard.get_key(None, 1)
            if (char[0] in JAP_QUESTIONNAIRE.keys() and self.agent_macro_behavior.time_agent_started and
                    self.agent_macro_behavior.accept_key_input and
                    (libtime.get_time()-self.agent_macro_behavior.time_agent_started)/1000 > block_chosen['min_time']):
                self.agent_macro_behavior.time_agent_started = None
                answer_key = char[0]
                agent_break_event.set()
                print(encapsulate_text(str(char), color='blue', background='yellow'))
                logger_dict['questionnaire_recorder'][0].set([None, char[1],
                                                              self.agent_macro_behavior.running_agent_name,
                                                              None, char[0]])
            # Print to console if new agent is shown on screen
            if draw_instruction and not draw_instruction == '__gaze_cursor__':
                print(colored_text(draw_instruction, 'yellow'))
            # Make and show instruction screen, and wait for keypress
            if draw_instruction == '__instruction_screen__':
                instruction_str = self.draw.msg2
                draw_time = self.scr_hdlr.make_and_draw_screen(instruction_str)
                self.draw.msg2 = JAP_AGT_START_GAZE
                logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'instruction', screen_count,
                                                       instruction_str.split('\n')])
                screen_count += 1
                # wait for keypress
                if not skip_instructions and not instruction_str == ' ':
                    self.keyboard.get_key(None, None, flush=True)
                else:
                    libtime.pause(1000)
                self.wait_4_instr.set()

            # Show a video
            elif draw_instruction == 'video':
                # Play video
                draw_time_s, draw_time_e = movs[self.draw.msg2].play_video()
                logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time_s, draw_time_e, 'video',
                                                      self.draw.msg2, screen_count])
                screen_count += 1
            # Create new screens
            elif draw_instruction == '__new_screens__':
                if self.draw.msg2 == 'empty':
                    draw_time = self.scr_hdlr.make_and_draw_screen('')
                    logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'empty screen',
                                                           screen_count])
                else:
                    draw_time = self.scr_hdlr.draw_agent_on_target_screen(self.draw.msg2, force_stim_signal=True)
                    logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, self.draw.msg2,
                                                           screen_count])

                screen_count += 1

                if JAP_NEW_OBJECTS or self.first_run:
                    if JAP_NEW_OBJECTS:
                        target_dict = self.object_picker.get_new_targets()
                    self.scr_hdlr.make_agent_screens_with_objects(target_dict, states2draw,
                                                                  fixation_detector=fixation_detector,
                                                                  aoi_tol=JAP_AOI_TOL, draw_aois=draw_aois,
                                                                  aoi_border_size=aoi_border_size)
                    self.first_run = False
                self.wait_4_instr.set()
                self.wait_4_instr.clear()

            # Take a screenshot
            elif draw_instruction == '__screenshot__':
                if screenshots:
                    self.scr_hdlr.make_screenshot(self.logger.get_screenshot_name())

            # Change screens and adjust values for screen recorder
            elif draw_instruction == '__change_screens__':
                x = len(self.draw.msg2) - 11  # Get object number
                self.scr_hdlr.change_screen_for_trial(self.draw.msg2)
                # Adjust values for logging
                target_dict['left'] = JAP_TRIAL_TYPES[self.draw.msg2]['object_left' + self.draw.msg2[-x:]]
                target_dict['right'] = JAP_TRIAL_TYPES[self.draw.msg2]['object_right' + self.draw.msg2[-x:]]
                target_dict['correct'] = JAP_TRIAL_TYPES[self.draw.msg2]['correct_aoi']

            # Add and show a gaze cursor to current screen
            elif draw_instruction == '__gaze_cursor__':
                self.scr_hdlr.draw_gaze_cursor(self.tracker)

            # Show a questionnaire
            elif draw_instruction == '__questionnaire__':
                print(encapsulate_text('test', color='cyan', background='magenta'))
                if inital_questionnaire:
                    initial_questionnaire.set()
                    initial_questionnaire = None
                if not skip_key_input:
                    if answer_key and answer_key in JAP_QUESTIONNAIRE.keys():
                        question = JAP_QUESTIONNAIRE[answer_key]['question']
                        draw_time = self.scr_hdlr.make_and_draw_screen(question)
                        logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'questionnaire',
                                                               screen_count])
                        char = self.keyboard.get_key(JAP_QUESTIONNAIRE[answer_key]['answers'], None, flush=True)
                        logger_dict['questionnaire_recorder'][0].set([draw_time, char[1],
                                                                      self.agent_macro_behavior.running_agent_name,
                                                                      question.split('\n'), char[0]])
                        screen_count += 1
                        answer_key = None
                    else:
                        pass
                        darw_event_set_time = libtime.get_time()
                        draw_time = self.scr_hdlr.make_and_draw_screen('')
                        logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'empty screen',
                                                               screen_count])
                        screen_count += 1
                        libtime.pause(1000)
                self.draw.msg2.set()
                block_progress += 1
                self.gui.eyetracker_setup_window.progress_bar.setValue(block_progress)

            # Show initial questionaire
            elif draw_instruction == '__initial_questionnaire__':
                if not skip_key_input and self.agent_macro_behavior.accept_key_input:
                    initial_questionnaire = self.draw.msg2
                    self.draw.msg2 = JAP_AGT_START_GAZE
                    question = JAP_QUESTIONNAIRE['initial_question']['question']
                    draw_time = self.scr_hdlr.make_and_draw_screen(question)
                    logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'initial_questionnaire',
                                                           screen_count])
                    screen_count += 1
                    char = self.keyboard.get_key(JAP_QUESTIONNAIRE['initial_question']['answers'], None, flush=True)
                    print(char)
                    logger_dict['questionnaire_recorder'][0].set([draw_time, char[1],
                                                                  self.agent_macro_behavior.running_agent_name,
                                                                  question.split('\n'), char[0]])
                    initial_questionnaire.set()
                else:
                    self.draw.msg2.set()
                block_progress += 1
                self.gui.eyetracker_setup_window.progress_bar.setValue(block_progress)

            # Show a wait screen
            elif draw_instruction == '__wait_screen__':
                draw_time = self.scr_hdlr.make_and_draw_screen(JAP_TXT_B1[age_group]['wait'])
                logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'wait_screen', screen_count])
                screen_count += 1

            elif draw_instruction == '__baseline__':
                port.write(JAP_NIRS['trigger_base_line_start'])
                t0, t1 = self.scr_hdlr.show_base_line_screen_w_progress(self.draw.msg2, self.draw.msg3)
                self.draw.msg3 = None
                logger_dict['screen_recorder'][0].set([t0, t1, 'baseline', screen_count])
                screen_count += 1
                port.write(JAP_NIRS['trigger_base_line_end'])

            elif draw_instruction == '__send_trigger__':
                port.write(JAP_NIRS[self.draw.msg2])

            # Anything else (i.e. a gaze shift by the agent)
            elif draw_instruction:
                if gamify:
                    score = game_hub.score
                else:
                    score = None
                if draw_instruction in self.scr_hdlr.screens.keys() or draw_instruction[:-1] == 'startgaze':
                    if JAP_SHOW_GAZE_CURSER:
                        # show gaze cursor
                        if draw_instruction:
                            # if new agent is to be drawn get it
                            self.cur_agt = draw_instruction
                        draw_time = self.scr_hdlr.draw_agent_on_target_screen(self.cur_agt, tracker=self.tracker,
                                                                              aoi=self.draw.msg3)
                    else:
                        if draw_instruction:
                            # if there is a new agent to draw it will be shown on the screen
                            if draw_instruction[:-1] == 'startgaze':
                                draw_time = self.scr_hdlr.draw_agent_on_target_screen(draw_instruction[:-1],
                                                                                      force_stim_signal=True,
                                                                                      score=score, aoi=self.draw.msg3,
                                                                                      correct=self.draw.msg4)
                            else:
                                draw_time = self.scr_hdlr.draw_agent_on_target_screen(draw_instruction,
                                                                                      force_stim_signal=True,
                                                                                      score=score, aoi=self.draw.msg3,
                                                                                      correct=self.draw.msg4)
                    self.draw.msg3 = None
                    if draw_instruction:
                        # if there was a new agent to draw this will be written to log
                        if args.exp_type == 'ja_nirs':
                            logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, draw_instruction,
                                                                  screen_count, target_dict['left'],
                                                                  target_dict['right'], target_dict['correct'],
                                                                  self.draw.msg4])

                        elif args.exp_type == 'basic':
                            logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, draw_instruction,
                                                                   screen_count, target_dict['tar_up_left'],
                                                                   target_dict['tar_up_right'],
                                                                   target_dict['tar_down_left'],
                                                                   target_dict['tar_down_right']])
                        screen_count += 1
                else:
                    print(encapsulate_text(colored_text(draw_instruction, 'blue'), color='red'))
            if macro_finished.is_set():
                loop_on = False
            if draw_instruction is not None:
                draw_lock.release()

# --------------------------------------------------------------------------------------------------------------
# Loop for displaying stuff done
# --------------------------------------------------------------------------------------------------------------

        # ====
        # Show agent rating
        if not skip_key_input and JAP_AGENT_RATING and block_chosen == JAP_BLOCK_LIST[-1]:
            # Show rating instructions
            draw_event_set_time = libtime.get_time()
            draw_time = self.scr_hdlr.make_and_draw_screen(JAP_TXT_B1[age_group]['rating'])
            logger_dict['screen_recorder'][0].set([draw_event_set_time, draw_time, 'rating_instr', screen_count])
            screen_count += 1
            libtime.pause(3000)
            self.keyboard.get_key(timeout=None, flush=True)
            # Do rating
            if subject_data['sex'] == 'm':
                self.scr_hdlr.show_agent_rating(JAP_AGENT_RATING_AGENTS['male'], JAP_AGENT_RATING_QUESTIONS,
                                                logger_dict['agent_rating_recorder'][0])
            else:
                self.scr_hdlr.show_agent_rating(JAP_AGENT_RATING_AGENTS['female'], JAP_AGENT_RATING_QUESTIONS,
                                                logger_dict['agent_rating_recorder'][0])
        for vid in JAP_VIDS:
            movs[vid].save_video_progess()
        # ====
        # Show finish screen
        draw_event_set_time = libtime.get_time()
        draw_time = self.scr_hdlr.show_instructions('finished')
        print('Loop in experiment.py done')
        self.time_done = libtime.get_time()

        # ====
        # Stop all threads and data collection
        if JAP_TRACKING and JAP_SHOW_GAZE_CURSER:
            self.trigger.stop()
        game_hub.stop()
        self.event_handler.stop()
        fixation_detector.stop()
        save_started = libtime.get_time()
        print(encapsulate_text("Don't panic! Just saving data.", color='red'))
        self.logger.stop()

        # Stop/Pause fNIRS recording
        if JAP_FACE_READING:
            face_reader.stop_analyzing()
            face_reader.stop_detailed_log()
        try:
            os.rename(self.tracker.gaze_data_call_file_name,
                      os.path.join(self.logger.data_dir, self.tracker.gaze_data_call_file_name))
        except AttributeError:
            pass
        if JAP_TRACKING:
            if self.tracker.recording:
                self.tracker.stop_recording()
            self.tracker.close()

        print(encapsulate_text("Done saving. Took "+str(round((libtime.get_time()-save_started)/1000, 2))+'s',
                               color='green'))
        libtime.pause(1000)

        if block_chosen == JAP_BLOCK_LIST[-1]:
            # Show final screen
            self.scr_hdlr.show_instructions('end_paradigm')
            # End fNIRS recording
            if JAP_NIRS['use'] and block_chosen == JAP_BLOCK_LIST[-1]:
                port.write(JAP_NIRS['trigger_end'])
                print('Stopped fNIRS recording.')
        else:
            self.scr_hdlr.show_instructions('end_block')

        # Wait and close display
        libtime.pause(1500)
        self.scr_hdlr.display.close()
        # Move and rename collected data
        self.logger.move_n_rename_data()
        # print remaining threads
        print_threads()
        print(colored_text('... paradigm done!', 'green'))

# Run paradigm
if __name__ == '__main__':

    # optinal arguments when calling file from console
    parser = argparse.ArgumentParser(description='doing some stuff')
    parser.add_argument('-c', '--auto_create', action='store_true', default=False,
                        help='automatically create an agent')
    parser.add_argument('-a', '--draw_aois', action='store_true', default=False, help='Draw boxes around used AOIs')
    parser.add_argument('-f', action='store_true', default=False, help='skip calibraiton entirely')
    parser.add_argument('-i', '--skip_instr', action='store_true', default=False,
                        help='skip instructions at paradigm start')
    parser.add_argument('-k', '--skip_key_input', action='store_true', default=False,
                        help='Skip keyboard input in instruction screens')
    parser.add_argument('-o', '--option', default=[], action='append', nargs=2,
                        metavar=('OPTION', 'VALUE'), help='set a special VARIABLE to a given VALUE')
    parser.add_argument('-t', action='store_true', default=False, help='testing')
    parser.add_argument('-r', action='store_true', default=False, help='reload previous HI data')
    parser.add_argument('-d', '--delete', action='store_true', default=False, help='Delete test proband log files' +
                        '1337_H4x0r before starting the paradigm')
    parser.add_argument('--gaze_cursor', action='store_true', default=False, help='show gaze cursor')
    parser.add_argument('--agent', default=None, help='define the agent, which will be used')
    parser.add_argument('--code', default=None, help='sets the subject code used for saving the data')
    parser.add_argument('--runs', default=10, type=int, help='number of runs, the defined agent will do')
    parser.add_argument('--gui', default=False, action='store_true', help='only run the setup window')
    parser.add_argument('--screenshots', action='store_true', default=False, help='Capture screenshots')
    parser.add_argument('--aoi_border_size', default=5, type=int, help='thickness of the AOI box border')
    parser.add_argument('--stopwatch', default=None, type=float, metavar='SEC',
                        help='run a stopwatch during the experiment, printing the current time every SEC')
    parser.add_argument('--force_quit', default=False, action='store_true', help='force experiment to quit at the end')
    parser.add_argument('--gamify', default=False, action='store_true', help='Will present some score on screen')
    parser.add_argument('--block', default=None, type=str, metavar='BLOCK', help='set block to run')
    parser.add_argument('--exp_type', default=None, type=str, help='select an experiment type: basic or ja_nirs,' +
                        ' their corresponding config file will be imported')

    args = parser.parse_args()

    for option, value in args.option:
        option_type = type(vars()[option])
        print(option_type)
        vars()[option] = option_type(value)

    if args.gaze_cursor:
        JAP_SHOW_GAZE_CURSER = True

    if args.agent:
        behavioral_sequence = [[args.agent, args.runs]]

    if args.stopwatch:
        stopwatch = StopWatch(args.stopwatch)
        stopwatch.start()

    # Delete all pickles if no HI ID is reloaded
    if not args.r:
        if os.path.exists('video.pickle'):
            os.remove('video.pickle')
            print('Removed video.pickle')
        if os.path.exists('trial.pickle'):
            os.remove('trial.pickle')
            print('Removed trial.pickle')
        if os.path.exists('save.pickle'):
            os.remove('save.pickle')
            print('Removed save.pickle')

    # Import study specific file
    if args.exp_type:
        if args.exp_type == 'basic':
            from studies.basic import *
        elif args.exp_type == 'ja_nirs':
            from studies.ja_nirs import *
    else:
        from studies.basic import *

    # If set, import FaceReader client
    if JAP_FACE_READING:
        from msrresearch_helpers import facereader

    # If true, add agent name to screen right before a macro block starts (for debugging)
    # if JAP_SINGLE_TRIAL_INSTRUCTIONS:
    #    for state in JAP_AGT_TXT_B1:
    #        JAP_AGT_TXT_B1[state] = state + '\n' + JAP_AGT_TXT_B1[state]

    if not args.gui:
        jap_experiment = JAP_Experiment(test=args.t, fast_forward=args.f, skip_key_input=args.skip_key_input,
                                        skip_instructions=args.skip_instr, screenshots=args.screenshots,
                                        code=args.code, gamify=args.gamify, block_name=args.block,
                                        auto_create=args.auto_create, draw_aois=args.draw_aois,
                                        aoi_border_size=args.aoi_border_size, reload_save=args.r,
                                        delete_test_prob=args.delete)
        if args.force_quit:
            jap_experiment.gui.eyetracker_setup_window.quit()
