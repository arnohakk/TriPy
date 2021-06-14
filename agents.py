import pygaze
from pygaze import libtime
# from constants import *
from threading import Thread, Event
from framework.stuff import colored_text, encapsulate_text, print_threads
import os.path
from numpy.random import normal as gauss
from numpy.random import poisson, choice, uniform, lognormal
from numpy import exp
from scipy.stats import exponnorm
import time


class AgentMacroBehavior(Thread):
    """ A class to "play through" the agents's behavioral macro state sequence by looping over a list defined in
    individual study file (in sub dir studies). It handles the start current macro state of the current trial,
    sets behavioral parameters, as well as presentation of intructions and rewards.

    :param wait_4_instr: Event to wait for instruction screens to finish
    :type wait_4_instr: :class:`threading.Event`
    :param draw: Event to send a message to main thread handling display visualization
    :type draw: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param draw_lock: Create an event that is fired when screen needs to be updated on the display.
    :type draw_lock: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param agent_finished_event: An event to tell this agent that a sub agent is finished
    :type agent_finished_event: :obj:`threading.Event`
    :param finished_event: An event for signaling that current macro state is finished
    :type finished_event: :obj:`threading.Event`
    :param list_behavior_always_on: List of macro states that are always expressed (BlinkingAgent)
    :type list_behavior_always_on: list
    :param behavioral_sequence: Sequence of macro states with correspoding parameters
    :type behavioral_sequence: dictionary
    :param startgaze: Gaze direction at the beginning of a macro state
    :type startgaze: string
    :param trans_dict: Translating between gaze directions of the agent and AOI names
    :type trans_dict: dictionary
    :param age_group: Age group, defining which instruction text used later on
    :type age_group: string
    :param accept_key_input: Indicating whether a trial can be terminated via a button press
    :type accept_key_input: Boolean
    :param save_trigger: ???
    :type save_trigger: ??? tobii logger
    :param gamehub: Keeps track of scores gained via successful JA
    :type gamehub: :class:`jap_pygaze_framework`
    :param accumulative_agents: All macro states that are possible in the given study
    :type accumulative_agents: list item ??
    :param *agents: EMOTISK_agent agent objects
    """

    def __init__(self, wait_4_instr, draw, draw_lock, agent_finished_event, finished_event, list_behavior_always_on,
                 point_scr_dur, behavioral_sequence, baseline, startgaze, start_gaze_dur, trans_dict, age_group,
                 accept_key_input, save_trigger, gamehub, nirs_stuff, accumulative_agents, *agents):
        Thread.__init__(self, name='AgentMacroBehavior')
        # TOCHECK
        import pygaze
        print('Initializing AgentMacroBehavior...')

        # ASSIGNED STUFF
        # -- EVENTS to communicate across threads
        self.wait_4_instr = wait_4_instr  # Wait for instruction screens to finish (if presented)
        self.draw = draw  # Send a message to main thread handling display visualization via PsychoPy
        self.draw_lock = draw_lock  # ?? (BJFRGN)
        self.agent_finished_event = agent_finished_event  # Check if trial has finished through its running time
        self.finished_event = finished_event  # Signal that the entire behavioral sequence is finished

        # -- MACRO BEHAVIOR STUFF
        self.macrostates_always_on = list_behavior_always_on  # List of macro states that are always expressed (blinks)
        self.point_scr_dur = point_scr_dur  # Interval from which duration of point screen is drawn uniformly
        self.behavioral_sequence = behavioral_sequence  # List containing sequence of macro behavioral states

        # -- HI stuff
        self.age_group = age_group  # Age group of HI to select correct screens for instructions and avatar selection
        # Set the accepted key inputs to break the run() lopp of the currently running marco state (agent)
        self.accept_key_input_default = accept_key_input
        self.accept_key_input = self.accept_key_input_default

        self.nirs_stuff = nirs_stuff  # Shall a basline screen be shown at start and end?

        # -- AGENT MECHANIC STUFF
        # Set start gaze for the beginning of each trial
        if 'no_obj' in startgaze:
            self.first_shift = 'straight_no_obj'
        else:
            self.first_shift = 'straight'
        self.trans_dict = trans_dict  # Dictionary translating between AOIs and agent's gaze directions

        # MISC
        self.save_trigger = save_trigger  # function to save exe tracker data
        self.gamehub = gamehub  # Add game hub for keeping track of scores
        # -- AGENT STUFF
        self.accumulative_agents = accumulative_agents  # List of all accumulative agents (BJFRGN)
        self.agents = {}  # dict for macro states
        # add dictionary for behavioral states (only one will be running at any given time)
        for agent in agents:
            self.agents[agent['name']] = agent

        # Prepare logging
        self.list_macro_states = []  # list where all macro states will be appended
        self.behavioral_sequence_history = []  # history of macro states
        self.time_gaze_lag = []
        self.all_states = self.macrostates_always_on + self.list_macro_states
        self.time_agent_started = None

        self.daemon = True  # set necessary variables for running as a threading.Thread
        self.correct_object = None  # Variable to set correct object position
        self.show_wait_screen = False  # Show a screen indicating to participant that she should "wait" for her partner
        self.trials_done = 0
        self.total_trials_done = 0
        self.show_baseline = baseline  # Whether a baseline should be shown (for fNIRS recording)
        self.start_gaze_dur = int(start_gaze_dur/100)  # Compute duration of start gaze (used for stimtracker signal)
        print('... AgentMacroBehavior initialized.')

    def run(self):
        """
        Method "playing through" macro state sequence. Will create necessary macro states (agents) with adapted trial
        parameters as defined in study file.

        """

        print(encapsulate_text('Starting macro state sequence...', color='green'))

        self.gamehub.event.set('dummy')  # Fire dummy event to start correct gamehub logging
        # Make sure correct screens are used in very first trial (don't know why it does not work when first in loop)
        if self.behavioral_sequence[0]['trial_type']:
            self.draw_lock.acquire()
            self.draw.set_micro_state('__change_screens__', self.behavioral_sequence[0]['trial_type'],
                                      time=libtime.get_time())
            self.draw.clear()

        # Loop over macro state sequence
        for macro_state in self.behavioral_sequence:
            # Set correct screens if defined
            if macro_state['trial_type']:
                self.draw_lock.acquire()
                self.draw.set_micro_state('__change_screens__', macro_state['trial_type'], time=libtime.get_time())
                self.draw.clear()

            # MACRO STATE CREATION
            # Assign agent object for current macro state
            if macro_state["agent"] in self.accumulative_agents:
                agent = self.agents[macro_state["agent"]]['class'](self.agents[macro_state["agent"]], macro_state[3])
            else:
                agent = self.agents[macro_state["agent"]]['class'](self.agents[macro_state["agent"]])

            print(encapsulate_text('New macro state running: ' + agent.name, color='green'))

            # define place to save a gaze lag
            # is this still used? (??)
            if agent.name == 'IJA_Agent':
                self.time_gaze_lag = agent.gaze_lag

            # If given, change agent parameters
            if macro_state["trial_param"]:
                for key, value in macro_state["trial_param"].items():
                    if key == 'run_time':
                        value = value*1000  # Convert run_time to [ms]
                    agent.change_parameter(key, value)  # Set other values

            # Set macro state parameters
            self.show_vid = agent.show_vid  # Set whether to present score/reward video
            self.show_points = agent.show_points #(??)
            self.point2score = agent.point2view  # Set who many points are needed to display reward
            self.trials2view = agent.trials2view  # Set who many trials are needed to display reward

            print_threads()  # Print running threads

            # Wait if something is being drawn right now
            while self.draw.is_set():
                pass

            # Create screens
            self.draw_lock.acquire()
            self.draw.set_micro_state('__new_screens__', msg2='empty', time=libtime.get_time())  # Create new screens
            # self.draw.set_micro_state('__new_screens__', msg2=' ', time=libtime.get_time())  # Create new screens

            # Set all events correctly
            self.wait_4_instr.wait()
            self.wait_4_instr.clear()
            self.draw.clear()

            #############################
            # Begin screen presentation #
            #############################

            # If set, show (age-adapted) instruction screen
            show_instructions = False
            if macro_state['instr']:
                if len(macro_state['instr']) > 1:
                    if macro_state['instr'][self.age_group]:
                        instr = macro_state['instr'][self.age_group]
                        show_instructions = True
                elif len(macro_state['instr']) == 1 and macro_state['instr'] is not None:
                        instr = macro_state['instr']
                        show_instructions = True
            if show_instructions:
                self.draw_lock.acquire()
                self.draw.set_micro_state('__instruction_screen__', instr, time=libtime.get_time())
                self.draw.clear()
                self.wait_4_instr.wait(timeout=300)  # Wait for a key press by participant
                self.wait_4_instr.clear()
            # Set correct fNIRS trigger for block type
            if self.nirs_stuff['use']:
                if agent.gaze_down:
                    trig_msg = 'trigger_' + agent.name[0:3] + 'c_start'
                else:
                    trig_msg = 'trigger_' + agent.name[0:3] + '_start'
                self.draw_lock.acquire()
                self.draw.set_micro_state('__send_trigger__', msg2=trig_msg, time=libtime.get_time())
                self.draw.clear()

            # -- Begin agent presentation

            # Show start gaze screen five times (total ~500ms) with stimtracker trigger pixel in 100 ms intervals to
            # mark the start of a trial
            for i in range(self.start_gaze_dur):
                self.draw_lock.acquire()
                self.draw.set(msg='startgaze'+str(i), time=libtime.get_time())
                self.draw.clear()
                time.sleep(0.1)
            # Make agent gaze in initial gaze direction
            self.draw_lock.acquire()
            self.draw.set_micro_state(self.first_shift, self.first_shift, time=libtime.get_time())
            self.draw.clear()
            time.sleep(0.1)
            # If set, try to take a screenshot (not functional)
            if False:
                self.draw_lock.acquire()
                self.draw.set('__screenshot__')
                self.draw.clear()
                time.sleep(0.1)

            # Create always on agents (i.e. blinking agent)
            agents_always_on = []
            for a in self.macrostates_always_on:
                agents_always_on.append(self.agents[a]['class'](self.agents[a]))

            # Inform current macro state about its start time to determine max duration
            agent.change_parameter('time_start', libtime.get_time())
            agent.start()  # Start macro state thread
            self.time_agent_started = libtime.get_time()  # Get time when agent is started

            # Start always on agents
            for a in agents_always_on:
                a.start()
            self.behavioral_sequence_history.append(macro_state['agent'])  # log state
            # Wait until time in macro state is up (BJFRGN)
            self.agent_finished_event.wait(timeout=agent.run_time+10)
            print('Macro state ' + macro_state['agent'] + ' finished')
            self.draw.do_blink = False  # Make sure that not a blink will finish the trial
            # stop all always on agents (i.e. BlinkingAgent.
            for a in agents_always_on:
                a.stop()
                a.force_finish_event.set()
                a.stop_blinking()
            print('Blinking agent finished')

            # Wait for all agents to finish
            all_finished = False
            while not all_finished:
                all_finished = True
                for a in agents_always_on:
                    if a.is_alive():
                        all_finished = False
                        break
            print('All finished')
            self.trials_done += 1
            self.total_trials_done += 1

            # Send fNIRS signal that block has ended
            if self.nirs_stuff['use']:
                if agent.gaze_down:
                    trig_msg = 'trigger_' + agent.name[0:3] + 'c_end'
                else:
                    trig_msg = 'trigger_' + agent.name[0:3] + '_end'
                self.draw_lock.acquire()
                self.draw.set_micro_state('__send_trigger__', msg2=trig_msg, time=libtime.get_time())
                self.draw.clear()

            # -- REWARD PRESENTATION
            # If set, present number of correct objects
            # TOCHECK: eigener parameter (??)
            if self.show_points:
                msg = 'points_' + str(self.gamehub.score_correct_objects)
                if self.draw.msg4:
                    msg = msg + '_correct'
                else:
                    msg = msg + '_wrong'
                self.draw_lock.acquire()
                self.draw.set_micro_state(msg,  time=libtime.get_time())
                if self.point_scr_dur:
                    time.sleep(uniform(self.point_scr_dur[0], self.point_scr_dur[1]))
                self.draw.clear()

            # IF set AND enough points are reached, present reward video stimulus
            # and reset points
            if self.show_vid and (self.gamehub.score_correct_objects >= self.point2score or
               self.trials_done >= self.trials2view):
                self.draw_lock.acquire()
                self.draw.set_micro_state('video', 'correct', time=libtime.get_time())
                self.draw.clear()
                self.gamehub.score_correct_objects = 0
                self.trials_done = 0
                if self.nirs_stuff['baseline'] and self.show_baseline:
                    if self.total_trials_done == len(self.behavioral_sequence):
                        bl_min = self.nirs_stuff['baseline_duration'][0]
                        bl_max = self.nirs_stuff['baseline_duration'][1]
                    else:
                        bl_min = self.nirs_stuff['baseline_duration_2'][0]
                        bl_max = self.nirs_stuff['baseline_duration_2'][1]
                    self.draw_lock.acquire()
                    self.draw.set_micro_state('__baseline__', msg2=bl_min, msg3=bl_max, time=libtime.get_time())
                    self.draw.clear()

            # IF set, show a questionnaire at the end of the agent's run
            questionnaire_event = Event()
            self.draw_lock.acquire()
            if agent.did_key_press:
                self.draw.set_micro_state('__questionnaire__', questionnaire_event)
            else:
                self.draw.set_micro_state('__initial_questionnaire__', questionnaire_event)
            self.draw.clear()
            questionnaire_event.wait()

            # IF set, present a waiting screen
            if self.show_wait_screen:
                self.draw_lock.acquire()
                self.draw.set_micro_state('__wait_screen__', time=libtime.get_time())
                self.draw.clear()

            # SAVE EYETRACKING DATA
            print(encapsulate_text("Don't panic! Just saving data.", color='red'))
            save_start = libtime.get_time()
            self.save_trigger.set()
            self.save_trigger.clear()
            self.save_trigger.wait()
            print(encapsulate_text('Done saving. Took ' + str(round((libtime.get_time()-save_start)/1000, 2))+'s',
                                   color='green'))
            time.sleep(.1)  # (??) Warum solange? (used to be 2)
            self.agent_finished_event.clear()

        # add a muCap marker to end the last block
        self.draw_lock.acquire()
        self.draw.set_micro_state('__instruction_screen__', ' ')
        self.draw.clear()
        self.finished_event.set() # set event singaling that the entire behavioral sequence is completed
        print(encapsulate_text('Macro state sequence finished.'))

    def add_object(self, objct, name):
        setattr(self, name, objct)


