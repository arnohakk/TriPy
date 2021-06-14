# -*- coding: utf-8 -*-

import pygaze
import os
import random
import time
import glob
import pygaze_framework
from stuff import encapsulate_text, colored_text
from pygaze import libscreen, liblog, libtime
from psychopy.visual import RatingScale, TextStim
from threading import Thread


class JAP_ScreenHandler(pygaze_framework.ScreenHandler):

    """
    :param agent_dir:
    :type agent_dir: dictionary (strings)
    :param agent_size: Size of agent in pixels
    :type agent_size: tuple int
    :param agent_pos: Position of agent on screen in pixels from upper left corner
    :type agent_pos: list int
    :param agent_dict: Dict of single gaze directions and corresponding image filenames must be present for desidered
                       gaze directions in a given experiment
    :type agent_dict: Dictionary
    :param tar_size: Target size in pixels
    :type tar_size: tuple int
    :param tar_pos:
    :type tar_pos: dicitonary
    :param stimtracker_parameters: Stimtracker "pixel" location and size in screen in rgb color and pixels units
    :type stimtracker_parameters: dictionary
    :param mucap_parameters: RGB colors indicating muCap events to have double data for screen presentations
                             (seems not to be reliable) (these parameters also need to be adjusted in config file for
                             muCap dict containing RGB color information to trigger mucap)
    :type mucap_parameters: dicitionary
    :param instruction_texts: all instrucution texts according to age group
    :type instruction_texts: dicitonary
    :param object_picker:
    :type object_picker: :obj:`jap_pygaze_framework.ObjectPicker`
    :param dispsize: canvas size in pixel
    :type dispsize: int tuple
    :param start_gaze: initial gaze direction of agent when trial starts
    :type start_gaze: string
    :param trial_types: trial is defined the following way: [agent state, instruction before block
                        (None if set to none), accept button press to end trial, position of correct object]
    :types trial_types:  dictionary
    :param age_group: Definition of HI age groups in years
    :type age_group: dictionary entry
    :param min_instr_read_time: minimum instruction reading time
    :type min_instr_read_time: int
    :param txt_b1:
    :type txt_b1: str
    :param txt_welcome:
    :type txt_welcome: str
    :param target_direct_list:
    :type target_direct_list: string
    :param behavioral_sequence: Sequence of trials with correspoding trial parameters as defined in study file
    :type behavioral_sequence: dicitionary
    :param screennr: screen on which the experiment is being dispalyed on
    :type screennr: int
    :param resize_proportional:
    :type resize_proportional: boolean


    """

    def __init__(self, agent_dir, agent_size, agent_pos, agent_dict, tar_size, tar_pos, stimtracker_parameters,
                 mucap_parameters, instruction_texts, object_picker, dispsize, start_gaze, trial_types, age_group,
                 min_instr_read_time, txt_b1, txt_welcome, target_direct_list, behavioral_sequence, nirs_param,
                 correct_colour=None, point_width=4, aoi_width=5, screennr=0, resize_proportional=True):
        super(JAP_ScreenHandler, self).__init__(stimtracker_parameters, mucap_parameters, instruction_texts,
                                                object_picker, dispsize, nirs_param, screennr=screennr,
                                                resize_proportional=True)
        # dict for screens containing instructions
        self.instruction_scrs = {}
        self.last_agent = None
        self.last_screen = None

        self.agent_dir = agent_dir
        self.agent_size = agent_size
        self.agent_pos = agent_pos
        self.agent_dict = agent_dict

        self.tar_size = tar_size
        self.tar_pos = tar_pos

        self.create_only_screens_created = False
        self.start_gaze = start_gaze
        self.trial_types = trial_types  # JAP_TRIAL_TYPES as defined in studies/*setup_file*.py
        self.target_direct_list = target_direct_list

        self.age_group = age_group
        self.min_instr_read_time = min_instr_read_time
        self.txt_b1 = txt_b1
        self.txt_welcome = txt_welcome

        self.behavioral_sequence = behavioral_sequence
        self.draw_col = correct_colour

        self.color = {}
        self.color[True] = correct_colour[0]
        self.color[False] = correct_colour[1]

        self.point_width = point_width
        self.aoi_width = aoi_width

        if self.trial_types:
            self.rand_obj = False  # disables random objects to use trial types instead
        else:
            self.rand_obj = True

    def draw_agent_on_target_screen(self, agent, tracker=None, force_stim_signal=False, score=None, aoi=None,
                                    correct=None):
        """ Function to draw current agent on screen

        :param agent: Name of gaze direction to be drawn
        :type agent: str
        :param tracker: The eyetracker used in the experiment to draw a gaze curser
        :type tracker: :class:`OurTracker`
        :param force_stim_signal:
        :type force_stim_signal: Boolean
        :param score: Score to be drawn on screen
        :type score: int
        :param aoi: AOI to be drawn on screen
        :type aoi: list
        :param correct: Indicating whether correct stimuli was chosen to select correct highlight color
        :type correct: Boolean

        """
        temp_screen = libscreen.Screen()

        try:
            if self.stimtracker_black:
                temp_screen.copy(self.screens[agent]['black'])
            else:
                temp_screen.copy(self.screens[agent]['white'])
        except KeyError as error:
            print(colored_text(agent, 'red'))
            print(agent)
            print(self.screens.keys())
            print(error.args)
        self.last_screen = libscreen.Screen()
        self.last_screen.copy(temp_screen)

        # If set, add fixation cross, score, or aoi highlight to screen
        if tracker or score or aoi:
            if tracker:
                temp_screen.draw_fixation('cross', 'green', tracker.sample())
            if score or score == 0:
                temp_screen.draw_text(score, pos=(1800, 1000), fontsize=32)
            if aoi is not None:
                temp_screen.draw_rect('yellow', aoi[0], aoi[1], aoi[2], aoi[3], self.aoi_width)
            if correct is not None:
                temp_screen.draw_rect(self.color[correct], aoi[0], aoi[1], aoi[2], aoi[3], self.aoi_width)

        # Update display and get update time
        self.display.fill(temp_screen)
        self.display.show()
        draw_time = libtime.get_time()

        # Set correct values for stimtracker signal
        if self.last_agent != agent or force_stim_signal:
            self.stimtracker_black = not self.stimtracker_black
            self.last_agent = agent

        return draw_time

    def make_all_screens(self, target_list, trials2draw, fixation_detector=None, aoi_tol=None, draw_aois=False):
        """Method to create all possible screens that could be shown in a\
                single block of an experiment

        :param target_list: list of targets to be shown
        :type target_list: list
        :param trials2draw: list of trials for which actually screens shall be created
        :type trials2draw: list
        :param fixation_detector:
        :type fixation_detector: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
        :param aoi_tol: Additional size of AOI in pixels added to image size
        :type aoi_tol: list int
        :param draw_aois:
        :type draw_aois: Boolean

        """
        if not self.create_only_screens_created:
            self.make_agent_only_screens()
            self.make_point_screens_cricles()
            self.create_only_screens_created = True

        self.make_agent_screens_with_objects(target_list, trials2draw, fixation_detector=fixation_detector,
                                             aoi_tol=aoi_tol, draw_aois=draw_aois)
        self.make_instruction_screens()

    def make_agent_screens_with_objects(self, target_dict, trials2draw, fixation_detector=None, aoi_tol=None,
                                        draw_aois=False, aoi_border_size=1):
        """ Method to create all screens with objects an all possbile gaze directions of virtual character
        :param target_dict:
        :type target_dict: list
        :param fixation_detector:
        :type fixation_detector: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
        :param aoi_tol: Additional size of AOI in pixels added to image size
        :type aoi_tol: list int
        :param draw_aois:
        :type draw_aois: Boolean
        :param aoi_border_size: defines the line width of the aoi borders
        :type aoi_border_size: int

        """
        # create new screen
        target_screen = libscreen.Screen()
        aois = {}

        # Use random objects ...
        if self.rand_obj:
            for target, file_name in target_dict.items():
                # draw targets on screen
                self.store_image(target, file_name, self.tar_pos[target],
                                 self.tar_size)
                self.draw_image(target_screen, target)
                aois[target] = {'pos': tuple(self.images_stored[target].position),
                                'size': self.images_stored[target].size,
                                'tol': aoi_tol}
                self.draw_agent_on_object_screens(aois, target_screen, fixation_detector, draw_aois, aoi_border_size)

        # ... or use predefined trial types
        else:
            # Loop over JAP_TRIAL_TYPES:
            # draw objects and correct postions
            self.screens_dict = {}

            for trial_type, value in self.trial_types.iteritems():
                if trial_type in trials2draw:
                    for key, value in value.iteritems():
                        if key.startswith('object'):
                            o_file = os.path.join(self.target_direct_list[0], value)
                            pos = key.replace('object_', '')
                            pos = ''.join(i for i in pos if not i.isdigit())
                            self.store_image(key, o_file, self.tar_pos[pos], self.tar_size)
                            self.draw_image(target_screen, key)
                            aois[pos] = {'pos': tuple(self.images_stored[key].position),
                                         'size': self.images_stored[key].size,
                                         'tol': aoi_tol}
                            self.draw_agent_on_object_screens(aois, target_screen, fixation_detector, draw_aois,
                                                              aoi_border_size)
                            self.screens_dict[trial_type] = dict(self.screens)
            init_screen = self.behavioral_sequence[0]['trial_type']
            self.screens = self.screens_dict[init_screen]

    def draw_agent_on_object_screens(self, aois, target_screen, fixation_detector=None, draw_aois=False,
                                     aoi_border_size=1):

        """ Method to create screens with all gaze directions of agent with objects
        :param aois:
        :type aois: list
        :param target_screen:
        :type target_screen:
        :param fixation_detector:
        :type fixation_detector: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
        :param draw_aois:
        :type draw_aois: Boolean
        :param aoi_border_size: defines the line width of the aoi borders
        :type aoi_border_size: int

        """
        # Create one screen for every possbile gaze direction and stimtracker signal
        for agent, image in self.agent_dict.items():
            screen = libscreen.Screen()
            screen.copy(target_screen)
            # self.store_image(agent, os.path.join(self.agent_dir, image), self.agent_pos, self.agent_size)
            agent_img = 'agt_' + agent
            self.draw_image(screen, agent_img)
            # Add AOIs for fixation detector
            if fixation_detector:
                fixation_detector.add_multiple_aois(aois)
                if draw_aois:
                    fixation_detector.draw_aois(screen, aoi_border_size)
            self.make_mucap_trigger_pixel(screen, agent)
            self.screens[agent] = {}
            self.screens[agent]['white'] = screen
            self.copy_screen_w_stimtracker_pixel(self.screens[agent])
            self.check_start_gaze(agent, screen)

    def make_agent_only_screens(self):
        """ Method to create screens with all gaze directions without any objects and StimTracker pixel
        """

        for agent, image in self.agent_dict.items():
            screen = libscreen.Screen()
            agent_img = 'agt_' + agent
            self.store_image(agent_img, os.path.join(self.agent_dir, image), self.agent_pos, self.agent_size)
            self.draw_image(screen, agent_img)
            agt = agent + '_no_obj'
            self.screens[agt] = {}
            self.screens[agt]['white'] = screen
            self.copy_screen_w_stimtracker_pixel(self.screens[agt])
            self.check_start_gaze(agt, screen)

    def check_start_gaze(self, agent, screen):
        """ Check whether current screen is also used for startgaze and if so, create startgaze screen from it, used to
        create a clear stimtrack pattern at the beginning of each trial

        :param agent:
        :type agent:
        :param screen:
        :type screen:
        """
        if agent == self.start_gaze:
            self.screens['startgaze'] = {}
            start_screen = libscreen.Screen()
            start_screen.copy(screen)
            self.make_mucap_trigger_pixel(start_screen, 'block_start')
            self.screens['startgaze']['white'] = start_screen
            self.copy_screen_w_stimtracker_pixel(self.screens['startgaze'])

    def make_point_screens_cricles(self):
        """ Method to create screens for showing point progress as circles
        """
        for j, colour in enumerate(self.draw_col):
            for i in range(4):
                screen_name = 'points_' + str(i)
                if j == 1:
                    screen_name = screen_name + '_wrong'
                if j == 0:
                    screen_name = screen_name + '_correct'
                fill = False
                screen = libscreen.Screen()
                if i > 2:
                    fill = True
                screen.draw_circle(pos=((2./3.) * self.dispsize[0], 0.5 * self.dispsize[1]),
                                   pw=self.point_width, fill=fill, colour=colour)
                if i > 1:
                    fill = True
                screen.draw_circle(pos=(0.5 * self.dispsize[0], 0.5 * self.dispsize[1]), pw=self.point_width,
                                   fill=fill, colour=colour)
                if i > 0:
                    fill = True
                screen.draw_circle(pos=((1./3.) * self.dispsize[0], 0.5 * self.dispsize[1]),
                                   pw=self.point_width, fill=fill, colour=colour)

                self.screens[screen_name] = {}
                self.screens[screen_name]['white'] = screen
                self.copy_screen_w_stimtracker_pixel(self.screens[screen_name])

    def present_instruction_screen(self, text, screen_count):  # different name, too similar to make_instructon_screens
        """ Method to make and draw screen with instrucions
        :param text:
        :type text: str
        :param screen_count:
        :type screen_count: int
        """
        draw_time = self.make_and_draw_screen(self.txt_b1[self.age_group][text])
        screen_count += 1
        libtime.pause(self.min_instr_read_time)
        return screen_count, draw_time

    def make_instruction_screens(self):
        """ Create all non-agent screens
        """
        for name, text in self.instruction_texts.iteritems():
            self.instruction_scrs[name] = {}
            self.instruction_scrs[name]['white'] = libscreen.Screen()
            self.instruction_scrs[name]['black'] = libscreen.Screen()
            if name == 'finished':
                self.make_mucap_trigger_pixel(self.instruction_scrs[name]['white'], 'stop_rec')
            elif name == 'end_block' or 'end_paradigm':
                self.make_mucap_trigger_pixel(self.instruction_scrs[name]['white'], 'quit_rec')

            self.draw_text(text, self.instruction_scrs[name]['white'])
            self.copy_screen_w_stimtracker_pixel(self.instruction_scrs[name])

    def show_instructions(self, name):
        """Method to show instructions to participant
        :param name: Name of screen to be shown
        :type name: str
        """
        return self.show_a_screen(self.instruction_scrs[name])

    def make_agent_selection_screen(self, directory, age_selection, text):
        """Method to create a screen showing agent's and asking participant to pick one
        :param directory: path to selected agent images
        :type directory: string
        :param age_selection: age group
        :type age_selection: list element
        :param text: instruction text corresponding to age group
        :type text: dictionary
        """
        # Create empty screens
        self.agt_select_screen = {}
        self.agt_select_screen['white'] = libscreen.Screen()
        # Draw instructions on screen
        self.agt_select_screen['white'].draw_text(text=text,
                                                  pos=(900, 900), center=True, font='mono',
                                                  fontsize=32)
        # Get all images to draw
        agt_imgs = glob.glob(os.path.join(directory, age_selection, "*.png"))
        # First image's postion
        img_pos = self.dispsize[0]/len(agt_imgs)
        # Draw images on screen
        img_counter = 0
        for img in agt_imgs:
            self.agt_select_screen['white'].draw_image(img, pos=(300+img_pos*img_counter,
                                                       self.dispsize[1]/2), scale=0.5)
            img_counter += 1
        self.copy_screen_w_stimtracker_pixel(self.agt_select_screen)
        return agt_imgs

    def change_screen_for_trial(self, trial_type):
        """ Method to set different screen according to the trial type
        :param trial_type: Initial gaze direction of agent when trial starts
        :type trial_type: string
        """
        self.screens = self.screens_dict[trial_type]

    def show_agent_selection_screen(self):
        """Method to show screen with agent selection to participant
        """
        return self.show_a_screen(self.agt_select_screen)

    # {{{
    # def show_updated_avatar(self, clear=False, draw_all=False, tracker=None):
    #     """A new :py:func:`show` function, which I need to fully understand to
    #     write a documentation.

    #     :param clear: clear the screen after moving it to the display. By\
    #                     default True.
    #     :type clear: bool
    #     :param draw_all: draw the screen with all the objects to be drawn\
    #                     always. By default False.
    #     :type draw_all: bool
    #     :param tracker: An :py:class:`OurTracker` object. If given the current\
    #                     gaze position will be drawn. By default None.
    #     :type tracker: OurTracker
    #     """
    #     if tracker:
    #         self.screen.draw_fixation(colour='green', pos=tracker.sample())

    #     self.display.fill(self.screen_2_draw)
    #     self.display.show()
    # }}}

    def show_agent_rating(self, agents, questions, logger=None, low=1, high=9, marker_start=0,
                          scale=' = sehr . . . gar nicht = ', only_mouse=False, use_mouse=False):
        """ Method to
        :param agents: list containg strings for corresponding agents to be rated
        :type agents: dictionary entry (strings)
        :param questions:
        :type questions: list (strings)
        :param logger:
        :type logger: dicitonary
        :param low:
        :type low: int
        :param high:
        :type high: int
        :param marker_start:
        :type marker_start: int
        :param scale:
        :type scale: string
        :param only_mouse_:
        :type only_mouse: bool
        :param use_mouse:
        :type use_mouse: bool
        """

        print(encapsulate_text('PRESENTING AGENT_RATING', color='magenta', background='cyan'))

        random.shuffle(agents)  # Assign agents to a random position

        # Creaate and present agents
        empty_screen = libscreen.Screen()
        for agent in agents:
            agent_image = self.Image(agent, size=(self.display.dispsize[0], self.display.dispsize[1]/2),
                                     position=(self.display.dispsize[0]/2, self.display.dispsize[1]/3))
            agent_screen = libscreen.Screen()
            agent_screen.draw_image(agent_image.image, agent_image.position)
            for question in questions:
                agent_rating_screen = libscreen.Screen()
                agent_rating_screen.copy(agent_screen)
                ratingscale = RatingScale(pygaze.expdisplay, low=low, high=high, markerStart=marker_start,
                                          scale=str(low)+scale+str(high), mouseOnly=only_mouse, noMouse=not use_mouse,
                                          textColor='black', pos=(0, -1*self.display.dispsize[1]/3))
                agent_rating_screen.screen.append(ratingscale)
                text_stim = TextStim(pygaze.expdisplay, question, pos=(0, -1*self.display.dispsize[1]/6),
                                     color='black', height=40, wrapWidth=1500)
                agent_rating_screen.screen.append(text_stim)
                self.display.fill(agent_rating_screen)
                self.display.show()
                while ratingscale.noResponse:
                    self.display.fill(agent_rating_screen)
                    self.display.show()
                if logger:
                    logger.set([agent, question, ratingscale.getHistory()])
                if questions.index(question) < len(questions) - 1:
                    self.display.fill(agent_screen)
                    self.display.show()
                    time.sleep(0.5)
            self.display.fill(empty_screen)
            self.display.show()
            time.sleep(0.5)


