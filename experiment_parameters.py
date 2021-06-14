# -*- coding: utf-8 -*-

from os import path
from constants import DISPSIZE
from time import strftime as get_date
# FILE TO DEFINE LAB/SETUP SPECIFIC PARAMETERS

# These parameters should be the same for any experiment conducted in the same lab and/or setup.
# You can also redefine all parameters in the study specific file (see studies subdir of this repo for examples to copy
# and adapt.)

# ==============================================================================
# HI Settings
# ==============================================================================
# Definition of HI age groups in years
# (computed via entered date of birth and used for presenting age adapted for fake avatar selection IF activated)
JAP_AGE_GROUPS = {
                  'child': [0, 12],
                  'teen_young': [12, 14],
                  'teen_old': [14, 18],
                  'adult_young': [18, 30],
                  'adult_old': [30, 100],
                  }

# ==============================================================================
# AGENT PARAMETERS (LOCATION, SIZE, AOIS, AND GAZE DIRECTIONS)
# ==============================================================================
# Dir where agent images a located (one sub dir per agent)
JAP_AGT_DIR = path.join('figs', 'virtual_characters')
# Dict for all agent dirs, agent can be selected via GUI
JAP_AGT_DIR = {
               'male_test': path.join(JAP_AGT_DIR, 'male'),
               # 'female_test': path.join(JAP_AGT_DIR, 'female')
              }

JAP_FACE_READING = False
JAP_SHOW_INSTR = True  # Show instructions before each macro state

# Point screen duration
JAP_POINT_SCR_DUR = [1, 1.5]  # Duration of point screen presentation drawn uniformly from interval in [s]

# Position of agent on screen in pixels from upper left corner
JAP_AGT_POS = [int(DISPSIZE[0] / 2), int(DISPSIZE[1] * 0.63)]
JAP_AGT_SIZE = (2000, 800)  # Size of agent in pixels

# AOI(s) for the agent (in pixels)
JAP_AGT_AOI = {
               # 'AOI_agert_upper_face': ((810, 440), (300, 160)),
               'AOI_agent_eyes': {
                                  'pos': (960, 650),
                                  'size': (400, 150),  # was (300, 150) is basic study
                                  'tol': None,
                                  },
               # 'AOI_agent_lower_face': ((810, 700), (300, 220))
              }
JAP_AGT_START_GAZE_DUR = 500  # Duration of start gaze in [ms]

# Dict of single gaze directions and corresponding image filenames
# must be present for desidered gaze directions in a given experiment
JAP_AGT_DICT = {

    'straight': 'straight.png',
    'closed': 'closed.png',
    'up': 'up.png',
    'down': 'down.png',

    'left': 'left.png',
    'down_left': 'down_left.png',
    'up_left': 'up_left.png',

    'right': 'right.png',
    'down_right': 'down_right.png',
    'up_right': 'up_right.png',

    'hc_down': 'half_closed.png',
    'down': 'down.png',
    'down_left': 'down_left.png',
    'down_right': 'down_right.png',

    'pers_fix_fh': 'pers_fix_fh.png',
    'pers_fix_left': 'pers_fix_left.png',
    'pers_fix_right': 'pers_fix_right.png',
    'pers_fix_nose': 'pers_fix_nose.png',
    'pers_fix_mouth': 'pers_fix_mouth.png',
    'pers_fix_throat': 'pers_fix_throat.png',

    'brows_up': 'brows_up.png',
    'smile': 'happy_straight.png',
}

JAP_MACRO_ALWAYS_ON = ['BlinkingAgent']  # Behavioral macro states that are always running

# ALWAYS ON STATES (active whenever agent is present on screen): ===============
# BLINKING AGENT ===============================================================

# Temporal parameters
JAP_AGT_BLINK_INTERVAL = [8.8, 0.62, None, 'lognormal', 1.]  # Time between two blinks
JAP_AGT_BLINK_DURATION = [100., 0.1, None, 'nonrandom', 1.]  # Duration of a blink

# IJA AGENT
# Microstate transition matrix
JAP_TRANS_MAT_IJA = {}
JAP_TRANS_MAT_IJA['left'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}
JAP_TRANS_MAT_IJA['right'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}
JAP_TRANS_MAT_IJA['up_left'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}
JAP_TRANS_MAT_IJA['up_right'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}
JAP_TRANS_MAT_IJA['straight'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}