class Agent(Thread):
    """A generic class to manage general aspects of agent's microbehavior.
    Only acts as a parent class to specific child classes for the currently implemented macro states collecting
    pan-state methods() for agent behavior.


    :param cur_agt: Current gaze direction of agent (use start gaze direction)
    :type cur_agt: str
    :param draw: Event to fire when agent will send a messge to update screen to main thread
    :type draw: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param draw_lock: Event to make sure that no two or more thread are trying to send a draw message to change the
                      screen
    :type draw_lock: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param blinking: Event to check wheter agent is currently blinking
    :type blinking: :obj:`threading.Event`
    :param trans_matrix: Macro state's specific probabilitic transition matrix among micro states
    :type trans_matrix: dictionary
    :param questionnaire: questionnaire to be shown when a button is pressed (if active)
    :type questionnaire: dictionary
    :param finished_event: Event to signal AgentMacroBehavior when this agent has finished
    :type finished_event: :obj:`threading.Event`
    :param break_event: Pauses agent
    :type break_event: :obj:`threading.Event`
    :param name: Name for thread of running agent
    :type name: str
    """

    def __init__(self, cur_agt, draw, draw_lock, blinking, trans_matrix=None, questionnaire=None, finished_event=None,
                 break_event=Event(), name='NullAgent'):
        Thread.__init__(self, name=name)

        self.time_start = libtime.get_time()  # Get agent start time
        # EVENTS to communicate across threads
        self.draw = draw
        self.draw_lock = draw_lock
        self.blinking = blinking
        self.finished_event = finished_event
        self.break_event = break_event

        # -- Agent stuff
        self.name = name
        print('Initializing Basic Agent class for ' + self.name)
        self.cur_agt = cur_agt  # Set current agent's appearance
        self.trans_matrix = trans_matrix  # Transition probability dictionary
        self.getting_attention = False  # Will the agent try to get the HI's attention by rapid gaze shifts?
        self.does_know_correct = False
        self.gaze_down = False

        # -- Participant stuff
        # General stuff
        self.did_key_press = True
        self.daemon = True
        self.is_running = False
        self.paused = Event()

        # Boolean indicating whether agent has some knowledge on what
        # object to gaze at
        self.questionnaire = questionnaire  # ??

        # DEFAULT VALUES (used by specific macro states (agents))
        self.correct_aoi = None
        self.wrong_aoi = None
        self.knows_correct_aoi = False
        self.point2view = float('Inf')

        self.draw.do_blink = True
        self.draw.aoi = None  # According AOI to draw
        self.draw.correct_aoi_fixed = None

        print('... initialized Basic Agent Class')

    def change_micro_state(self):
        """
        Method to change the agent's current micro state (i.e. visual appearance a_x) via returning a simple message as
        str.

        New micro state is dicided on whether the agent has knowledge about the correct object
        (self.does_know_correct):
        (i) If True: Gaze with probability self.p_correct_object at correct object, otherwise randonly gaze at any
        other randomnly sampled AOI in self.possible_aois.

        Returns a string used by another method to be send to the main thread handling display visualization.

        """

        rand_num = uniform()  # Sample a random number for a behavioral decision
        if self.does_know_correct:  # Behavior if agent has knowledge about correct object location
            if rand_num < self.p_correct_object:
                return self.correct_aoi
            else:  # Get a wrong gaze direction
                return self.get_wrong_gaze_direction()
        else:  # If not, change gaze direction according to transition probability matrix
            cum_prob = 0.0
            for gaze_direc, gaze_prob in self.trans_matrix[self.cur_agt].iteritems():
                cum_prob += gaze_prob
                if rand_num < cum_prob:
                    print(colored_text(gaze_direc, 'red') + ' | ' + colored_text(str(gaze_prob), 'green'))
                    print(colored_text('New gaze direction: ' + gaze_direc))
                    return gaze_direc

    def get_wrong_gaze_direction(self):
        """ Returns a gaze direction that is defined in self.possible_aois but not currently gazed at by the HI
        """
        temp_aois = list(self.possible_aois)
        if self.cur_agt in temp_aois:
            temp_aois.remove(self.cur_agt)
        return choice(temp_aois)

    def get_new_waiting_time(self, param):
        """
        Method to sample a micro state duration

        :raises: NotImplementedError
        """

        if param[3] == 'gauss':
            l_bound = param[0] - param[4]*param[1]
            u_bound = param[0] + param[4]*param[1]
            while True:
                value = gauss(loc=param[0], scale=param[1])
                if (value > l_bound) and (value < u_bound):
                    return value

        elif param[3] == 'lognormal':
            l_bound = exp(param[0]-param[4]*param[1])
            u_bound = exp(param[0]+param[4]*param[1])
            while True:
                value = lognormal(param[0], param[1])
                if value > l_bound and value < u_bound:
                    return value

        elif param[3] == 'exgauss':
            mu, sigma, lam = param[0], param[1], param[2]
            mean_ex = mu + lam
            var_ex = sigma ** 2 + (1 / lam ** 2)
            K = 1./(sigma*lam)
            l_bound = mean_ex-param[4]*var_ex
            u_bound = mean_ex+param[4]*var_ex
            while True:
                value = exponnorm.rvs(K, loc=mu, scale=sigma)
                if value > l_bound and value < u_bound:
                    return value

        elif param[3] == 'nonrandom':
            return param[0]

        else:
            print('Error in get_new_waiting_time() for distribution type:')
            print(param[3])
            raise(NotImplementedError('Defined random distribution not implemented'))

    def change_parameter(self, name, value):
        """
        Method to change a parameter from agent's default value
        :param name: Name of parameter stored in self. to change
        :type name: str
        :param value: new variable
        :type value: depends on name
        """
        setattr(self, name, value)
        print('Parameter ' + name + ' set to ' + str(value))

    def check_if_finished(self):
        """
        Check whether time in macro state has expired to set condition for running while loop to False
        """
        if (libtime.get_time() - self.time_start > self.run_time) or self.break_event.is_set():
            self.is_running = False
            print('Done with block of macro behavior')

    def stop(self):
        """
        Stop the running agent
        """
        print('MacroState stopped')
        self.is_running = False

    def pause(self):
        """
        Pause the running agent
        """
        self.paused.clear()

    def unpause(self, runs=None):
        """
        Unpause the running agent
        :param runs: ??
        :type runs: Booleans
        """
        self.paused.set()

    def wait_for_event(self, timeout=None):
        """
        Makes agent wait for a event
        :param timeout: Time to max wait for in ???
        :type timeout: double

        """
        self.break_event.wait(timeout=timeout)