class JAP_LogManager(pygaze_framework.LogManager):

    class PostExperimentLogger:
        """ A class to log variables to a file, used for almost all data logging
        :param variable:
        :type variable:
        :param log_dir:
        :type log_dir:
        :param code:
        :type code:
        :param name:
        :type name: string
        """

        def __init__(self, variable, log_dir, code, name='some_variable'):
            self.variable = variable
            self.log_name = os.path.join(log_dir, code + '_' + name)
            self.log = liblog.Logfile(filename=self.log_name)
            # self.log.write(['Time', 'Screen'])
            print('PostExperimentLogger ' + name + ' initialized...')

        def save_variable_to_txt_file(self):
            for entry in self.variable:
                self.log.write(entry)

        def save_variable_to_txt_file(self):
            for entry in self.variable:
                self.log.write(entry)
            self.variable = []

    def __init__(self, data_dir, block_name=None, tracker=None, participant_data=None, age_group=None, verbose=False,
                 mucap_dir=None, mucap_marker=None, mucap_wmv=None, fixation_data=None, log_dict={}, screenshots=False,
                 tobii_save_event=None):
        super(JAP_LogManager, self).__init__(data_dir, block_name, tracker, participant_data, age_group, verbose,
                                             mucap_dir, mucap_marker, mucap_wmv, fixation_data, log_dict, screenshots,
                                             tobii_save_event=tobii_save_event)

    def log_variable(self, variable, name):
        setattr(self, name, self.PostExperimentLogger(variable, self.data_dir, self.data['code'],
                                                      name=name))