# IJA get_attention() method parameters
JAP_IJA_GET_ATTENTION_PARAMETERS = {
                                    'n_attempts': 0,
                                    'agent_image': 'brows_up',
                                    'agent_image_list': [
                                                         ['straight', 50],
                                                         ['brows_up', 0.000000001],
                                                         ],
                                    't_max_per_attempt': [2000, 300],
                                    't_show_agent_image': [250, .0000001],
                                    }
JAP_SINGLE_CHANCE = {}
JAP_SINGLE_CHANCE['one_gaze_shift'] = False  # Agent will perform only a single gaze shift before ending
JAP_SINGLE_CHANCE['stop_trial_if_no_mg'] = False  # Trial will end if no mutual gaze was established
# ==============================================================================
# Default Non-interactive agent parameters
# ==============================================================================

# INTROSPECTIVE AGENT (INT) ====================================================

# Temporal behavioral parameters (for sampling micro state durations)
JAP_A_INT_TIMINGS = {
                    'left': [6.9118, 0.5245, 'lognormal', 1],
                    'up_left': [6.9976, 0.6765, 'lognormal', 1],
                    'up_right': [6.9347, 0.6305, 'lognormal', 1],
                    'right': [6.888, 0.5526, 'lognormal', 1],
                    'pers_fix_fh': [7.1456, 0.7109, 'lognormal', 1],
                    'straight': [7.3693, 0.7827, 'lognormal', 1],
                    'pers_fix_mouth': [6.7995, 0.4997, 'lognormal', 1],
                    'pers_fix_throat': [7.311, 0.7915, 'lognormal', 1],
                   }

# Behavioral transition probabilites
JAP_A_INT_TRANS_MAT = {}
JAP_A_INT_TRANS_MAT['left'] = {'left': 0, 'up_left': 0.214, 'up_right': 0.184, 'right': 0.092, 'pers_fix_fh': 0.102,
                               'straight': 0.378, 'pers_fix_mouth': 0.02, 'pers_fix_throat': 0.01}
JAP_A_INT_TRANS_MAT['up_left'] = {'left': 0.271, 'up_left': 0, 'up_right': 0.302, 'right': 0.093, 'pers_fix_fh': 0.109,
                                  'straight': 0.217, 'pers_fix_mouth': 0.008, 'pers_fix_throat': 0}
JAP_A_INT_TRANS_MAT['up_right'] = {'left': 0.063, 'up_left': 0.189, 'up_right': 0, 'right': 0.261,
                                   'pers_fix_fh': 0.117, 'straight': 0.361, 'pers_fix_mouth': 0.009,
                                   'pers_fix_throat': 0}
JAP_A_INT_TRANS_MAT['right'] = {'left': 0.115, 'up_left': 0.115, 'up_right': 0.124, 'right': 0, 'pers_fix_fh': 0.062,
                                'straight': 0.566, 'pers_fix_mouth': 0.018, 'pers_fix_throat': 0}
JAP_A_INT_TRANS_MAT['pers_fix_fh'] = {'left': 0.05, 'up_left': 0.054, 'up_right': 0.045, 'right': 0.054,
                                      'pers_fix_fh': 0, 'straight': 0.757, 'pers_fix_mouth': 0.009,
                                      'pers_fix_throat': 0.031}
JAP_A_INT_TRANS_MAT['straight'] = {'left': 0.108, 'up_left': 0.125, 'up_right': 0.097, 'right': 0.144,
                                   'pers_fix_fh': 0.474, 'straight': 0, 'pers_fix_mouth': 0.041,
                                   'pers_fix_throat': 0.011}
JAP_A_INT_TRANS_MAT['pers_fix_mouth'] = {'left': 0, 'up_left': 0, 'up_right': 0, 'right': 0, 'pers_fix_fh': 0.125,
                                         'straight': 0.375, 'pers_fix_mouth': 0, 'pers_fix_throat': 0.5}
JAP_A_INT_TRANS_MAT['pers_fix_throat'] = {'left': 0.043, 'up_left': 0.044, 'up_right': 0.044, 'right': 0.044,
                                          'pers_fix_fh': 0.217, 'straight': 0.304, 'pers_fix_mouth': 0.304,
                                          'pers_fix_throat': 0}
# PARTNER-ORIENTED AGENT (PO) ==================================================

# Temporal behavioral parameters
JAP_A_PO_TIMINGS = {
                    'left': [6.8056, 0.3991, 'lognormal', 1],
                    'right': [6.7505, 0.3811, 'lognormal', 1],
                    'pers_fix_fh': [6.9308, 0.5442, 'lognormal', 1],
                    'straight': [7.2916, 0.7684, 'lognormal', 1],
                    'pers_fix_mouth': [6.7463, 0.409, 'lognormal', 1],
                    'pers_fix_throat': [6.8211, 0.4562, 'lognormal', 1],
                    }