class RJA_Agent(Agent):
    """A class to manage the agent's behavior in RJA macro state: It will follow the HI's fixation after a certain
    delay, and, if it starts to get bored, begin to explore the objects around it on its own (for details see methods
    paper and run() method).

    :param fixation_detector: Fixation dector for registering relevant fixation events
    :type fixation_detector: :obj:'pygaze_framework.EventHandler'
    :param cur_agt: Current gaze direction of agent (use start gaze direction)
    :type cur_agt: str
    :param draw: event to fire when redrawing screen on display to participant
    :type draw: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param draw_lock: Create an event that is fired when screen needs to be updated on the display.
    :type draw_lock: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param blinking: event to check whether agent is currently blinking
    :type blinking: :obj:`threading.Event`
    :param trans_dic: Dictionary containing translation
    :type trans_dic: dict
    :param follow_lag: Mean time and variance of agent gaze following in [ms]
    :type follow_lag: list
    :param follow_prob: Probalility of agent following gaze
    :type follow_prob: double in the interval [0,1]
    :param reset_lag: ??
    :type reset_lag: double
    :param straight_agent: ?? not used instead it says start gaze
    :type straight_agent: ??
    :param wait_eye: ??
    :type wait_eye: Boolean
    :param gazes_wrong: ??
    :type gazes_wrong: Boolean
    :param possible_aois: ??
    :type possible_aois: list
    :param bored_parameters: ??
    :type bored_parameters: Dictionary
    :param show_vid: Show a video when participants fixates an object (terminates current agent)
    :type show_vid: list
    :param highlight_obj: Draw a red rectangle around fixated object
    :type highlight_obj: Boolean
    :param questionnaire: questionnaire to be shown when a button is pressed (if active)
    :type questionnaire: dictionary
    :param log_event: ??
    :type log_event: dictionary
    :param finished_event: An event for signaling that time for current macro state is up
    :type finished_event: :obj:`threading.Event`
    :param break_event: Pauses agent
    :type break_event: :obj:`threading.Event`
    :param game_event:
    :type game_event: :obj:`jap_pygaze_framework.gamehub`
    :param name: Name for thread of running agent
    :type name: str
    """

    def __init__(self, fixation_detector, cur_agt, draw, draw_lock, blinking, trans_dic, follow_lag, follow_prob,
                 reset_lag, straight_agent, wait_eye, ja_init_waiting_time, gazes_wrong, possible_aois,
                 break_trial_if_no_mg, single_chance, bored_parameters, show_vid, show_vid_always, show_points,
                 highlight_obj=False, correct_feedback=False, questionnaire=None, log_event=None, finished_event=None,
                 break_event=None, game_event=None, name='RJA_Agent'):
        super(RJA_Agent, self).__init__(cur_agt, draw, draw_lock, blinking,
                                        trans_matrix=bored_parameters['trans_matrix'], questionnaire=questionnaire,
                                        finished_event=finished_event, break_event=break_event, name=name)

        print('Initializing RJA Agent... ')

        self.fixation_detector = fixation_detector  # Fixation detector object for gaze-contingency
        self.trans_dict = trans_dic  # Dict translation between AOIs and gaze directions

        self.follow_lag = follow_lag  # Time after which agent will gaze at object fixated by HI (to establish JA)
        self.follow_prob = follow_prob  # Probability of agent to follow HI's gaze (to establish JA)
        self.break_trial_if_no_mg = break_trial_if_no_mg
        self.single_chance = single_chance
        self.reset_lag = reset_lag
        self.straight_agent = straight_agent
        self.wait_eye = wait_eye
        self.get_bored = bored_parameters['get_bored']
        self.time_to_bore = bored_parameters['time_to_bore']
        self.time_to_look_around = bored_parameters['time_to_look_around']
        self.gazes_wrong = gazes_wrong  # If agents decides not to respond to a JA bid, shall it gaze at a wrong AOI?
        self.possible_aois = possible_aois  # Names of wrong AOIs to choose from when gazing wrong

        self.log_event = log_event
        self.game_event = game_event

        self.highlight_obj = highlight_obj[0]  # Object AOI will be highlighted if fixated by HI
        self.HL_time = highlight_obj[1] / 1000.
        self.show_vid = show_vid[0]  # Inidicats if video is shown when HI fixated an object and trial is terminated
        self.point2view = show_vid[1]
        self.show_points = show_points
        self.show_vid_always = show_vid_always[0]
        self.trials2view = show_vid_always[1]

        self.p_correct_feedback = correct_feedback

        self.last_aoi = None
        self.run_time = []

        self.ja_init_waiting_time = ja_init_waiting_time
        self.max_wait_4_eyecontact = True
        self.max_wait_4_eyecontact_time = 5000.

        print('...initialized RJA Agent.')

    def run(self):

        print('RJA Agent running...')
        self.log_event.set([libtime.get_time(), 'start'])  # Start RJA recorder

        # Clean AOI list and message to make agent only respond to new fixations
        self.fixation_detector.fixation_list = []
        self.fixation_detector.aoi_event.msg = None
        self.draw.msg4 = None  # Clear message for display event

        self.is_running = True
        reset_time_to_wait = True
        reset_time = libtime.get_time()
        is_bored = False  # When set to True agent is bored and starts to explore objects
        mg = False  # Set to true when mututal gaze detected

        # Loop handling gaze shifts
        while self.is_running:
            self.paused.wait()  # wait, if the agent is paused

            # Wait for the next activated AOI
            if reset_time_to_wait:
                if is_bored:
                    waiting_time = self.get_new_waiting_time(self.time_to_look_around)
                else:
                    waiting_time = self.get_new_waiting_time(self.time_to_bore)
                reset_time = libtime.get_time()
                time_to_wait = reset_time + waiting_time
                reset_time_to_wait = False

            # Get some sort of fixation timeout for waiting time and the fixation detector
            fixation_timeout = waiting_time - reset_time + libtime.get_time() - \
                self.fixation_detector.tracker.fixtimetresh

            # Get currently fixated AOI
            active_aoi = self.fixation_detector.aoi_event.wait(timeout=fixation_timeout/1000.)
            self.fixation_detector.aoi_event.clear()

            # If set, wait for eyecontact
            if self.wait_eye and not mg:
                t_ja_waiting = self.get_new_waiting_time(self.ja_init_waiting_time)
                t_ja_waiting_start = libtime.get_time()
                print('RJA agent is waiting for eye contact')
                while active_aoi is not 'AOI_agent_eyes' and libtime.get_time() < t_ja_waiting + t_ja_waiting_start:
                    active_aoi = self.fixation_detector.aoi_event.wait(timeout=fixation_timeout/1000)
                    time.sleep(.1)
                    print('HI looking at ' + str(active_aoi))
                    self.fixation_detector.aoi_event.clear()
                if active_aoi is 'AOI_agent_eyes':
                    mg = True
                    print('Eye contact established')
                else:
                    print('No eye contact established')
                    self.is_running = False

            if not self.wait_eye or mg:
                # check whether last and current AOIs are different to indicate new JA attempt
                if active_aoi != self.last_aoi:
                    if self.log_event and active_aoi:
                        self.log_event.set([libtime.get_time(), 'JA_initiated', active_aoi])

                    # wait if the agent is currently blinking
                    self.blinking.acquire()
                    self.blinking.release()
                    # Check whether agent is following,and if, whether to gaze at correct or wrong AOI
                    rand_num = uniform()  # Sample number [0,1] to make behavioral decision whether to follow or not
                    if self.gazes_wrong or self.follow_prob > rand_num:
                        # Trigger drawing of the current agent
                        if active_aoi in self.trans_dict:

                            # print('active aoi: ' + active_aoi)  # Print currently fixated AOI
                            self.cur_agt = self.trans_dict[active_aoi]  # Get correspoding gaze direction
                            # Wait time JAP_AGT_FOLLOW_LAG
                            self.break_event.wait(self.get_new_waiting_time(self.follow_lag)/1000.)

                            # Change micro state
                            self.draw_lock.acquire()  # Make sure only this agent tries to draw
                            if not self.gaze_down:
                                if self.follow_prob > rand_num or active_aoi is 'AOI_agent_eyes':  # Is following
                                    print(colored_text('FOLLOWS CORRECT', 'green'))
                                    agt2draw = self.cur_agt
                                else:  # Gazes at wrong AOI
                                    print(colored_text('FOLLOWS WRONG', 'red'))
                                    agt2draw = self.get_wrong_gaze_direction()
                            else:
                                if active_aoi is 'AOI_agent_eyes':
                                    agt2draw = self.cur_agt
                                else:
                                    agt2draw = 'down'

                            # print('New agents gaze direction: ' + agt2draw)
                            self.draw.set_micro_state(agt2draw, agt2draw, time=libtime.get_time())
                            self.log_event.set([libtime.get_time(), 'Agent_followed', agt2draw])  # Log gaze following
                            self.draw.clear()  # Allow other agents to draw
                            # print(colored_text('followed', 'green'))

                            # If set, set draw() message to highlight currently fixated object
                            if self.highlight_obj and active_aoi is not None and active_aoi is not 'AOI_agent_eyes':
                                if active_aoi == self.trans_dict[self.correct_aoi]:
                                    if uniform() <= self.p_correct_feedback:
                                        correct_aoi_fixed = True
                                    else:
                                        correct_aoi_fixed = False
                                else:
                                    if uniform() <= self.p_correct_feedback:
                                        correct_aoi_fixed = False
                                    else:
                                        correct_aoi_fixed = True

                                msg3 = [self.fixation_detector.aois[active_aoi].pos[0],
                                        self.fixation_detector.aois[active_aoi].pos[1],
                                        self.fixation_detector.aois[active_aoi].size[0],
                                        self.fixation_detector.aois[active_aoi].size[1]]
                                self.blinking.acquire()
                                self.blinking.release()
                                self.draw_lock.acquire()
                                time.sleep(self.HL_time * 2.)
                                self.draw.set_micro_state(agt2draw, agt2draw, msg3, correct_aoi_fixed,
                                                          libtime.get_time())
                                time.sleep(self.HL_time)
                                self.draw.clear()
                            else:
                                msg3 = None
                                correct_aoi_fixed = False

                            # log a successful JA to the game log
                            self.game_event.set('success')
                            self.break_event.wait(self.get_new_waiting_time(self.reset_lag)/1000.)
                            reset_time_to_wait = True
                    # Behavior if agent does not follow
                    elif active_aoi:
                        # Give info that the agent did not follow gaze
                        self.log_event.set([libtime.get_time(), 'Agent_not_followed', active_aoi])
                        print(colored_text('did not follow', 'red'))
                        self.game_event.set('failure')  # log a failed JA to the game log

                    self.last_aoi = active_aoi
                    is_bored = False

                    if active_aoi not in {'AOI_agent_eyes', None}:
                        if correct_aoi_fixed:  # If correct AOI was fixated
                            self.game_event.set('correct_object', time=libtime.get_time())
                            correct_aoi_fixed = None
                        else:
                            pass
                        #if self.single_chance:
                        #    self.is_running = False
                        self.get_bored = False

                # If there is now new AOI and the agent is supposed to show boredom, start showing it
                elif self.get_bored and libtime.get_time() > time_to_wait:
                    print(encapsulate_text("I'm bored...", color='blue', background='white'))
                    is_bored = True
                    # Draw a new micro state for the agent, who is looking around bored.
                    self.blinking.acquire()
                    self.blinking.release()
                    self.draw_lock.acquire()  # Make sure only this agent tries to draw
                    self.cur_agt = self.change_micro_state()
                    self.draw.set_micro_state(self.cur_agt, self.cur_agt, time=libtime.get_time())
                    self.draw.clear()  # Allow other agents to draw
                    reset_time_to_wait = True

                # If there was no AOI activated, reset everything to straight agent
                # if not active_aoi and not self.get_bored:
                #     self.cur_agt = self.straight_agent
                #     self.blinking.acquire()
                #     self.blinking.release()
                #     self.draw_lock.acquire()
                #     self.draw.set(self.cur_agt, libtime.get_time())
                #     print('==========')
                #     print(self.cur_agt)
                #     print('==========')
                #     blubb
                #     self.draw.clear()
                self.check_if_finished()

        # Finishing up agent
        self.log_event.set([libtime.get_time(), 'stop'])
        if not self.break_event.is_set():
            self.did_key_press = False
        self.break_event.clear()
        self.finished_event.set()
        print self.correct_aoi
        print('RJA_Agent finished')