class ObjectPicker():
    """
    A class to (randonly) choose the objects to be shown during the experiment.

    :param tar_names: names of the targets for the screen
    :type tar_names: list
    :param object_dir_list: a list of folders, where the objects can be found
    :type object_dit_list: list
    """

    def __init__(self, tar_names, object_dir_list):
        self.tar_names = tar_names
        self.object_dir_list = object_dir_list

        self.last_pick_list = None

    def get_new_targets(self):
        """
        Get a dictionary of new objects for the creation of the screens.
        :returns: a dict of the new objects
        """
        new_pick = {}
        while True:
            object_dir = random.choice(self.object_dir_list)
            object_list = os.listdir(object_dir)
            new_pick_list = random.sample(object_list, len(self.tar_names))
            if not new_pick_list == self.last_pick_list:
                self.last_pick_list = new_pick_list
                for i, v in enumerate(new_pick_list):
                    new_pick[self.tar_names[i]] = os.path.join(object_dir, v)
                break
        return new_pick


class GameHub(Thread):
    """A class to gamify the experiment. Used to keep track of different kind of scores
       :param on_success: points gained when chosen correct
       :type on_success: int
       :param on_failure: points gained/substracted when chosen wrong
       :type on_failure: int
       :param on_later_success:
       :type on_later_success: int
       :param log_event:
       :type log_event: :obj:`msrresearch_helpers.pygaze_framework.MyEvent`
       :param name:
       :type name: string
    """

    def __init__(self, on_success=3, on_failure=-1, on_later_success=1, log_event=None, name='Game_Hub'):
        super(GameHub, self).__init__(name=name)
        print('Initializing GameHub...')
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_later_success = on_later_success
        self.log_event = log_event

        self.score = 0

        self.event = pygaze_framework.MyEvent()
        self.is_running = False
        self.daemon = True
        self.name = name
        self.score_correct_objects = 0
        self.correct_object_this_trial = None
        self.trials = 0
        print('GameHub initialized')

    def run(self):

        self.is_running = True
        while(self.is_running):

            result = self.event.wait(timeout=2.)

            if result:
                if result == 'success':
                    self.score += self.on_success
                elif result == 'failure':
                    self.score += self.on_failure
                elif result == 'later_success':
                    self.score += self.on_later_success
                elif result == 'correct_object':
                    self.score_correct_objects += 1
                elif result == 'correct_object_this_trial':
                    self.correct_object_this_trial = True
                elif result == 'wrong_object_this_trial':
                    self.correct_object_this_trial = False
                elif result == 'trial_done':
                    self.trials += 1
                elif result == 'dummy':
                    pass
                else:
                    raise LookupError(result + ' not defined!')

                if self.log_event:
                    self.log_event.set([self.event.time, self.score])
                print(encapsulate_text('current score {}'.format(self.score),
                                       color='blue', background='yellow'))

    def stop(self):
        self.is_running = False