# Behavioral transition probabilites
JAP_A_PO_TRANS_MAT = {}
JAP_A_PO_TRANS_MAT['left'] = {'left': 0, 'right': 0.095, 'pers_fix_fh': 0.048, 'straight': 0.857, 'pers_fix_mouth': 0,
                              'pers_fix_throat': 0}
JAP_A_PO_TRANS_MAT['right'] = {'left': 0.048, 'right': 0, 'pers_fix_fh': 0.095, 'straight': 0.857, 'pers_fix_mouth': 0,
                               'pers_fix_throat': 0}
JAP_A_PO_TRANS_MAT['pers_fix_fh'] = {'left': 0.01, 'right': 0.017, 'pers_fix_fh': 0, 'straight': 0.914,
                                     'pers_fix_mouth': 0.042, 'pers_fix_throat': 0.017}
JAP_A_PO_TRANS_MAT['straight'] = {'left': 0.049, 'right': 0.093, 'pers_fix_fh': 0.717, 'straight': 0,
                                  'pers_fix_mouth': 0.11, 'pers_fix_throat': 0.031}
JAP_A_PO_TRANS_MAT['pers_fix_mouth'] = {'left': 0, 'right': 0, 'pers_fix_fh': 0.147, 'straight': 0.627,
                                        'pers_fix_mouth': 0, 'pers_fix_throat': 0.226}
JAP_A_PO_TRANS_MAT['pers_fix_throat'] = {'left': 0, 'right': 0.026, 'pers_fix_fh': 0.263, 'straight': 0.474,
                                         'pers_fix_mouth': 0.237, 'pers_fix_throat': 0}

# 1.1.1 OBJECT ORIENTED AGENT =================================================

# Temporal behavioral parameters
JAP_A_OO_TIMINGS = {
                    'left': [7.3661, 0.6775, 'lognormal', 1],
                    'up_left': [7.2177, 0.6565, 'lognormal', 1],
                    'up_right': [7.256, 0.6496, 'lognormal', 1],
                    'right': [7.3722, 0.7063, 'lognormal', 1],
                    'pers_fix_fh': [6.9142, 0.5016, 'lognormal', 1],
                    'straight': [6.8641, 0.5101, 'lognormal', 1],
                   }

# Behavioral transition probabilites
JAP_A_OO_TRANS_MAT = {}
JAP_A_OO_TRANS_MAT['left'] = {'left': 0, 'up_left': 0.589, 'up_right': 0.187, 'right': 0.145, 'pers_fix_fh': 0.04,
                              'straight': 0.039}
JAP_A_OO_TRANS_MAT['up_left'] = {'left': 0.395, 'up_left': 0, 'up_right': 0.472, 'right': 0.079, 'pers_fix_fh': 0.02,
                                 'straight': 0.034}
JAP_A_OO_TRANS_MAT['up_right'] = {'left': 0.094, 'up_left': 0.391, 'up_right': 0, 'right': 0.464, 'pers_fix_fh': 0.022,
                                  'straight': 0.029}
JAP_A_OO_TRANS_MAT['right'] = {'left': 0.23, 'up_left': 0.205, 'up_right': 0.482, 'right': 0, 'pers_fix_fh': 0.026,
                               'straight': 0.057}
JAP_A_OO_TRANS_MAT['pers_fix_fh'] = {'left': 0.252, 'up_left': 0.268, 'up_right': 0.155, 'right': 0.073,
                                     'pers_fix_fh': 0, 'straight': 0.252}
JAP_A_OO_TRANS_MAT['straight'] = {'left': 0.233, 'up_left': 0.163, 'up_right': 0.214, 'right': 0.145,
                                  'pers_fix_fh': 0.245, 'straight': 0}
# RJA AGENT
JAP_BREAK_TRIAL_IF_NO_MG = False
# RJA bored parameters (if not JA is initiated by HI, agents starts gazing at objects)
JAP_RJA_BORED_PARAMETERS = {
                           'get_bored': False,  # Set to True to activate
                           'trans_matrix': JAP_A_OO_TRANS_MAT,  # Uses object oriented state transitions
                           'time_to_bore': [2000, 100, None, 'gauss', 1.],
                           'time_to_look_around': [2000, 100, None, 'gauss', 1.],
                           }