class RJA_Agent_Dict(RJA_Agent):
    """
    A derivative of RJA_Agent to create an agent with its parameters in a dictionary
    :param Parameter: ??
    :type parameter: dictionary
    """

    def __init__(self, parameter):
        super(RJA_Agent_Dict, self).__init__(parameter['fixation_detector'], parameter['cur_agt'],
                                             parameter['draw_event'], parameter['draw_lock'], parameter['blink_event'],
                                             parameter['translation_dict'], parameter['follow_lag'],
                                             parameter['follow_prob'], parameter['reset_lag'], parameter['start_gaze'],
                                             parameter['wait_eye'], parameter['ja_init_waiting_time'],
                                             parameter['gazes_wrong'], parameter['possible_aois'],
                                             parameter['break_trial_if_no_mg'], parameter['single_chance'],
                                             parameter['bored_parameters'], parameter['show_vid'],
                                             parameter['show_vid_always'], parameter['show_points'],
                                             parameter['highlight_obj'], parameter['correct_feedback'],
                                             parameter['questionnaire'], parameter['log_event'],
                                             parameter['finished_event'], parameter['break_event'],
                                             parameter['game_event'])
        self.paused.set()
        print(parameter['break_event'])
        print(encapsulate_text(str(self.break_event), color='green'))


