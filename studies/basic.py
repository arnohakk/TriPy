# -*- coding: utf-8 -*-

from os import path
from constants import DISPSIZE
from experiment_parameters import space_text, JAP_AGT_SCLT_DIR, JAP_OBJ_DIR, JAP_AGT_POS
from time import strftime as get_date
from numpy import array, sin, cos, pi
from random import sample, shuffle

# DESIGN YOUR INDIVIDUAL EXPERIMENT HERE (BASIC STUDY, use --exp_type basic to call this experiment)
# SETUP YOUR LAB/SETUP SPECIFIC OPTIONS IN experiment_parameters.py

# Present age-adapted fake avatar selection
JAP_CHOOSE_AVATAR = True

# ==============================================================================
# ==============================================================================
# ======================== 1. AGENT OPTIONS ====================================
# ==============================================================================
# ==============================================================================

# Temporal parameters are defined as:
# 'gaze_direction': [mu, sigma, (tau), disttype, interval in SD in which
# returned sampled value will be to avoid outliers in microp state duration]

# GLOBAL PARAMETERS
# Initial gaze direction of agent when trial starts (use '_no_obj' suffix to present objects in RJA/IJA states only
# after eyecontact has been established)
JAP_AGT_START_GAZE = 'down'

# 1.1 MACRO STATES DEFINING PARAMETERS
# Set agent's behavioral parameters via defining micro states

# ALWAYS ON STATES (active whenever agent is present on screen): ===============


# INDIVIDUAL MACRO STATES ======================================================
# INTROSPECTIVE AGENT (INT) ====================================================