# ==============================================================================
# VC RATING AND SELECTION
# ==============================================================================

# Question on dominance and trustworthiness inspired by ???
# Perform agent rating at the end of the last expimental block
JAP_CHOOSE_AVATAR = False

# Dir of VCs for HI to fake select from
JAP_AGT_SCLT_DIR = path.join('figs', 'virtual_characters', 'agent_selection')
JAP_AGT_SCLT_SUB_DIRS = ['child', 'teen_young', 'teen_old', 'adult_young', 'adult_old']  # Age group specific subdirs

JAP_AGENT_RATING = True  # IF True, activates agent rating at the end of the last block of an experiment
JAP_AGENT_RATING_QUESTIONS = [
                              'Für wie vertrauenswürdig halten Sie diesen Charakter?',
                              'Für wie dominant halten Sie diesen Charakter?',
                              ]

# ==============================================================================
# GENERAL INSTRUCTION TEXTS OPTIONS
# ==============================================================================

JAP_FONT_SIZE = 50  # Text font size used during enire experiment (chosen for FullHD resolution)

# Instruction text at the beginning of paradigm ================================
JAP_START_TEXT = 'Please press any key to start the experiment.'
# Adult
__JAP_TXT_B1_A = {'inst_1': JAP_START_TEXT}
# Teenager
__JAP_TXT_B1_T = {'inst_1': JAP_START_TEXT}
# Child
__JAP_TXT_B1_C = {'inst_1': JAP_START_TEXT}

# Dictionary collecting all age specific instructions
JAP_TXT_B1 = {
              'child': __JAP_TXT_B1_C,
              'teen_young': __JAP_TXT_B1_T,
              'teen_old': __JAP_TXT_B1_T,
              'adult_young': __JAP_TXT_B1_A,
              'adult_old': __JAP_TXT_B1_A,
              }

# Text shown at the end of pretty much every Instruction screen
space_text = '\n\n\nZum Fortfahren bitte die Leertaste drücken.'

# Age-adapted eyetracker caibration texts to be shown before and after PyGaze calibration routine
JAP_CALIB_TXT = {
                  'begin': 'Press space to start eyetracker calibration',
                  'no_success': 'Calibration failed.',
                  'end': 'Calibration saved. Press "Start" in GUI to begin paradigm.'}

# Age-adapted fake avatar selection instructions
JAP_AGT_SEL_TEXT = {
                    'child': 'Mit den Tasten 1 bis 3 kannst du einen Avatar aussuchen.',
                    'teen_young': 'Mit den Tasten 1 bis 3 bitte einen Avatar auswählen.',
                    'teen_old': 'Mit den Tasten 1 bis 3 bitte einen Avatar auswählen.',
                    'adult_young': 'Mit den Tasten 1 bis 3 bitte einen Avatar auswählen.',
                    'adult_old': 'Wählen Sie mit den Tasten 1 bis 3 bitte einen Avatar.',
                    }

# Welcome screen at the very beginning when starting the actual paradigm (after clicking on "start" on GUI)
__JAP_WELCOME_TEXT_A = {'welc': 'Herzlich Willkommen zum eigentlichen Experiment!\n\n\nIhre genauen ' +
                                'Instruktionen haben Sie bereits gelesen und der Eyetracker ist jetzt auf ' +
                                'Ihre Augen kalibriert.\n Gleich können Sie einen Avatar auswählen, der Sie auf dem ' +
                                'Monitor Ihres Partners darstellt.\nIm Anschluss werden wir Ihnen noch einmal die ' +
                                'wichtigsten Regeln kurz zusammenfassen und ein paar Proberunden durchführen, ' +
                                'bevor das eigentliche Experiment beginnt.' + space_text}
__JAP_WELCOME_TEXT_T = {'welc': 'Herzlich Willkommen zum eigentlichen Experiment!\n\n\nDeine genauen Instruktionen' +
                                'hast du bereits gelesen und der Eyetracker ist jetzt auf deine Augen eingestellt.\n' +
                                'Gleich darfst du einen Avatar auswählen, der dich auf dem Monitor deines ' +
                                'Spielpartners darstellt.\nDann werden wir dir noch einmal die wichtigsten Regeln' +
                                'kurz zeigen und ein paar Proberunden spielen, bevor es dann richtig losgeht!' +
                                space_text}