class IJA_Agent(Agent):
    """A class to manage avatar's behavior: In this mode, the avatar will explore the items presented on the screen.

    :param fixation_detector: Fixation detector to fire AOI events
    :type fixation_detector: :obj:'pygaze_framework.EventHandler'
    :param cur_agt: Current gaze direction of agent (use start gaze direction)
    :type cur_agt: str
    :param draw: Event that fires when display shall be updated to participant
    :type draw: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param draw_lock: Create an event that is fired when screen needs to be updated on the display.
    :type draw_lock: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param blinking: :param blinking: Event to check wheter agent is currently blinking
    :type blinking: :obj:`threading.Event`
    :param trans_matrix: Martix containing transition probabilities amoung microstates
    :type trans_matrix: dictionary
    :param agt_straight: Time of agent looking straight before fixating object
    :type agt_straight: list
    :param t_gaze_at_obj_ija: Time in [ms] after which agent will start trying to get participant's attention
    :type t_gaze_at_obj_ija: double
    :param t_gaze_straight:  Mean time to change microstate in [ms]
    :type t_gaze_straight: float
    :param subj_fix_t:  Part will be looked at while agent is trying to get attention
    :type subj_fix_t: list (double)
    :param t_2_look_straight_again: Time after succ. IJA before agent looks straight again
    :type t_2_look_straight_again: list (double)
    :param ja_init_waiting_time: Time to wait before initaitong joint attention
    :type ja_init_waiting_time: list
    :param ja_init_aois: AOI to wait for before initiating joint attention
    :type ja_init_aois: list (str)
    :param trans_dict: ??? translating between gaze directions of the agent and AOI names
    :type trans_dict: dictionary
    :param p_correct_object: Probalility that IJA agent will select correct object, set to *None* to turn off
    :type p_correct_object: double
    :param possible_aois: ??
    :type possible_aois: list
    :param get_attention_parameters: IJA get_attention() method parameters
    :type get_attention_parameters: dictionary
    :param show_vid: Show a video when participants fixates an object (terminates current agent)
    :type show_vid: list
    :param highlight_obj: Draw a red rectangle around fixated object
    :type highlight_obj: Boolean
    :param questionnaire: questionnaire to be shown when a button is pressed (if active)
    :type questionnaire: dictionary
    :param log_event: ??
    :type log_event: dictionary
    :param finished_event: An event for signaling that time for current macro state is up
    :type finished_event: :obj:`threading.Event`
    :param break_event: Pauses agent
    :type break_event: :obj:`threading.Event`
    :param game_event: ??
    :type game_event: :obj:`jap_pygaze_framework.gamehub`
    :param name: Name for thread of running agent
    :type name: str
    """

    class AOI_Checker(Thread):
        """Class to check whether fixation_detector is in any given AOI
        :param fixation_detector: Objecct sending messages of a fixation events
        :type fixation_detector: :obj:'pygaze_framework.EventHandler'
        :param name: Name of thread
        :type name: str
        """

        def __init__(self, fixation_detector, name='AOI_Checker'):
            super(IJA_Agent.AOI_Checker, self).__init__(name=name)
            self.fixation_detector = fixation_detector
            self.name = name
            self.running = False
            self.unpaused = Event()
            self.unpaused.set()
            self.daemon = True
            self.cur_aoi = []
            self.aoi_fixed = []
            print('AOI Checker Agent initialized...')

        def run(self):
            """
            The function running in once AOI_Checker.start() is executed.
            Don't run this function by hand, but only by starting the thread!
            """
            # set the bool to keep the while loop running
            print('Fixation detector running...')
            self.running = True
            while self.running:
                # wait at this point if AOI_Checker is paused
                self.unpaused.wait()
                # wait for the aoi_event to trigger and get name of fixated AOI
                next_aoi = self.fixation_detector.aoi_event.wait(timeout=1.)
                if next_aoi and next_aoi not in self.aoi_fixed:
                    self.aoi_fixed.append(next_aoi)
                    print(colored_text(self.aoi_fixed, 'red'))
                # Make this run method wait again
                self.fixation_detector.aoi_event.clear()

        def set_aoi(self, aoi):
            """
            Set the AOI to be detected.

            :param aoi: A existing AOI
            :type aoi: string
            """
            self.cur_aoi = aoi

        def unpause(self):
            """
            Unpause the AOI_Checker
            """
            if not self.unpaused.is_set():
                self.unpaused.set()

        def pause(self):
            """
            Pause the AOI_Checker
            """
            if self.unpaused.is_set():
                self.unpaused.clear()

        def stop(self):
            """
            Stop a running AOI_Checker
            """
            self.running = False
            self.fixation_detector.aoi_event.set(None)

    def __init__(self, fixation_detector, cur_agt, draw, draw_lock, blinking, trans_matrix, agt_straight,
                 t_gaze_at_obj_ija, t_gaze_straight,  subj_fix_t, t_2_look_straight_again, ja_init_waiting_time,
                 ja_init_aois, trans_dict, p_correct_object, possible_aois, break_trial_if_no_mg=False,
                 single_chance=False, get_attention_parameters=None, show_vid=False, show_vid_always=False,
                 show_points=False, highlight_obj=False, correct_feedback=False, questionnaire=None, log_event=None,
                 finished_event=None, break_event=None, game_event=None, name='IJA_Agent'):
        super(IJA_Agent, self).__init__(cur_agt, draw, draw_lock, blinking, trans_matrix=trans_matrix,
                                        questionnaire=questionnaire, finished_event=finished_event,
                                        break_event=break_event, name=name)
        print('Initializing IJA Agent...')
        # print(subj_fix_t)

        self.fixation_detector = fixation_detector
        if 'no_obj' in cur_agt:
            self.agt_straight = 'straight_no_obj'
        else:
            self.agt_straight = 'straight'
        self.log_event = log_event
        self.trans_dict = trans_dict
        self.t_gaze_straight = t_gaze_straight
        self.t_gaze_at_obj_ija = t_gaze_at_obj_ija
        self.ja_counter = {}
        self.t_2_look_straight_again = t_2_look_straight_again
        self.get_attention_parameters = get_attention_parameters
        # create AOI checker
        self.ja_init_aois = ja_init_aois
        self.ja_init_waiting_time = ja_init_waiting_time  # Max time to wait to establish mg
        self.aoi_checker = self.AOI_Checker(fixation_detector)
        self.gaze_lag = []
        self.game_event = game_event
        if p_correct_object:
            self.p_correct_object = p_correct_object
            self.does_know_correct = True
            self.possible_aois = possible_aois
            self.possible_aois_set = []  # List used for set comparision
            for aoi in possible_aois:
                self.possible_aois_set.append(self.trans_dict[aoi])
            self.possible_aois_set = set(self.possible_aois_set)
        else:
            self.does_know_correct = False
        self.show_points = show_points
        self.show_vid = show_vid[0]
        self.point2view = show_vid[1]
        self.show_vid_always = show_vid_always[0]
        self.trials2view = show_vid_always[1]
        self.point_duration = 1.2  # Duration collected correct objects is shown in [s]
        self.correct_objects = 0
        self.highlight_obj = highlight_obj[0]
        self.HL_time = highlight_obj[1] / 1000.
        self.p_correct_feedback = correct_feedback
        self.show_correct = True
        self.single_chance = single_chance['one_gaze_shift']
        self.stop_trial_if_no_mg = single_chance['stop_trial_if_no_mg']
        print('IJA Agent initialized.')

    def run(self):
        """Start behavioral state
        """

        print('IJA Agent running...')
        self.is_running = True  # Boolean indicating that agent is running
        self.draw.msg4 = None  # Clear draw message
        self.draw.aoi = None

        # Start AOI checker
        self.aoi_checker.start()
        self.aoi_checker.unpause()

        self.log_event.set([libtime.get_time(), 'start'])  # log the start of the current agent run

        # Loop for behavior
        while self.is_running:
            self.paused.wait()  # waits if agent is currently paused

            # Show agent gazing straight
            self.blinking.acquire()
            self.blinking.release()
            self.draw_lock.acquire()
            self.draw.set_micro_state(self.agt_straight, self.agt_straight, time=libtime.get_time())
            self.draw.clear()

            # Wait for mutual gaze (mg, i.e. eye contact)
            t_ja_waiting = self.get_new_waiting_time(self.ja_init_waiting_time)
            mg, t_ja_waiting_start = False, libtime.get_time()
            self.log_event.set([libtime.get_time(), 'starts waiting for eye contact', str(self.ja_init_aois)])
            self.aoi_checker.aoi_fixed = []  # clear found AOIs
            # print(colored_text('waiting for eye contact on '+str(self.ja_init_aois), color='yellow'))
            print('===============================================')
            print('Max time waiting for eye contact ' + str(t_ja_waiting))
            print('Parameters:' + str(self.ja_init_waiting_time))
            print('===============================================')
            # Loop doing the waiting
            while libtime.get_time() < t_ja_waiting + t_ja_waiting_start and not mg:
                # Check if any facial agent AOI has  been fixated
                if any(aoi in self.aoi_checker.aoi_fixed for aoi in self.ja_init_aois):
                    print(colored_text('eye contact established', color='green'))
                    self.log_event.set([libtime.get_time(), 'eye contact established'])
                    mg = True

                    # Show objects, if not present
                    self.cur_agt = self.draw.return_msg2()
                    if '_no_obj' in self.cur_agt:
                        self.cur_agt = self.cur_agt.replace('_no_obj', '')
                        self.blinking.acquire()
                        self.blinking.release()
                        self.draw_lock.acquire()
                        self.draw.set_micro_state(self.cur_agt, self.cur_agt, time=libtime.get_time())
                        self.log_event.set([libtime.get_time(), 'eye_contact_established',
                                            self.trans_dict[self.cur_agt]])
                        self.draw.clear()
                        self.agt_straight = 'straight'  # Make sure objects are shown if the agent looks again

            # If eye contact was established
            if mg:
                # Keep gazing straight
                gaze_straight_time = self.get_new_waiting_time(self.t_gaze_straight)/1000.
                self.break_event.wait(gaze_straight_time)
                print('===============================================')
                print('Gazing straight at HI for before IJA ' + str(gaze_straight_time))
                print('Parameters:' + str(self.t_gaze_straight))
                print('===============================================')

                # Change gaze direction to initiate JA
                self.cur_agt = self.change_micro_state()  # Select a gaze direction
                # Select gaze direaction to draw later
                if self.gaze_down:
                    agt2draw = 'down'
                else:
                    agt2draw = self.cur_agt
                self.aoi_checker.set_aoi(self.trans_dict[self.cur_agt])  # Set correct AOI for aoi checker
                # Draw agent performing gaze shift
                self.blinking.acquire()
                self.blinking.release()
                self.draw_lock.acquire()
                self.draw.set_micro_state(agt2draw, agt2draw, time=libtime.get_time())
                time_start_gaze = libtime.get_time()
                self.log_event.set([time_start_gaze, 'JA_initiated', self.trans_dict[self.cur_agt]])
                self.draw.clear()
                # Get maximal gaze duration at object by agent
                t_max_look = self.get_new_waiting_time(self.t_gaze_at_obj_ija) + libtime.get_time()
                print('===============================================')
                print('Max gaze duration at object ' + str(t_max_look))
                print('parameters:' + str(self.t_gaze_at_obj_ija))
                print('===============================================')

                # Check whether the correct AOI was triggered or time has elapsed
                self.aoi_checker.aoi_fixed = []  # Reset list of fixated AOIs
                break_loop = False  # Boolean to break following loop
                ja, t_looked = False, 0.0  # Boolean indicating whether JA occured, time looked at object by agent

                # Joint attention detection loop
                while t_looked < t_max_look and not break_loop and not self.break_event.is_set():

                    # Check if JA occured
                    if self.trans_dict[self.cur_agt] in self.aoi_checker.aoi_fixed:
                        self.gaze_lag.append([libtime.get_time() - time_start_gaze])
                        if self.log_event:
                            self.log_event.set([libtime.get_time(), 'JA_succsesfull', self.trans_dict[self.cur_agt]])
                        ja, break_loop = True, True
                    else:
                        correct_aoi_fixed = None

                    # Check if any possible AOI was fixated
                    if self.correct_aoi:
                        if len(set(self.aoi_checker.aoi_fixed).intersection(self.possible_aois_set)) > 0:
                            possible_aoi_fixated = True
                            break_loop = True  # Will finish loop
                        else:
                            possible_aoi_fixated = False
                    else:
                        possible_aoi_fixated = False

                    t_looked = libtime.get_time()  # Get time for loop condition

                # If set, check if correct AOI was fixated
                if self.correct_aoi:
                    if self.trans_dict[self.correct_aoi] in self.aoi_checker.aoi_fixed:
                        self.draw.correct_aoi_fixed = True
                    else:
                        self.draw.correct_aoi_fixed = False

                    if self.draw.correct_aoi_fixed:
                        self.game_event.set('correct_object', time=libtime.get_time())  # Increase score

                    if self.show_correct and possible_aoi_fixated:
                        self.get_attention_parameters = False
                        self.is_running = False

                # If set, highlight fixated object
                if self.highlight_obj and self.aoi_checker.aoi_fixed:
                    if self.aoi_checker.aoi_fixed[-1] is not 'AOI_agent_eyes':
                        self.draw.aoi = [self.fixation_detector.aois[self.aoi_checker.aoi_fixed[-1]].pos[0],
                                         self.fixation_detector.aois[self.aoi_checker.aoi_fixed[-1]].pos[1],
                                         self.fixation_detector.aois[self.aoi_checker.aoi_fixed[-1]].size[0],
                                         self.fixation_detector.aois[self.aoi_checker.aoi_fixed[-1]].size[1]]
                        # wait for agent's blink to finish
                        self.blinking.acquire()
                        self.blinking.release()
                        self.draw_lock.acquire()

                        time.sleep(self.HL_time)
                        self.draw.set_micro_state(msg=agt2draw, msg2=agt2draw, msg3=self.draw.aoi,
                                                  msg4=self.draw.correct_aoi_fixed, time=libtime.get_time())
                        time.sleep(self.HL_time)
                        self.draw.clear()
                # If set and no JA occured, agent will try to get attention with rapid gaze shifts
                if not ja and self.get_attention_parameters and not self.gaze_down:
                    for i in range(self.get_attention_parameters['n_attempts']):
                        t_max_get_attention = self.get_new_waiting_time(
                                self.get_attention_parameters['t_max_per_attempt']) + libtime.get_time()
                        for agent_image in self.get_attention_parameters['agent_image_list']:
                            self.draw_lock.acquire()
                            self.draw.set_micro_state(agent_image[0], agent_image[0], time=libtime.get_time())
                            self.log_event.set([libtime.get_time(), 'try_getting_attention', agent_image[0]])
                            self.draw.clear()
                            time.sleep(agent_image[1]/1000.)
                        time.sleep(self.get_new_waiting_time(self.get_attention_parameters['t_show_agent_image'])/1000.)
                        self.draw_lock.acquire()
                        self.draw.set_micro_state(self.cur_agt, self.cur_agt, time=libtime.get_time())
                        self.draw.clear()
                        while not ja and t_looked < t_max_get_attention and not self.break_event.is_set():
                            if self.trans_dict[self.cur_agt] in self.aoi_checker.aoi_fixed:
                                ja = True
                            t_looked = libtime.get_time()
                        if ja:
                            break
                if ja:
                    # Print result
                    print(colored_text(' JA on object successful', 'green') + '\n\tcurrent agent: ' + self.cur_agt +
                          '\n\ttraget: ' + self.trans_dict[self.cur_agt])
                    self.game_event.set('success', time=libtime.get_time())  # Get a point for successful JA
                    if not self.single_chance:
                        gaze_at_obj = self.get_new_waiting_time(self.t_2_look_straight_again)/1000.
                        print('===============================================')
                        print('Keep gazing at object for ' + str(gaze_at_obj))
                        print('parameters:' + str(self.t_2_look_straight_again))
                        print('===============================================')
                        print(gaze_at_obj)
                        self.break_event.wait(gaze_at_obj)
                else:
                    print(encapsulate_text('failure', color='red'))
                    self.game_event.set('failure', time=libtime.get_time())
                    if self.log_event:
                        self.log_event.set([libtime.get_time(), 'JA_failed'])
                if not possible_aoi_fixated and self.single_chance:
                    self.is_running = False
                self.count_ja()
                self.check_if_finished()

            # 2. If no eye contact was established
            else:
                self.log_event.set([libtime.get_time(), 'eye contact failed'])
                if self.stop_trial_if_no_mg:
                    self.is_running = False
                    possible_aoi_fixated = False
                    correct_aoi_fixed = False