# Temporal behavioral parameters (for sampling micro state durations)
JAP_A_INT_TIMINGS = {
                    'left': [6.9118, 0.5245, None, 'lognormal', 1],
                    'up_left': [6.9976, 0.6765, None, 'lognormal', 1],
                    'up_right': [6.9347, 0.6305, None, 'lognormal', 1],
                    'right': [6.888, 0.5526, None, 'lognormal', 1],
                    'pers_fix_fh': [7.1456, 0.7109, None, 'lognormal', 1],
                    'straight': [7.3693, 0.7827, None, 'lognormal', 1],
                    'pers_fix_mouth': [6.7995, 0.4997, None, 'lognormal', 1],
                    'pers_fix_throat': [7.311, 0.7915, None, 'lognormal', 1],
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
                    'left': [6.8056, 0.3991, None, 'lognormal', 1],
                    'right': [6.7505, 0.3811, None, 'lognormal', 1],
                    'pers_fix_fh': [6.9308, 0.5442, None, 'lognormal', 1],
                    'straight': [7.2916, 0.7684, None, 'lognormal', 1],
                    'pers_fix_mouth': [6.7463, 0.409, None, 'lognormal', 1],
                    'pers_fix_throat': [6.8211, 0.4562, None, 'lognormal', 1],
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
                    'left': [7.3661, 0.6775, None, 'lognormal', 1],
                    'up_left': [7.2177, 0.6565, None, 'lognormal', 1],
                    'up_right': [7.256, 0.6496, None, 'lognormal', 1],
                    'right': [7.3722, 0.7063, None, 'lognormal', 1],
                    'pers_fix_fh': [6.9142, 0.5016, None, 'lognormal', 1],
                    'straight': [6.8641, 0.5101, None, 'lognormal', 1],
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

# 2. IJA AGENT =================================================================

# Temporal behavioral parameters
JAP_AGT_T_STRAIGHT = [7.23, 0.57, None, 'lognormal', 1.]  # Time of agent looking straight before fixating object
JAP_AGT_T_LOOK_S_AGAIN = [899., 265., None, 'gauss', 1.]  # Time after succ. IJA before agent looks straight again
JAP_AGT_T_OBJ_IJA = [7.2, 0.55, None, 'lognormal', 1.]  # Time before agent looks straight again & picks new object
JAP_INITIAL_JA_AOIS = ['AOI_agent_eyes']  # AOI to wait for before initiating joint attention
JAP_INITIAL_JA_WAITING_TIME = [5000, None, None, 'nonrandom', None]  # Time to wait before initaitong joint attention
JAP_SUBJ_FIX_T = [1000., 300.]  # Part will be looked at while agent is trying to get attention IS IT REALLY USED?

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
# Microstate transition matrix
JAP_TRANS_MAT_IJA = {}
JAP_TRANS_MAT_IJA['left'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}
JAP_TRANS_MAT_IJA['right'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}
JAP_TRANS_MAT_IJA['up_left'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}
JAP_TRANS_MAT_IJA['up_right'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}
JAP_TRANS_MAT_IJA['straight'] = {'straight': 0., 'left': 0.25, 'right': 0.25, 'up_left': 0.25, 'up_right': 0.25}

# 3. RJA AGENT =================================================================
# Agent waits for eye contact before following with gaze
JAP_AGT_WAIT_EYE_CONTACT = False
JAP_AGT_RJA_FOLLOW_WRONG = True
JAP_AGT_RJA_FOLLOW_WRONG_AOIS = ['left', 'right']
JAP_INITIAL_RJA_WAITING_TIME = [5000, None, None, 'nonrandom', None]  # Time to wait before initaitong joint attention

# Temporal parameters
JAP_AGT_FOLLOW_LAG = [6.06, 0.32, None, 'lognormal', 1.]  # Time of agent gaze following
JAP_AGT_FOLLOW_PROB = 1.  # Probability of agent to follow gaze on object
JAP_AGT_FOLLOW_PROB2 = 0.33  # Probability of agent to follow gaze on object (second state)
JAP_AGT_RESET_LAG = [6.78, 0.62, None, 'lognormal', 1.]  # Time of agent fixating activated aoi by participant

# RJA bored parameters (if not JA is initiated by HI, agents starts gazing at objects)
JAP_RJA_BORED_PARAMETERS = {
                           'get_bored': False,  # Set to True to activate
                           'trans_matrix': JAP_A_OO_TRANS_MAT,  # Uses object oriented state transitions
                           'time_to_bore': [2000, 100, None, 'gauss', 1.],
                           'time_to_look_around': [2000, 100, None, 'gauss', 1.],
                           }

# ==============================================================================
# ==============================================================================
# ======================== INSTRUCTIONs/TEXT OPTIONS ============================
# ==============================================================================
# ==============================================================================


# 1. STUDY SPECIFIC INSTRUCTION TEXTS (presented before the first block of an experiment)
# TODO ISSUE #416 https://github.com/msrresearch/joint_attention_paradigma/issues/416

# Instruction text at the beginning of paradigm ================================
# Adult
__JAP_TXT_B1_A = {'inst_1': 'Danke! Sie werden nun gleich den Avatar Ihres Partners und vier Objekte sehen. \
                             Zuvor werden wir kurz die wichtigsten Regeln wiederholen:' + space_text,
                  'inst_2': 'Grundsätzlich sind Sie entweder in der "Handlungsrolle":\n\n\n' +
                            'Kurz gesagt: Sie bekommen konkrete Aufgaben wie z.B. „Achten Sie auf die Objekte“ ' +
                            'oder „Versuchen Sie den Blick des anderen zu leiten“. Folge Sie bitte dieser Anweisung' +
                            'bis zum Ende der Runde.' + space_text,
                  'inst_3': 'Oder Sie sind in der Beobachterrolle:\n\n\n' +
                            'Kurz gesagt: Ihre Aufgabe ist es herauszufinden, ob Ihr Spielpartner gerade ' +
                            'versucht, sich mit Ihnen auszutauschen oder nicht.\nDrücken Sie bitte die blaue ' +
                            'mit "J" markierte Taste für "Ja" oder die rote mit "N" markierte Taste für "Nein".\n\n' +
                            'Versuchen Sie sich bitte möglichst schnell, aber auch sicher zu entscheiden: Sie haben ' +
                            'bei jeder Runde maximal 30 Sekunden Zeit. ' + space_text,
                  'inst_4': 'Haben Sie noch Fragen? Wenn ja, wenden Sie sich bitte an den/die VersuchsleiterIn.\n' +
                            'Wenn nicht, drücken Sie bitte die Leertaste um mit dem Spiel zu beginnen.'}
# Teenager
__JAP_TXT_B1_T = {'inst_1': 'Danke! Jetzt werden wir kurz die wichtigsten Regeln wiederholen:' + space_text,
                  'inst_2': 'Entweder bist du in der Handlungsrolle:\n\n\n' +
                            'Kurz gesagt: Du bekommst konkrete Aufgaben wie z.B. „Achte auf die Objekte“ oder ' +
                            '„Versuche den Blick des anderen zu leiten“. Folge dieser Anweisung bis zum Ende ' +
                            'der Runde.' + space_text,
                  'inst_3': 'Oder du bist in der Beobachterrolle:\n\n\n' +
                            'Kurz gesagt: Deine Aufgabe ist es herauszufinden, ob dein Spielpartner gerade ' +
                            'versucht, sich mit dir auszutauschen oder nicht.\nDrücke bitte die blaue ' +
                            'mit "J" markierte Taste für "Ja" oder die rote mit "N" markierte Taste für "Nein".\n\n' +
                            'Versuche bitte dich möglichst schnell, aber auch sicher zu entscheiden: Du hast ' +
                            'bei jeder Runde maximal 30 Sekunden Zeit. ' + space_text,
                  'inst_4': 'Hast du noch Fragen?\n\nWenn ja, wende dich bitte an den/die VersuchsleiterIn.\n' +
                            'Wenn nicht, drücke bitte die Leertaste um mit dem Spiel zu beginnen.'}

# Child
__JAP_TXT_B1_C = {'inst_1': 'Danke! Jetzt werden wir kurz die wichtigsten Regeln für dich wiederholen:' + space_text,
                  'inst_2': 'Manchmal solltst du "etwas tun":\n\n\n' +
                            'Kurz gesagt: Du bekommst eine genaue Aufgabe wie z.B. „Achte auf die Objekte.“ ' +
                            'Folge dieser Anweisung bis zum Ende der Runde.' + space_text,
                  'inst_3': 'Oder du bist in der Beobachterrolle:\n\n\n' +
                            'Kurz gesagt: Deine Aufgabe ist es herauszufinden, ob dein Spielpartner gerade ' +
                            'versucht, sich mit dir auszutauschen oder nicht.\nDrücke bitte die blaue ' +
                            'mit "J" markierte Taste für "Ja" oder die rote mit "N" markierte Taste für "Nein".\n\n' +
                            'Versuche bitte dich möglichst schnell, aber auch sicher zu entscheiden: Du hast ' +
                            'bei jeder Runde maximal 30 Sekunden Zeit. ' + space_text,
                  'inst_4': 'Hast du noch Fragen? Wenn ja, frage bitte die Versuchsleiterin oder den ' +
                            'Versuchtsleiter.\nWenn nicht, drücke bitte die Leertaste um mit dem Spiel zu ' +
                            'beginnen.'}

# Dictionary collecting all age specific instructions
JAP_TXT_B1 = {
              'child': __JAP_TXT_B1_C,
              'teen_young': __JAP_TXT_B1_T,
              'teen_old': __JAP_TXT_B1_T,
              'adult_young': __JAP_TXT_B1_A,
              'adult_old': __JAP_TXT_B1_A,
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

# ==============================================================================
# ==============================================================================
# ====================== AGENT'S MACRO STATE SEQUENCE ==========================
# ==============================================================================
# ==============================================================================

# List of integers how many times each macro state shall occour in the final sequence
# (If only one value is given, it will be used for all macro states)
JAP_TIMES_PER_MACRO_STATE = [1]
# Min time in [s] after which a button press is accepted during a block to finish it
JAP_MIN_BLOCK_DUR = 2

# Text to be shown right before a new trial starts
JAP_AGT_TXT_B1 = {
                  'PA_OO': {age_group: inst['round_start'] for age_group, inst in JAP_INBTW_TEXT.items()},
                  'PA_PO': {age_group: inst['round_start'] for age_group, inst in JAP_INBTW_TEXT.items()},
                  'PA_I': {age_group: inst['round_start'] for age_group, inst in JAP_INBTW_TEXT.items()},
                  'IJA': {age_group: inst['round_start'] for age_group, inst in JAP_INBTW_TEXT.items()},
                  'RJA': {age_group: inst['round_start'] for age_group, inst in JAP_INBTW_TEXT.items()},
                  }

JAP_AGT_TXT_PILOT = {
                     'PA_PO': {age_group: inst['Partner_oriented'] for age_group, inst in JAP_INSTR_TEXT.items()},
                     'PA_I': {age_group: inst['Introspective'] for age_group, inst in JAP_INSTR_TEXT.items()},
                     'PA_OO': {age_group: inst['Object_oriented'] for age_group, inst in JAP_INSTR_TEXT.items()},
                     'IJA': {age_group: inst['IJA_Agent'] for age_group, inst in JAP_INSTR_TEXT.items()},
                     'RJA': {age_group: inst['RJA_Agent'] for age_group, inst in JAP_INSTR_TEXT.items()},
                     }

# A list to define the blocks used in the experiment (can be selected via GUI)

# Each element of this list is a block type which can be selected via the GUI (use -r when calling experiment.py to
# cycle through all blocks for current HI)

# A trial is defined the following way:
# [agent state, instruction before block (None if set to none), accept button press to end trial,
# position of correct object]

JAP_BLOCK_LIST = [
                  # Pratice parts
                  {
                   'name': 'practice_Pilotstudie',
                   'min_time': JAP_MIN_BLOCK_DUR,
                   #            Agent state , instructions ,         keypress, correct positon,
                   'sequence': [
                                {'agent': 'RJA_Agent', 'instr': None, 'trial_type': None,
                                 'trial_param': {'accept_keypress': False}},
                                {'agent': 'IJA_Agent', 'instr': None, 'trial_type': None,
                                 'trial_param': {'accept_keypress': False}},
                                 {'agent': 'OO_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                                 'trial_param': {'accept_keypress': False}},
                                 {'agent': 'PO_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                                 'trial_param': {'accept_keypress': False}},
                                 {'agent': 'INT_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                                 'trial_param': {'accept_keypress': False}},
                               ],
                   'states': None,
                   'times_per_state': None,
                   'baseline': False,
                  },
                  {
                   'name': 'practice_Basisstudie',
                   'min_time': JAP_MIN_BLOCK_DUR,
                   'sequence': [
                                {'agent': 'OO_Agent', 'instr': JAP_AGT_TXT_B1['PA_OO'], 'trial_type': None,
                                'trial_param': {'accept_keypress': True}}, {'agent': 'IJA_Agent', 'instr':
                                JAP_AGT_TXT_B1['IJA'], 'trial_type': None, 'trial_param': {'accept_keypress': True}},
                                {'agent': 'PO__Agent', 'instr': JAP_AGT_TXT_B1['PA_PO'], 'trial_type': None,
                                'trial_param': {'accept_keypress': True}}, {'agent': 'RJA_Agent', 'instr':
                                JAP_AGT_TXT_B1['RJA'], 'trial_type': None, 'trial_param': {'accept_keypress': True}},
                                {'agent': 'INT_Agent', 'instr': JAP_AGT_TXT_B1['PA_I'], 'trial_type': None,
                                'trial_param': {'accept_keypress': True}},
                               ],
                   'states': None,
                   'times_per_state': None,
                   'baseline': False,
                  },
                  # Experimental parts (does not work because make_now_really_real_jap_sequence is outdated)
                  {'name': 'block_01',
                   'min_time': JAP_MIN_BLOCK_DUR,
                   'sequence': None,
                   'states': [
                              # Verhaltensrolle
                              {'agent': 'PO_Agent', 'instr': JAP_AGT_TXT_B1['PA_PO'], 'trial_type': None,
                              'trial_param': {'accept_keypress': True}}, {'agent': 'OO_Agent', 'instr':
                              JAP_AGT_TXT_B1['PA_OO'], 'trial_type': None, 'trial_param': {'accept_keypress': False}},
                              {'agent': 'PO_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                              'trial_param': {'accept_keypress': False}},
                              {'agent': 'INT_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                              'trial_param': {'accept_keypress': False}}, {'agent': 'OO_Agent', 'instr':
                              JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None, 'trial_param': {'accept_keypress': False}},
                              {'agent': 'INT_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                              'trial_param': {'accept_keypress': False}},
                              {'agent': 'IJA_Agent', 'instr': None, 'trial_type': None, 'trial_param':
                              {'accept_keypress': False}}, {'agent': 'IJA_Agent', 'instr': None, 'trial_type': None,
                              'trial_param': {'accept_keypress': False}},
                              {'agent': 'RJA_Agent', 'instr': None, 'trial_type': None, 'trial_param':
                              {'accept_keypress': False}}, {'agent': 'RJA_Agent', 'instr': None, 'trial_type': None,
                              'trial_param': {'accept_keypress': False}},
                              # Beobachterrolle
                               {'agent': 'PO_Agent', 'instr': JAP_AGT_TXT_B1['PA_PO'], 'trial_type': None,
                               'trial_param': {'accept_keypress': True}}, {'agent': 'OO_Agent', 'instr':
                               JAP_AGT_TXT_B1['PA_OO'], 'trial_type': None, 'trial_param': {'accept_keypress': True}},
                               {'agent': 'PO_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                               'trial_param': {'accept_keypress': False}}, {'agent': 'INT_Agent', 'instr':
                               JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None, 'trial_param': {'accept_keypress': True}},
                               {'agent': 'OO_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                               'trial_param': {'accept_keypress': True}},
                               {'agent': 'INT_Agent', 'instr': JAP_AGT_TXT_PILOT['IJA'], 'trial_type': None,
                               'trial_param': {'accept_keypress': True}},
                               {'agent': 'IJA_Agent', 'instr': None, 'trial_type': None, 'trial_param':
                               {'accept_keypress': False}}, {'agent': 'IJA_Agent', 'instr': None, 'trial_type': None,
                               'trial_param': {'accept_keypress': True}},
                               {'agent': 'RJA_Agent', 'instr': None, 'trial_type': None, 'trial_param':
                               {'accept_keypress': False}}, {'agent': 'RJA_Agent', 'instr': None, 'trial_type': None,
                               'trial_param': {'accept_keypress': True}},
                            ],
                   'times_per_state': JAP_TIMES_PER_MACRO_STATE,
                   'baseline': False,
                  }]
# Dictionary containing macro state durations in [s] [with keypress, without keypress]
JAP_BLOCK_DUR_DICT = {
                      'child': [10, 10],
                      'teen_young': [10, 10],
                      'teen_old': [10, 10],
                      'adult_young': [10, 10],
                      'adult_old': [10, 10]
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

# =============================================================================
# =============================================================================
# OBJECT PARAMETERS
# =============================================================================
# =============================================================================

# Get new objects for each block (needs some 1-2 seconds to recreate correspoding screens)
JAP_NEW_OBJECTS = False

# Path list to object files
JAP_TAR_DIR_LIST = [path.join(JAP_OBJ_DIR, 'cubes')]

__JAP_TAR_NAME_1 = 'tar_down_left'
__JAP_TAR_NAME_2 = 'tar_up_left'
__JAP_TAR_NAME_3 = 'tar_down_right'
__JAP_TAR_NAME_4 = 'tar_up_right'

JAP_TAR_NAMES = [__JAP_TAR_NAME_1, __JAP_TAR_NAME_2, __JAP_TAR_NAME_3, __JAP_TAR_NAME_4]

# Object ccordinates
JAP_FACT_UPPER_TARGETS = 0.282  #
JAP_FACT_LEFT_TARGETS = 0.2   #
JAP_TAR_SIZE = (1000, 200)  # Target size in pixels
JAP_R = 600  # Radius in pixels from center of the screen on which targets will be distributed
JAP_PHI_1 = pi  # Angle in radian for direction of first target
JAP_PHI_2 = 17 * pi / 24  # Angle in radian for direction of second target
JAP_PHI_3 = 7 * pi / 24  # Angle in radian for direction of third target
JAP_PHI_4 = 0  # Angle in radian for direction of fourth target

# ONLY ONE OF THESE SHOULD ACTUALLY BEEN NEEDED C.F. ISSUE #30
# Dict for mapping agent's gaze direction to AOI
JAP_TRANS_DICT = {
                 'left': __JAP_TAR_NAME_1,
                 'up_left': __JAP_TAR_NAME_2,
                 'right': __JAP_TAR_NAME_3,
                 'up_right': __JAP_TAR_NAME_4,
                 'straight': 'straight',
                 'AOI_agent_upper_face': 'straight',
                 'AOI_agent_eyes': 'straight',
                 'AOI_agent_lower_face': 'straight'
}

# Dict for mapping AOI to agent's gaze direction
JAP_TRANS_DICT2 = {
                  __JAP_TAR_NAME_1: 'left',
                  __JAP_TAR_NAME_2: 'up_left',
                  __JAP_TAR_NAME_3: 'right',
                  __JAP_TAR_NAME_4: 'up_right',
                  'straight': 'straight',
                  'AOI_agent_upper_face': 'straight',
                  'AOI_agent_eyes': 'straight',
                  'AOI_agent_lower_face': 'straight'
}

# =============================================================================
# =============================================================================
# ================================= MISC ======================================
# =============================================================================
# =============================================================================

# If set to True, Noldus FaceReader will be used to anaylize emotional state of HI in real time (no agent interactivity
# so far implemented)
JAP_FACE_READING = False


def __jap_pos(r, phi):
    """
    Function to get cartheisan coordinates (in unit pixels) from polar coordinates, used for target positioning
    :param r: Radius
    :type r: double
    :param phi: degree in [rad]
    :type phi: double
    """
    return [int(JAP_AGT_POS[0] + r * cos(phi)), int(JAP_AGT_POS[1] - r * sin(phi))]

JAP_TAR_POS = {
              __JAP_TAR_NAME_1: __jap_pos(JAP_R, JAP_PHI_1),
              __JAP_TAR_NAME_2: __jap_pos(JAP_R, JAP_PHI_2),
              __JAP_TAR_NAME_4: __jap_pos(JAP_R, JAP_PHI_3),
              __JAP_TAR_NAME_3: __jap_pos(JAP_R, JAP_PHI_4)
}