__JAP_WELCOME_TEXT_C = {'welc': 'Herzlich Willkommen zum eigentlichen Experiment!\n\n\nDie Spielregeln hast ' +
                                'du bereits gelesen und der Eyetracker ist jetzt auf deine Augen eingestellt.\n' +
                                'Gleich darfst du einen Avatar auswählen, der dich auf dem Monitor deines ' +
                                'Spielpartners darstellt.\nDann werden wir dir noch einmal die wichtigsten Regeln' +
                                'kurz zeigen und ein paar Proberunden spielen, bevor es dann richtig losgeht!' +
                                space_text}
JAP_WELCOME_TEXT = {
              'child': __JAP_WELCOME_TEXT_C,
              'teen_young': __JAP_WELCOME_TEXT_T,
              'teen_old': __JAP_WELCOME_TEXT_T,
              'adult_young': __JAP_WELCOME_TEXT_A,
              'adult_old': __JAP_WELCOME_TEXT_A,
}


# Agent rating text
__JAP_RATING_TEXT_A = {'Im folgenden werden wir Ihnen noch Bilder von virtuellen Gesichtern zeigen, bei ' +
                       'denen wir gerne Ihre kurze Einschätzung haben würden, wie "dominant" und ' +
                       '"vertrauenswürdig" Sie diese bewerten. Dazu wählen Sie bitte per Tastendruck einen ' +
                       'Wert und bestätigen diesen mit Enter.\nDanach ist das Experiment beendet.' + space_text}

__JAP_RATING_TEXT_T = {'Im folgenden werden wir dir noch Bilder von virtuellen Gesichtern zeigen, bei ' +
                       'denen wir gerne deine kurze Einschätzung haben würden, wie "dominant" und ' +
                       '"vertrauenswürdig" du diese bewertest. Dazu wähle bitte per Tastendruck einen ' +
                       'Zahl und bestätige diese mit Enter.\nDanach ist das Experiment beendet.' + space_text}

__JAP_RATING_TEXT_C = {'Im folgenden werden wir dir noch Bilder von Avataren zeigen, bei ' +
                       'denen wir gerne deine kurze Einschätzung haben würden, wie "dominant" (anders gesagt ' +
                       'mächtig) und "vertrauenswürdig" du diese findest. Dazu wähle bitte eine Zahl durch  ' +
                       'Drücken der entsprechenden Taste und bestätige diese mit Enter.\n' +
                       'Danach ist das Experiment beendet.' + space_text}

JAP_RATING_TEXT = {
              'child': __JAP_RATING_TEXT_C,
              'teen_young': __JAP_RATING_TEXT_T,
              'teen_old': __JAP_RATING_TEXT_T,
              'adult_young': __JAP_RATING_TEXT_A,
              'adult_old': __JAP_RATING_TEXT_A,
}

# Per block instructions for "Verhaltensrolle" =================================
# Adult
_JAP_INSTR_TEXT_ADULT = {
                         'blank': '',
                         'welcome': 'Sie werden nun gleich den virtuellen Agenten Paul und einige Objekte sehen. ' +
                                    'Dazu werden Sie verschiedene Anweisungen bekommen, was Sie tun oder auf was ' +
                                    'Sie sich konzentrieren sollen. Wir bitten Sie, genau auf diese Anweisung zu ' +
                                    'achten und sich an sie zu halten.' + space_text,
                         'RJA_Agent': 'Handlungsrolle:\nBitte versuchen Sie sich mit Ihrem Partner auszutauschen ' +
                                      'und nutzen Sie Ihren Blick um ihn zu leiten.' + space_text,
                         'IJA_Agent': 'Handlungsrolle:\nBitte versuchen Sie sich mit Ihrem Partner ' +
                                      'auszutauschen und lassen Sie sich von seinem Blick leiten.' + space_text,
                         'Object_oriented': 'Handlungsrolle:\nBitte achten Sie auf die Objekte.' + space_text,
                         'Introspective': 'Handlungsrolle:\nBitte lassen Sie Ihre Augen geöffnet und konzentrieren ' +
                                          'Sie sich auf Ihren Atem.' + space_text,
                         'Partner_oriented': 'Handlungsrolle:\nBitte konzentrieren Sie sich auf Ihren Partner.' +
                                             space_text,
                         'finished': 'Fertig! Der Block ist nun beendet und ' +
                                     ' die Daten werden jetzt gespeichert. Bitte haben Sie einen Augenblick Geduld.',
                         'end_block': 'Der Block ist nun beendet, Sie können gerne eine kurze Pause machen.',
                         'end_paradigm': 'Vielen Dank für Ihre Teilnahme an unserem Experiment!'}