# Done with loop ----------------------------------
        self.draw.do_blink = False
        if self.HL_time:
            time.sleep(self.HL_time * 4)
        # reset agent to straight gaze
        if not self.show_vid and not self.show_points:
            self.draw_lock.acquire()
            self.draw.set(self.agt_straight)
            self.draw.clear()
        self.log_event.set([libtime.get_time(), 'stop'])
        self.aoi_checker.stop()
        # If running = false, finish up agent (has to be checked by Bjoern)
        if not self.break_event.is_set():
            self.did_key_press = False
        self.break_event.clear()
        self.finished_event.set()

    def stop(self):
        """
        Stop a running IJA_Agent
        """
        super(IJA_Agent, self).stop()
        self.aoi_checker.stop()

    def count_ja(self):
        """
        Counts number of joint attention instances
        """

        # TODO: Is this still used?
        output = '\n' + 'targets'.ljust(15) + '| trials | ja  | no ja\n'
        targets = self.ja_counter.keys()
        targets.sort()
        for target in targets:
            total = len(self.ja_counter[target])
            correct = 0
            for i in self.ja_counter[target]:
                if i:
                    correct += 1
            output += target.ljust(15) + '|' + str(total).rjust(7) + ' |' + str(correct).rjust(4) + ' |'
            output += str(total - correct).rjust(4) + '\n'
        print(output)


class IJA_Agent_Dict(IJA_Agent):
    """
    A wrapper class to create an IJA_Agent with all parameters inside a dictionary.
    :param parameter: ??
    :type parameter: dictionary
    """

    def __init__(self, parameter):
        super(IJA_Agent_Dict, self).__init__(parameter['fixation_detector'], parameter['cur_agt'],
                                             parameter['draw_event'], parameter['draw_lock'], parameter['blink_event'],
                                             parameter['transition_matrix'], parameter['start_gaze'],
                                             parameter['time_to_bore'], parameter['agent_straight'],
                                             parameter['subject_fixation_time'], parameter['agent_reset_time'],
                                             parameter['ja_init_waiting_time'], parameter['ja_init_aois'],
                                             parameter['translation_dict'], parameter['p_correct_object'],
                                             parameter['possible_aois'], parameter['break_trial_if_no_mg'],
                                             parameter['single_chance'], parameter['get_attention_parameters'],
                                             parameter['show_vid'], parameter['show_vid_always'],
                                             parameter['show_points'], parameter['highlight_obj'],
                                             parameter['correct_feedback'], parameter['questionnaire'],
                                             parameter['log_event'], parameter['finished_event'],
                                             parameter['break_event'], parameter['game_event'])
        self.paused.set()


class BlinkingAgent(Agent):

    """A class to manage agent's behavior: In this mode, the agent will blink with her eyes.
    :param blink_int: Duration in [ms] of average inter-blink interval
    :type blink_int: double
    :param blink_int_var: Variance of above
    :type blink_int_var: double
    :param blink_duration: Duration in [ms] of closed eyes during blinking
    :type blink_duration:  double
    :param blink_dur_var: Variance of above
    """

    def __init__(self, screen_handler, draw, draw_lock, blinking, blink_int, blink_dur, name='BlinkingAgent'):
        super(BlinkingAgent, self).__init__(None, draw, draw_lock, blinking, name=name)

        print('Initializing BlinkingAgent...')
        self.blink_int = blink_int  # Mean and variance for blink interval
        self.blink_dur = blink_dur  # Mean and variance for blink duration
        self.force_finish_event = Event()  # Event to force agent to finish
        print('... BlinkingAgent initialized.')

    def run(self):
        # sets the variable self.is running, which is used to terminate the agent
        self.is_running = True
        while self.is_running:
            print('BlinkingAgent running...')
            # Waits, if the agent is paused
            self.paused.wait()
            # Pauses for an apropriate time between blinks
            self.force_finish_event.wait(self.get_new_waiting_time(self.blink_int)/1000.)

            # Get correct screen name for showing agent with closed eyes
            if 'no_obj' in self.draw.return_msg2():
                self.agent_blink = 'closed_no_obj'
            else:
                self.agent_blink = 'closed'
            # clears the blinking event, signaling that the agent is blinking
            self.blinking.acquire()
            # Draw blinking agent
            if self.draw.do_blink:
                self.draw_lock.acquire()
                print('BLINKS')
                self.draw.set_micro_state(msg=self.agent_blink, msg3=self.draw.aoi, msg4=self.draw.correct_aoi_fixed,
                                          time=libtime.get_time())
                # clears draw event in order to reset it later
                self.draw.clear()
                # pauses for the time a blink takes
            else:
                print('DOESNT BLINK (Should only occur at the end of a trial)!')
            self.force_finish_event.wait(self.get_new_waiting_time(self.blink_dur)/1000.)
            # Redraw agent before blink
            self.draw_lock.acquire()
            self.draw.set_micro_state(msg=self.draw.return_msg2(), msg3=self.draw.aoi,
                                      msg4=self.draw.correct_aoi_fixed, time=libtime.get_time())
            self.draw.clear()  # clears draw event
            self.blinking.release()  # sets blinking event so no agents are blocked
        print('Blinking agent finished.')

    def stop_blinking(self):
        self.is_running = False