# Teenager
_JAP_INSTR_TEXT_TEEN = {
                        'blank': '',
                        'welcome': 'Sie werden nun gleich den virtuellen Agenten Paul und einige Objekte sehen. ' +
                                   'Dazu werden Sie verschiedene Anweisungen bekommen, was Sie tun oder auf was Sie ' +
                                   'sich konzentrieren sollen. Wir bitten Sie, genau auf diese Anweisung zu achten ' +
                                   'und sich an sie zu halten.' + space_text,
                        'RJA_Agent': 'Handlungsrolle: Bitte versuche dich mit deinem Partner auszutauschen und ' +
                                     'benutze deinen Blick um ihn zu leiten.' + space_text,
                        'IJA_Agent': 'Handlungsrolle: Bitte versuche dich mit deinem Partner auszutauschen ' +
                                     'und lasse dich von seinem Blick leiten.' + space_text,
                        'Object_oriented': 'Handlungsrolle: Bitte achten Sie auf die Objekte.' + space_text,
                        'Introspective': 'Handlungsrolle: Bitte lasse deine Augen geöffnet und konzentriere dich ' +
                                         'auf deinen Atem.' + space_text,
                        'Partner_oriented': 'Handlungsrolle: Bitte konzentriere dich auf deinen Partner.' + space_text,
                        'finished': 'Fertig! Der Block ist nun beendet und ' +
                                    ' die Daten werden jetzt gespeichert. Das dauert ein wenig.',
                        'end_block': 'Der Block ist nun beendet, du kannst gerne eine kurze Pause machen.',
                        'end_paradigm': 'Vielen Dank für deine Teilnahme an unserem Experiment!'}
# Children
_JAP_INSTR_TEXT_CHILD = {
                         'blank': '',
                         'welcome': 'Sie werden nun gleich den virtuellen Agenten Paul und einige Objekte sehen. ' +
                                    'Dazu werden Sie verschiedene Anweisungen bekommen, was Sie tun oder auf was ' +
                                    'Sie sich konzentrieren sollen. Wir bitten Sie, genau auf diese Anweisung zu ' +
                                    'achten und sich an sie zu halten.' + space_text,
                         'RJA_Agent': 'Deine Aufgabe: Bitte versuche dich mit deinem Partner auszutauschen und ' +
                                      'benutze deinen Blick um ihn zu leiten.' + space_text,
                         'IJA_Agent': 'Deine Aufgabe: Bitte versuche dich mit deinem Partner auszutauschen ' +
                                      'und lasse dich von seinem Blick leiten.' + space_text,
                         'Object_oriented': 'Deine Aufgabe: Bitte achte auf die Objekte.' + space_text,
                         'Introspective': 'Deine Aufgabe: Bitte lasse deine Augen geöffnet und konzentriere dich ' +
                                          'auf deinen Atem.' + space_text,
                         'Partner_oriented': 'Deine Aufgabe: Bitte konzentriere dich auf deinen Partner.' + space_text,
                         'finished': 'Fertig! Der Block ist nun beendet und ' +
                                     ' die Daten werden jetzt gespeichert. Das dauert ein wenig.',
                         'end_block': 'Der Block ist nun beendet. Du kannst gerne eine kurze Pause machen.',
                         'end_paradigm': 'Vielen Dank für deine Teilnahme an unserem Experiment!'}

# Dict collecting all age specific instructions
JAP_INSTR_TEXT = {
        'child': _JAP_INSTR_TEXT_CHILD,
        'teen_young': _JAP_INSTR_TEXT_TEEN,
        'teen_old': _JAP_INSTR_TEXT_TEEN,
        'adult_young': _JAP_INSTR_TEXT_ADULT,
        'adult_old': _JAP_INSTR_TEXT_ADULT}

# Instructions right before each block
JAP_INBTW_TEXT_A = {'wait': 'Bitte warten Sie kurz bis Ihr Partner bereit für die Runde ist.',
                    'round_start': 'Beobachterrolle:\nVersucht Ihr Partner sich mit Ihnen auszutauschen?\n' +
                                   '("J" für Ja, "N" für Nein)' + space_text,
                    'new_block': 'Drücken Sie bitte zum Starten der nächsten Runde die Leertaste.'}
JAP_INBTW_TEXT_T = {'wait': 'Bitte warte kurz bis dein Partner bereit ist...',
                    'round_start': 'Beobachte deinen Partner: Versucht er sich mit dir auszutauschen?\n' +
                                   '(drücke "J" für Ja oder "N" für Nein)' + space_text,
                    'new_block': 'Drücke bitte zum Starten des nächsten Durchgangs die Leertaste.'}