class BlinkingAgent_Dict(BlinkingAgent):
    """
    A wrapper class to create a BlinkingAgent with all parameters inside a dictionary.
    :param parameter: ??
    :type parameter: dictionary
    """

    def __init__(self, parameter):
        super(BlinkingAgent_Dict, self).__init__(parameter['screen_handler'], parameter['draw_event'],
                                                 parameter['draw_lock'], parameter['blink_event'],
                                                 parameter['blink_interval'], parameter['blink_duration'],
                                                 parameter['name'])
        self.paused.set()


class PassiveAgent(Agent):
    """
    Explores items regardless of eyetracking data (no interaction), used for pilot study

    :param cur_agt: Current gaze direction of agent (use start gaze direction)
    :type cur_agt: str
    :param draw: Event that fires when display shall be updated to participant
    :type draw: :class:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param draw_lock: Create an event that is fired when screen needs to be updated on the display.
    :type draw_lock: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
    :param blinking: :param blinking: Event to check wheter agent is currently blinking
    :type blinking: :obj:`threading.Event`
    :param trans_matrix: Martix containing transition probabilities amoung microstates
    :type trans_matrix: dictionary
    :param fix_time: ??
    :type fix_time: dictionary
    :param questionnaire: questionnaire to be shown when a button is pressed (if active)
    :type questionnaire: dictionary
    :param finished_event: An event for signaling that time for current macro state is up
    :type finished_event: :obj:`threading.Event`
    :param break_event: Pauses agent
    :type break_event: :obj:`threading.Event`
    :param name: Name for thread of running agent
    :type name: str
    """

    def __init__(self, cur_agt, draw, draw_lock, blinking, trans_matrix, fix_time, questionnaire=None,
                 finished_event=None, break_event=None, show_vid_always=True, show_points=False, name='PassiveAgent'):
        super(PassiveAgent, self).__init__(cur_agt, draw, draw_lock, blinking, trans_matrix=trans_matrix, name=name,
                                           questionnaire=questionnaire, finished_event=finished_event,
                                           break_event=break_event)

        # mean time and variance staying in microstate
        print('Passive agent initialing: ' + self.name)
        self.fix_time = fix_time
        self.cur_agt = 'straight'
        self.show_vid = show_vid_always[0]
        self.trials2view = show_vid_always[1]
        self.show_points = show_points
        print('Passive agent initialized: ' + self.name)

    def run(self):
        self.is_running = True
        print('Passive agent running:' + self.name)
        while self.is_running:
            self.paused.wait()
            self.blinking.acquire()
            self.blinking.release()
            # get a new micro state
            self.cur_agt = self.change_micro_state()
            # draw it
            self.draw_lock.acquire()
            self.draw.set_micro_state(self.cur_agt, self.cur_agt, time=libtime.get_time())
            self.draw.clear()
            # wait for an appropriate amount of time
            self.break_event.wait(self.get_new_waiting_time(self.fix_time[self.cur_agt])/1000.)
            self.check_if_finished()
        # check whether it ended because of time or key press
        if not self.break_event.is_set():
            self.did_key_press = False
        print(self.name + ' done.')
        self.break_event.clear()
        self.finished_event.set()


class Passive_Agent_Dict(PassiveAgent):
    """
    A wrapper class to create a Passive_Agent with all parameters within a dictionary
    :param parameter: ??
    :type parameter: dictionary
    """

    def __init__(self, parameter):
        super(Passive_Agent_Dict, self).__init__(parameter['cur_agt'], parameter['draw_event'], parameter['draw_lock'],
                                                 parameter['blink_event'], parameter['transition_matrix'],
                                                 parameter['fixation_time'], parameter['questionnaire'],
                                                 parameter['finished_event'], parameter['break_event'],
                                                 parameter['show_vid_always'], parameter['show_points'],
                                                 parameter['name'])
        self.paused.set()


class Mixed_Agent(Agent):
    """
    An agent class to combine a set of given agents within one agent run.

    In its basis, it works similar to AgentMacroBehavior, but with its own set
    of agents to cycle through.
    """

    def __init__(self, agent_dict, cur_agt, draw, draw_lock, questionnaire, new_objects, new_objects_event,
                 finished_event, agent_list, name='Mixed_Agent'):
        super(Mixed_Agent, self).__init__(cur_agt, draw, draw_lock, None, questionnaire=questionnaire,
                                          finished_event=finished_event, name=name)

        self.agent_dict = agent_dict
        self.agent_list = agent_list
        self.new_objects = new_objects
        self.new_objects_event = new_objects_event

        self.daemon = True
        self.is_running = True

    def run(self):
        agent_finished_event = Event()
        first_new_objects = True
        # loop through all agents given in agent_list and finish afterwards
        for macro_state in self.agent_list:
            print(encapsulate_text('New macro state: ' + macro_state[0], color='magenta'))
            self.draw_lock.acquire()
            self.draw.set_micro_state(self.cur_agt, self.cur_agt, time=libtime.get_time())
            agent = self.agent_dict[macro_state[0]]['class'](self.agent_dict[macro_state[0]])
            agent.finished_event = agent_finished_event
            agent.change_parameter('run_time', macro_state[1]*1000)
            # if required, get new objects and recreate all screens
            if self.new_objects and not first_new_objects:
                print(encapsulate_text('new objects', color='green'))
                self.draw_lock.acquire()
                self.draw.set_micro_state('__new_screens__', self.cur_agt, time=libtime.get_time())
                self.new_objects_event.wait()
            else:
                print(encapsulate_text('no new_objects', color='red'))
                first_new_objects = False
            agent.change_parameter('time_start', libtime.get_time())
            # start the given agent
            agent.start()
            # wait for it to finish
            agent_finished_event.wait(timeout=macro_state[1]+10)
            agent_finished_event.clear()

        self.finished_event.set()


class Mixed_Agent_Dict(Mixed_Agent):
    """
    A wrapper class to create a Mixed_Agent with it's parameters inside a dictionary.
    """

    def __init__(self, parameter, agent_list):
        super(Mixed_Agent_Dict, self).__init__(parameter['agent_dict'], parameter['cur_agt'], parameter['draw_event'],
                                               parameter['draw_lock'], parameter['questionnaire'],
                                               parameter['new_objects'], parameter['new_objects_event'],
                                               parameter['finished_event'], agent_list, parameter['name'])