JAP_INBTW_TEXT_C = {'wait': 'Bitte warte kurz bis dein Partner bereit ist...',
                    'round_start': 'Beobachte deinen Partner: Versucht er sich mit dir auszutauschen?\n' +
                                   '(drücke "J" für Ja oder "N" für Nein)' + space_text,
                    'new_block': 'Drücke bitte die Leertaste zum Starten der nächsten Runde.'}
# Dict collecting all age specific instructions that are displayed inbetween the study

JAP_INBTW_TEXT = {
        'child': JAP_INBTW_TEXT_C,
        'teen_young': JAP_INBTW_TEXT_T,
        'teen_old': JAP_INBTW_TEXT_T,
        'adult_young': JAP_INBTW_TEXT_A,
        'adult_old': JAP_INBTW_TEXT_A}


# ==============================================================================
# ==============================================================================
# ===================== AFTER BLOCK QUESTIONNAIRE ==============================
# ==============================================================================
# ==============================================================================

# (ends a trial via button press option is active in a trial, activated via trial definition)

JAP_QUESTIONNAIRE = {
                     'v': {
                           'question': 'Sie haben sich für "austauschen" entschieden.' + space_text,
                           'answers': ['space']
                           },
                     'n': {
                           'question': 'Sie haben sich für "nicht-austauschen" entschieden.' + space_text,
                           'answers': ['space']
                           },
                     'initial_question': {
                                          'question': 'Die Zeit ist abgelaufen.\n' +
                                                      'Bitte in der nächsten Runde ein wenig schneller entscheiden.' +
                                                      space_text,
                                          'answers': ['space']
                                          },
                     }

JAP_MIN_INSTR_READ_TIME = 300

# Block durations
# Dictionary containing macro state durations in [s] [with keypress, without keypress]
JAP_BLOCK_DUR_DICT = {
                      'child': [30, 20],
                      'teen_young': [30, 30],
                      'teen_old': [30, 30],
                      'adult_young': [30, 30],
                      'adult_old': [60, 60]
                      }

# =============================================================================
# =============================================================================
# ========================== VC RATING ========================================
# =============================================================================
# =============================================================================

JAP_AGENT_RATING_AGENTS = {'male': ['figs/virtual_characters/2017_07_10_rerendered/straight.png',
                                    path.join(JAP_AGT_SCLT_DIR, 'male', 'adult_young',
                                              'Roby_young_adult_straight.png'),
                                    path.join(JAP_AGT_SCLT_DIR, 'male', 'adult_young',
                                              'Tobi_young_adult_straight.png')
                                    ],
                           'female': ['figs/virtual_characters/2017_07_10_rerendered/straight.png',
                                      path.join(JAP_AGT_SCLT_DIR, 'male', 'adult_young',
                                                'Roby_young_adult_straight.png'),
                                      path.join(JAP_AGT_SCLT_DIR, 'male', 'adult_young',
                                                'Tobi_young_adult_straight.png')
                                      ]
                           }

# ==============================================================================
# GENERAL AOI PARAMETERS (SHAPE, ADDITIONAL MARGINS)
# ==============================================================================
JAP_AOI_TOL = [10, 10]  # Additional size of AOI in pixels added to image size
JAP_AOI_TYPE = 'rect'  # Shape of AOIs, either 'rect', 'circle' or 'ellipse', only tested for 'rect'

# ==============================================================================
# DATA COLLECTION
# ==============================================================================
JAP_LOG_DIR = 'logs'  # Directory for data collection
JAP_DATE_STR = get_date("%Y-%m-%dT%H_%M_%S")  # Get a date string, used for naming collected data

# ==============================================================================
# STIMTRACKER PARAMETERS (for exact stimulus presentation timing via extranal Tobii TX300 compatible device)
# ==============================================================================
# Stimtracker "pixel" location and size in screen in rgb color and pixels units
JAP_STIMTRACKER_PARAMETER = {
                             'color': (0, 0, 0),
                             'position': (70, 1053),
                             'size': (25, 25)}

# ==============================================================================
# muCap PARAMETERS (for simple syncronized video recording via USB webcam)
# ==============================================================================
JAP_MUCAP_DIR = 'mucap'  # Subdir name
JAP_VIDEO = 'video.wmv'  # muCap default video filename
JAP_VIDEO_MARKER = 'markers.csv'  # muCap default marker file name

# RGB colors indicating muCap events to have double data for screen presentations (seems not to be reliable)
# (these parameters also need to be adjusted in config file for muCap
# dict containing RGB color information to trigger mucap)
JAP_MUCAP_DICT = {
            # pixel for triggering muCap events
            'pixel_pos': (5, 5),
            # RGB Values for starting/stopping/pausing muCap recording
            'start_rec':  (201, 200, 201),
            'pause_rec':  (201, 200, 202),
            'stop_rec': (201, 200, 203),
            'quit_rec':  (201, 200, 204),
            # RGB values for triggering muCap events
            'block_start': (201, 200, 205),
            'block_end': (201, 201, 201),
            # RGB Values for gaze directions (microstates)
            'hc_down': (201, 201, 202),
            'pers_fh': (201, 201, 203),
            'right': (201, 201, 204),
            'up_left': (201, 201, 205),
            'pers_fix_left': (201, 202, 201),
            'straight': (201, 202, 202),
            'up_right': (201, 202, 203),
            'up': (201, 202, 204),
            'pers_fix_right': (201, 202, 205),
            'down': (201, 203, 201),
            'down_right': (201, 203, 202),
            'brows_up': (201, 203, 203),
            'down_left': (201, 203, 204),
            'closed': (201, 203, 205),
            'smile': (201, 204, 201),
            'pers_fix_nose': (201, 204, 202),
            'left': (201, 204, 203),
            'pers_fix_mouth': (201, 204, 204),
            'pers_fix_throat': (201, 204, 205),
            'pers_fix_fh': (201, 205, 201)
}

# ==============================================================================
# DEFAULT VALUES (will be overwritten by study-specific values if defined there)
# ==============================================================================
JAP_OBJ_DIR = path.join('figs', 'objects')  # Object dir
JAP_NEW_OBJECTS = True  # Pick new objects for each trial (needs some 1-2 seconds to recreate correspoding screens)

# Default agent parameters
JAP_P_IJA_AGT_CORRECT_CHOICE = None  # Probalility that IJA agent will select correct object, set to *None* to turn off
JAP_TRIAL_TYPES = None
JAP_AGT_IJA_AOIS = None
# If sequence shall be shortened below a certain age, age threshold (<=), number of trials to shorten, prefix of trials
# not to shorten (e.g. practice trails)
JAP_AGE_DEPENDENT_SEQUENCE = [False, None, None, None]

# ==============================================================================
# fNIRS stuff
# ==============================================================================
JAP_NIRS = {}
JAP_NIRS['use'] = False  # Send triggers to Hitachi ETG 4000
JAP_NIRS['baseline'] = False  # Show a basline screen
JAP_NIRS['baseline_duration'] = [2, 3]

# ===================
# DATA LOGGING
# ===================
JAP_SCR_REC_COLS = ['time_experiment', 'time_tracker', 'time_draw_event', 'time_draw', 'agent', 'srceen_count',
                    'target_up_left', 'target_up_right', 'target_down_left', 'target_down_right']

JAP_ALWAYS_SHOW_VID = [False, None]
JAP_SHOW_VID = [False, 3]
JAP_REWIND_VID = False
JAP_POINT_SCR_DUR = [0, 0]  # Duration of point screen presentation drawn uniformly from interval in [s]
# Show a video when participants fixates an object (terminates current trial)
JAP_SHOW_VID_IJA = [False, 0.]
# Show a video when participants fixates an object (terminates current agent)
JAP_SHOW_VID_RJA = [False, 0.]

JAP_SHOW_POINTS = False

# REWARD PRESENTATION
JAP_P_CORRECT_FEEDBACK = 1.
JAP_HL_OBJ_IJA = [False, 0.]
JAP_HL_OBJ_RJA = [False, 0.]

# ===================
# MISC
# ===================
JAP_SHOW_WAIT_SCR = False

# Videos to be presented during the experiment (called via .set_micro_state(msg='video', msg2='*element_name*'))
JAP_VIDS = {}

# ==============================================================================
# DEBUGGING PARAMETERS
# ==============================================================================
JAP_TRACKING = True  # If set to True eyetracker will be used
JAP_SHOW_GAZE_CURSER = False  # If set to True, gaze cursor will be shown
JAP_DUMMY = False  # If set to True, dummy mode will be activated (simulate gaze via mouse cursor)(not implemented)
JAP_PYGAZE_REC = False  # If set to True, Pygaze's default data logging will also be used
JAP_SHOW_AGENT_STATES = True  # Adds agent state to text on screens before every block
