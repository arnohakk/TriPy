from pygaze import eyetracker, libscreen, libtime, liblog, libinput, libgazecon
import tobii_research as tr
import PIL
from psychopy import iohub
from psychopy.visual import RatingScale, TextStim, MovieStim3
from threading import Thread, Event, Lock
import shutil
import os
import json
import cPickle as pickle
import sys
import traceback
import time
from .stuff import colored_text, encapsulate_text
import ctypes
import pprint
import random
import time
import copy

# try:
#     import msvcrt
# except ImportError:
#     raise NotImplementedError('Keyboard input for non Wnidows systems is not yet implemented!')


class MyEvent:
    """An extension of :class:`threading.Event` with the possibility to
    pass information from the thread setting the event to all threads
    waiting for the event to be raised.

    .. seealso:: :class:`threading.Event`
    """

    def __init__(self):
        self.event = Event()
        self.msg = None
        self.msg2 = None
        self.msg3 = None
        self.msg4 = None
        self.time = None

        self.do_blink = True  # Actually blink
        self.do_HL = False  # Highlight object while blinking
        self.aoi = None  # According AOI to draw
        self.correct_aoi_fixed = None

    def is_set(self):
        """Returns ``True`` if and only if the inner flag of the Event
        object is True."""
        return self.event.is_set()

    def clear(self):
        """Resets the inner flag to ``False``
        """
        self.event.clear()
        self.name = None
        # self.time = None

    def set(self, msg=None, time=None):
        """Sets the internal flag to ``True`` and lets the threads waiting
        resume.

        :param msg: Anything, which should be given to all waiting threads
        :type msg: object
        :param time: A second message, intended for a time.
        :type time: object
        """
        if msg:
            self.msg = msg
            # print('Message send:' + str(msg))
        if time:
            self.time = time
        self.event.set()

    def set_micro_state(self, msg=None, msg2=None, msg3=None, msg4=None, time=None):
        """Sets the internal flag to ``True`` and lets the threads waiting
        resume.

        :param msg: Anything, which should be given to all waiting threads
        :type msg: object
        :param msg2: A second object to be stored in MyEvent
        :type msg2: object
        :param time: A third object to be stored in MyEvent. Intended for a time
        :type time: object
        """
        self.msg = msg
        if msg2:
            self.msg2 = msg2
        if msg3:
            self.msg3 = msg3
        if msg4 is not None:
            self.msg4 = msg4
        if time:
            self.time = time
        self.event.set()
        # print('Message set: '+ self.msg)

    def wait(self, timeout=None):
        """Halts the calling thread until :func:`set` is called. Returns
        whatever :func:`set` is given. If nothing is given to :func:`set`,
        ``None`` will be returned.
        """
        self.event.wait(timeout)
        # print('Message returned from Event: '+ self.msg)
        msg = self.msg
        self.msg = None
        return msg

    def return_msg(self):
        return self.msg

    def return_msg2(self):
        return self.msg2


class EventHandler(Thread):
    """This class shall be used to detect button press and gaze events etc.

    :param keylist: keys that can be pressed
    :type keylist: str
    :param time: in [ms]
    :type time: float
    :param name: Name for thread
    :type name: str
    """

    class Fixation_Detector(Thread):
        """An object to detect fixations and check whether this is any any defined AOIs.

        :param tracker: Eyetracker used for fixation detection
        :type tracker: pygaze_framework.OurTracker object
        :param aoi_tol: NOT FUNCTIONAL
        :type aoi_tol: int
        :param name: Name for thread
        :type name: str
        """

        def __init__(self, tracker, log_event=None, aoi_tol=0, name='Fixation_Detector'):
            super(EventHandler.Fixation_Detector, self).__init__(name=name)
            self.tracker = tracker  # tracker object
            self.log_event = log_event  # log event
            self.num_aoi = 0  # counter for keeping track for number of AOIs
            self.aois = {}  # dict for AOIs
            self.aoi_event = MyEvent()  # event that is fired if fixation occured in relevant AOI
            self.daemon = True
            self.is_running = False
            self.aoi_tol = aoi_tol  # Not implemented
            # List of all fixations: time, pixel, object
            self.fixation_list = []

        def stop(self):
            self.is_running = False

        def run(self):
            """ Method to run the fixation detector

            """
            self.is_running = True
            num_aoi = len(self.aois)
            while self.is_running:
                found_aoi = False

                # Wait for a fixation to occur
                try:
                    fix_time, fix_pos = self.tracker.wait_for_fixation_start()
                except IndexError:
                    print('Cannot wait for a fixation to start')
                    print(encapsulate_text(str(libtime.get_time()), color='red', background='yellow'))
                    print(colored_text(traceback.format_exc(), color='red'))
                self.counter = 0

                # Go through all AOIs and check whether given fixation is within them
                # TOCHECK
                for name, aoi in self.aois.iteritems():
                    self.counter += 1
                    # if fixation is within the AOI, log it and append fixation to fixation_list
                    if aoi.contains(fix_pos):
                        self.aoi_event.set(name)
                        found_aoi = True
                        self.fixation_list.append([fix_time, fix_pos, name])
                        if self.log_event:
                            self.log_event.set([fix_time, fix_pos, name])
                        # print(colored_text('Fixation detected at ' + name, 'blue'))
                # if fixation was in no AOI, log it accordingly
                if not found_aoi and self.log_event:
                    self.log_event.set([fix_time, fix_pos, None])

        def add_aoi(self, pos, size, name, aoi_tol=None, aoi_type='rectangle'):
            """ Method to add AOI that will be checked fixation inside happened when fixation detector
            once has started
            """
            self.num_aoi += 1
            if aoi_tol:
                self.aois[name] = libgazecon.AOI(aoi_type,
                                                 (pos[0]-(int(size[0]/2)+aoi_tol[0]),
                                                  pos[1]-(int(size[1]/2)+aoi_tol[1])),
                                                 (size[0]+2*aoi_tol[0], size[1]+2*aoi_tol[1]))
            else:
                self.aois[name] = libgazecon.AOI(aoi_type, (pos[0]-int(size[0]/2), pos[1]-int(size[1]/2)), size)

        def add_multiple_aois(self, *aoi_dicts):
            """
            Add multiple AOIs at once.
            """
            for aoi_dict in aoi_dicts:
                for name, aoi_data in aoi_dict.items():
                    self.add_aoi(aoi_data['pos'], aoi_data['size'], name, aoi_data['tol'])

        def draw_aois(self, screen, border_size=5):
            """
            Draw rectangles around the all saved AOIs.

            This is a function primarily used for development.
            """
            for name, aoi in self.aois.items():
                screen.draw_rect('yellow', aoi.pos[0], aoi.pos[1], aoi.size[0], aoi.size[1], border_size)

    class BlinkDetector(Thread):
        """A class to detect blinks NOT FUNCTIONAL

        :param tracker: Eyetracker to detect blinks
        :type tracker: pygaze_framework.OurTracker object
        """

        def __init__(self, tracker, name='BlinkDetector'):
            super(EventHandler.BlinkDetector, self).__init__(name=name)
            # tracker object
            self.tracker = tracker
            self.is_running = False

        def run(self):
            self.is_running = True
            while self.is_running:
                blink_start = self.tracker.wait_for_blink_start()
                blink_end = self.tracker.wait_for_blink_end()
                print blink_end - blink_start

        def stop(self):
            self.is_running = False

    # TOCHECK
    class JA_Detector(Thread):
        """A class to detect joint attention by agent and participant NOT FUNCTIONAL

        :param tracker: Eyetracker to detect blinks
        :type tracker: pygaze_framework.OurTracker object
        """

        def __init__(self, tracker, name='JADetector'):
            super(EventHandler.JA_Detector, self).__init__(name=name)
            self.tracker = tracker
            self.is_running = False

        def run(self):
            self.is_running = True
            while self.is_running:
                pass

        def stop(self):
            self.is_running = False

    # TOCHECK
    class KeyInputHandler(Thread):
        """DOES NOT WORK, DON'T BOTHER TO USE IT!"""

        def __init__(self, keylist=None, name='KeyInputHandler'):
            super(EventHandler.KeyInputHandler, self).__init__(name=name)

            self.keylist = keylist

            self.keyboard = libinput.Keyboard()
            self.keyboard.set_timeout(500)
            self.daemon = True
            self.is_running = False

        def run(self):
            self.is_running = True
            while self.is_running:
                print(encapsulate_text('test', color='blue', background='yellow'))
                # char = msvcrt.getwch()
                char = self.keyboard.get_key()
                if char:
                    print(encapsulate_text('PRESSED '+char, color='red'))

    def __init__(self, keylist=[], time=500, name='EventHandler'):
        super(EventHandler, self).__init__(name=name)

        self.daemon = True
        self.is_running = False

        # Create empty dicts to be filled
        self.event_press_dic = {}
        self.event_release_dic = {}
        self.fixation_detector_dic = {}
        self.aoi_event = None

        # Initialize PsychoPy's ioHub, add a keyboard und keylist
        self.io = iohub.launchHubServer()
        self.keyboard = self.io.devices.keyboard
        self.keylist = keylist

        self.create_events(keylist)
        self.event_pressed = Event()
        self.event_released = Event()

        self.time = time

    def start(self, keylist=None, time=None):
        if time:
            self.time = time
        if keylist:
            self.set_keylist(keylist)
        super(EventHandler, self).start()

    def stop(self):
        for fixation_detector in self.fixation_detector_dic.values():
            fixation_detector.stop()
        self.is_running = False

    def run(self):
        self.is_running = True
        while self.is_running:
            keyboard_events = self.keyboard.getKeys()
            for event in keyboard_events:
                if event.type == 'KEYBOARD_PRESS':
                    self.event_pressed.set()
                    self.score_event(event, self.event_press_dic)
                else:
                    self.event_released.set()
                    self.score_event(event, self.event_release_dic)
            libtime.pause(self.time)

    def create_events(self, keylist):
        """Create events for buttons presses

        :param keylist:
        :type keylist:
        """
        if type(keylist) is str:
            self.event_press_dic[keylist] = Event()
            self.event_release_dic[keylist] = Event()
        elif type(keylist) is list:
            for key in keylist:
                self.event_press_dic[key] = Event()
                self.event_release_dic[key] = Event()

    def score_event(self, event, event_dic):
        if event.char == '\n' and 'return' in event_dic:
            event_dic['return'].set()
        elif event.char == ' ' and 'space' in event_dic:
            event_dic['space'].set()
        elif event.char in event_dic:
            event_dic[event.char].set()

    def reset_key_events(self):
        self.event_pressed.clear()
        self.event_released.clear()
        for event in self.event_press_dic.values():
            event.clear()
        for event in self.event_release_dic.values():
            event.clear()

    def set_keylist(self, keylist):
        self.event_press_dic = {}
        self.event_release_dic = {}
        self.create_events(keylist)

    def wait_for_either_key(self, keylist):
        """A function to wait for one of a given list of keys to be pressed.

        .. todo:: :py:func:`wait_for_either_key` rewrite this function to work\
                        with :py:class:`MyEvent`
        """
        keylist_backup = self.keylist
        self.set_keylist(keylist)
        while True:
            self.event_pressed.wait()
            for key, event in self.event_press_dic.iteritems():
                if event.isSet():
                    self.set_keylist(keylist_backup)
                    self.reset_key_events()
                    return key

    def create_aoi_from_image(self, fixation_detector, name, image, aoitype='rectangle'):
        """Method to create AOI for Fixation_Detector object for image

        :param fixation_detector: Fixation detector that will check for this AOI
        :type fixation_detector:
        :param name: Name of AOI
        :type name: str
        :param image: Image for which AOI is added
        :type name:
        """
        fixation_detector.add_aoi(image.position, image.size, name, aoi_type=aoitype)

    def create_aoi_from_coordinates(self, fixation_detector, name, position, size, aoi_type='rectangle'):
        """Method to create AOI and Fixation_Detector from given coordinates

        :param fixation_detector: Fixation detector that will check for this AOI
        :type fixation_detector:
        :param name: Name of AOI
        :type name: str
        :param position: The Position of the upper left corner of the AOI
        :type position: tuple
        :param size: Size of the AOI
        :type size: tuple
        :param aoi_type: Type of the AOI
        :type aoi_type: str
        """
        fixation_detector.add_aoi(position, size, name=name)


class ScreenHandler(object):

    """This class should be used to handle all screen related issues.

    :param agent_dir: directory where all images of agent are located
    :type agent_dir: use os.path.join method
    :param agent_size: Size of agent in pixels
    :type agent_size: list
    :param agent_pos: Postion of agent on screen
    :type agent_pos: tuple
    :param agent_dict: A dictionary containing translation from names used in\
                       this framework and the filenames of the images of the\
                       agent
    :type agent_dict: dict
    :param tar_dir: directory containing all objects which will be presented\
                    on the screen
    :type tar_dir: use os.path.join method
    :param tar_size: Size of targets in pixels
    :type tar_size: tuple
    :param tar_pos:
    :param stimtracker_parameters: Parameter for Stimtracker support: Whenever screen is changed,
                        a pixel will change color that can be registered by stimtracker device
    :param mucap_parameters:: will add mucap pixels  to correspoding screens to start video
                        recording automatically and get time stamps for events
    :param instruction_texts:
    :param object_picker: Class delivering names of objects to be shown on the screen
    :param resize_proportional: KP
    :type resize_proportional: boolean

    """

    class Movie:
        """A class to prepare and show video clips.

        In order to display videos as easily as possible, this class
        sets up the necessary screen(s) and defines the duration of the video that
        is to be displayed.

        :param file_name: The filename of the video clip (tested for .mp4 files)
        :type filename: str
        :param win: The handle to the active PsychoPy Window instance
        :type win: Psychopy Display
        """

        def __init__(self, file_name, win, disp, rewind_vid=True, playtime=1000):
            # Prepare video and add it to PsychoPy screens
            self.mov = MovieStim3(win, file_name, flipVert=False, noAudio=True)
            # self.mov.autoDraw = False
            self.rewind_vid = rewind_vid
            self.display = disp
            self.play_uniform = True
            self.played_time = 0.
            if self.rewind_vid:
                self.play_time = (self.mov.duration * 1000)
            else:
                if len(playtime) == 1:
                    self.play_time = playtime * 1000  # Convert to [ms]
                else:
                    self.play_times = [i * 1000 for i in playtime]  # Convert to [ms]
                    self.play_counter = 0
                    self.play_uniform = False
            if os.path.exists('video.pickle'):
                self.load_video_progress()
            else:
                print('Start video from beginning')

        def play_video(self):
            """ Method to play video

            """

            if not self.play_uniform:
                self.play_time = self.play_times[self.play_counter]
                self.play_counter += 1
            t1 = libtime.get_time()
            t0 = t1
            self.mov.play()
            while t1-t0 < self.play_time:
                self.mov.draw()
                t1 = self.display.show()
            self.mov.pause()
            self.played_time += t1 - t0

            if self.rewind_vid:  # Rewind vid and clear last frame
                self.mov.seek(0.)
                self.mov.play()
                self.mov.draw()
                self.mov.pause()
                
            return t0, t1

        def save_video_progess(self):
            with open('video.pickle', 'w+') as save_file:
                time_played = sum(self.play_times[:self.play_counter])/1000.
                print(encapsulate_text(str('VIDEO SAVED AT:' + str(time_played) + 'counter: ' +
                                       str(self.play_counter)), color='red'))
                print(encapsulate_text(str('VIDEO Played for:' + str(self.played_time)), color='red'))
                pickle.dump({'video_index': self.play_counter}, save_file)

        def load_video_progress(self):
            with open('video.pickle', 'r') as save_file:
                saved_data = pickle.load(save_file)
            self.play_counter = saved_data['video_index']
            time_played = sum(self.play_times[:self.play_counter])/1000.
            print(encapsulate_text(str('VIDEO LOADED AT:' + str(time_played) + 'counter: ' +
                                   str(self.play_counter)), color='red'))
            self.mov.seek(time_played)
            self.mov.play()
            self.mov.draw()
            self.mov.pause()

    class Image:

        """A class to store images.

        In order to make a interaction with images as easy as possible, this class
        the possibility to store all necessary information of an image to have easy
        access to them. This is especially intended to be used with the four images
        relevant functions of Screen_Handler.

        :param file_name: The filename of the image
        :type filename: str
        :param position: A tuple or a list of the x and y coordinate of the image.
        :type position: tuple, list
        :param size: The size of the image. If None, the original size of the image\
                        will be used.
        :type size: tuple, list
        :param scale_factor: The factor to rescale the imige
        :type scale_factor: float
        """

        def __init__(self, file_name, position=(0, 0), size=None, scale_factor=1):
            self.image = PIL.Image.open(file_name)
            self.image.load()
            self.position = position
            self.size = self.image.size
            self.has_aoi = False

            if not (scale_factor == 1):
                self.resize(scale_factor)

            if size:
                self.resize(size)
            else:
                self.size = self.image.size

        def resize(self, new_size, proportional=True):
            """A function to resize or rescale the image.

            Whether to resize or rescale the image is defined by the type of new_size:
            If it is list or tuple, the image will be resized, if it is float or int,
            it will be rescaled.

            :param new_size: The target size or scaling factor.
            :type new_size: list, tuple, int, float
            :param proportional: Whether the aspect ratio of the image should be\
                            kept while resizing. If True, the image will be scaled to fit\
                            completely within the rectangle drawn by new_size. Irrelevant\
                            for rescaling.
            :type proportional: bool
            """
            if type(new_size) in [list, tuple]:
                if proportional:
                    if type(self.size) is tuple:
                        self.size = list(self.size)
                    ratio = float(self.size[0]) / float(self.size[1])
                    # print new_size[0], new_size[1], ratio
                    if ratio < float(new_size[0]) / float(new_size[1]):
                        self.size[1] = int(new_size[1])
                        self.size[0] = int(new_size[1] * ratio)
                    else:
                        self.size[0] = int(new_size[0])
                        self.size[1] = int(new_size[0] / ratio)
                    self.size = tuple(self.size)
                else:
                    self.size = new_size
            else:
                self.size = (int(i * new_size) for i in self.size)
            self.image = self.image.resize(self.size)

        def move(self, new_position):
            """Move the image to a new location on the screen.

            :param new_position: the new absolute position on the screen.
            :type new_position: list, tuble

            .. todo:: :py:func:`move` Implement relative movement.
            """
            self.position = new_position
            self.has_aoi = False
            self.aoi = []

        def get_ulc_pos(self):
            """Returns the position of the upper left corner.

            :return: position of the upper left corner
            """
            return self.position[0] - int(self.size[0] / 2), self.position[1] - int(self.size[1] / 2)

    def __init__(self, stimtracker_parameters, mucap_parameters, instruction_texts, object_picker, dispsize,
                 nirs_param, screennr=0, resize_proportional=True):

        self.resize_proportional = resize_proportional
        self.stim_tracker_square = False

        # Create Pygaze/Psychopy Objects
        self.display = libscreen.Display(screennr=screennr)
        # General screens
        self.screens = {}
        # Dict for text screens
        self.screens_txt = {}
        # Dict for Image Objects
        self.images_stored = {}
        # Boolean for stimtracker signal
        self.stimtracker_black = True
        # Some parameters and text
        self.mucap_parameters = mucap_parameters
        # Some parameters and text
        self.stimtracker_parameters = stimtracker_parameters
        self.instruction_texts = instruction_texts
        # Object picker for selecting objects to be presented on the screen
        self.object_picker = object_picker
        self.dispsize = dispsize

        # For later use
        self.images_stored = {}

        # Progress bar stuff
        self.nirs_param = nirs_param  # As baseline is needed for NIRS, baseline duration is defined here
        # Progress bar geometry
        self.progressb = {}
        self.progressb['drawn'] = False
        self.progressb['x'] = self.dispsize[0] * .1
        self.progressb['x_len'] = self.dispsize[0] * .8
        self.progressb['y'] = 1000.
        self.progressb['y_len'] = 100.

    def make_text_screen(self, text, name):
        """ Make a screen containing text
        """
        self.screens_txt[name] = {}
        self.screens_txt[name]['white'] = libscreen.Screen()
        self.draw_text(text, self.screens_txt[name]['white'], fontsize=32)
        self.copy_screen_w_stimtracker_pixel(self.screens_txt[name])

    def show_text_screen(self, name):
        return self.show_a_screen(self.screens_txt[name])

    def make_fix_cross_screen(self):
        """ Create a simple screen with a central fixation cross and
        stimtracker signal
        """
        self.fix_cross_scr = {}
        self.fix_cross_scr['white'] = libscreen.Screen()
        self.fix_cross_scr['white'].draw_fixation(pw=3, diameter=75)
        self.copy_screen_w_stimtracker_pixel(self.fix_cross_scr)

    def add_progress_2_fix_cross_screen(self, fraction_filled=0.):
        # Add section filled
        if fraction_filled > 0.:
            self.fix_cross_scr['white'].draw_rect('green', self.progressb['x'], self.progressb['y'],
                                                  self.progressb['x_len']*fraction_filled, self.progressb['y_len'],
                                                  5, fill=True)
            self.fix_cross_scr['black'].draw_rect('green', self.progressb['x'], self.progressb['y'],
                                                  self.progressb['x_len']*fraction_filled, self.progressb['y_len'],
                                                  5, fill=True)
        return self.show_a_screen(self.fix_cross_scr)

    def show_base_line_screen_w_progress(self, min_dur, max_dur):
        self.make_fix_cross_screen()
        baseline_duration = random.randrange(min_dur, max_dur)
        t0 = libtime.get_time()
        self.fix_cross_scr['white'].draw_rect('green', self.progressb['x'], self.progressb['y'],
                                              self.progressb['x_len'], self.progressb['y_len'], 5)
        self.fix_cross_scr['black'].draw_rect('green', self.progressb['x'], self.progressb['y'],
                                              self.progressb['x_len'], self.progressb['y_len'], 5)
        for i in range(0, baseline_duration + 1):
            self.add_progress_2_fix_cross_screen(fraction_filled=i/float(baseline_duration))
            time.sleep(1.)
        t1 = libtime.get_time()

        return t0, t1

    def show_fix_cross_screen(self):
        """ Show fixation cross with stimtracker signal respectively
        """

        return self.show_a_screen(self.fix_cross_scr)

    def show_a_screen(self, screen):
        """Method to show screen selection to participant
        """
        if self.stimtracker_black:
            self.show(screen['black'])
        else:
            self.show(screen['white'])
        self.stimtracker_black = not self.stimtracker_black
        return libtime.get_time()

    def make_and_draw_screen(self, text, fontsize=30, color=None, mucap_stim=None):
        """ Draw text central on a blank Screen and present it
            :param text: Text to be presented
            :type text: str
            :param mucap_stim: Decides what type of mucap stim shall be added to screen
            :type mucap_stim: str
        """
        self.last_screen = None
        instruction_screen = {}
        instruction_screen['white'] = libscreen.Screen()
        self.draw_text(text, instruction_screen['white'], fontsize=fontsize, color=color)
        # check for the correct stimtracker signal
        if self.stimtracker_black:
            self.copy_screen_w_stimtracker_pixel(instruction_screen)
            instruction_screen = instruction_screen['black']
        else:
            instruction_screen = instruction_screen['white']
        # switch stimtracker signal
        self.stimtracker_black = not self.stimtracker_black
        # add mucap pixel
        self.make_mucap_trigger_pixel(instruction_screen, mucap_stim)
        # actually show the created screen
        self.display.fill(instruction_screen)
        self.display.show()
        return libtime.get_time()

    def copy_screen_w_stimtracker_pixel(self, screen):
        """ Copy screen and add a stimtracker pixel to it
             :param screen: dictionary conaining of pygaze Screen() object in item ['white']
             output will be in item ['black']
         """

        screen['black'] = libscreen.Screen()
        screen['black'].copy(screen['white'])
        screen['black'].draw_rect(colour=self.stimtracker_parameters['color'],
                                  x=self.stimtracker_parameters['position'][0],
                                  y=self.stimtracker_parameters['position'][1],
                                  w=self.stimtracker_parameters['size'][0],
                                  h=self.stimtracker_parameters['size'][1], fill=True)

    def make_mucap_trigger_pixel(self, screen, mucap_stim=None):
        """ Method to put a mucap pixel for a defined event on screen
        :param screen: Screen to draw pixel on
        :type: Pygaze screen
        :param mucap_stim: type of event to triggered by pixel
        :type mucap_stim: str
        """
        if mucap_stim:
            color = self.mucap_parameters[mucap_stim]
        else:
            color = None
        if color:
            screen.draw_rect(colour=color,
                             x=self.mucap_parameters['pixel_pos'][0],
                             y=self.mucap_parameters['pixel_pos'][1],
                             w=1, h=1, fill=True)

    def draw_aoi(self, screen, image):
        """ Method to draw aoi as rectangle on screen
        :param screen: screen to be drawn on
        :type screen:
        :param image: image of which aoi shall be drawn
        :type image:
        """
        screen.draw_rect(x=image.position[0] - image.size[0]/2.0, y=image.position[1] - image.size[1]/2.0,
                         w=image.size[0], h=image.size[1])

    def draw_gaze_cursor(self, tracker):
        if self.last_screen:
            temp_screen = libscreen.Screen()
            temp_screen.copy(self.last_screen)
            temp_screen.draw_fixation('cross', 'green', tracker.sample())
            self.display.fill(temp_screen)
            self.display.show()

    def store_image(self, name, file_name, position=(0, 0), size=None, scale_factor=1):
        """Store images, which should be drawn later on.

        In order to make the redrawing of images as easy as possible, images
        aren't drawn directly to the screen, but instead are stored in a
        dictionary as :py:class:`Image` objects.

        :param name: name of the image to be stored. With this name the image\
                        can also be retrieved.
        :type name: str
        :param file_name: directory and file name of the image.
        :type file_name: str
        :param position: Position, where the image should be drawn.
        :type position: list, tuple
        :param size: new size tor resize the image. If None is given, it will\
                        use the default size of the image
        :type size: list, tuple
        :param scale: scale to rescale the image. If none is given, it will not\
                        be rescaled
        :type scale: int, float
        """
        self.images_stored[name] = self.Image(file_name, position, size, scale_factor)

    def draw_image(self, screen, name, position=None, new_size=None, resize_proportional=None, draw_all=False):
        """Add image to the screen to be shown with :py:func:`show`.

        :param screen: the screen, the image should be drawn on
        :type screen: :class:`pygaze.libscreen.Screen`
        :param name: name of image
        :type name: str
        :param position: position where the image should be drawn. If None, the\
                        image will be drawn the in the image stored position
        :type position: list, tuple
        :param new_size: new size to resize the image. If None, the image will\
                        not be resized
        :type new_size: list, tuple, int, float
        :param draw_all: add the image to the separat screen for images which\
                        should be drawn with every redraw of the screen.
        :type draw_all: bool

        .. todo:: :py:func:`draw_image` If I understand the code\
                        correctly, there is at the moment no way to combine\
                        a draw_all=False and draw_all=False call of this\
                        function. This should be investigated in if it's\
                        true fixed.
        """
        image = self.images_stored[name]
        if position:
            image.move(position)

        if new_size:
            if type(resize_proportional) is not bool:
                resize_proportional = self.resize_proportional
            image.resize(new_size, resize_proportional)

        if not draw_all:
            screen.draw_image(image.image, image.position, None)
            # self.screen_insturctions.draw_rect(colour='red', x = image.get_ulc_pos()[0], y = image.get_ulc_pos()[1],
            #                                    w= image.size[0], h = image.size[1])
        else:
            screen.draw_image(image.image, image.position, None)
            screen.draw_rect(colour='red', x=image.get_ulc_pos()[0], y=image.get_ulc_pos()[
                             1], w=image.size[0], h=image.size[1])

    def draw_text(self,  text, screen, color=None, position=None, fontsize=30, font='mono'):
        """Draw text on the screen.

        :param text: the text to be drawn
        :type text: str
        :param color: the color of the text to be drawn. By default this is the\
                        foreground color.
        :type color: str, list, tuple
        :param position: the position of the to be drawn text. By default it\
                        will be drawn in the center of the screen.
        :type position: list, tuple
        :param fontsize: font size of the text. By default 12.
        :type fontsize: int
        :param font: font in which the text should be drawn.
        :type font: str

        .. todo:: :py:func:`draw_text` This needs to be updatet to the new way\
                        of drawing stuff.
        """
        screen.draw_text(text=text, colour=color, pos=position, fontsize=fontsize, font='mono')

    def draw_rating_scale(self, text, choices=None, labels=[], low=0, high=1, precision=1, scale=' = ja . . . nein = ',
                          only_mouse=False, use_mouse=False, markerStart=None, mucap_marker=None):
        """
        Create and draw a rating scale to be used in questionnaires
        """

        # use RatingScale directly from PsychoPy
        rating_scale = RatingScale(pygaze.expdisplay, low=low, high=high, labels=labels, precision=precision,
                                   markerStart=markerStart, mouseOnly=only_mouse, noMouse=not use_mouse,
                                   scale=str(low)+scale+str(high), textColor='black')
        temp_screen = libscreen.Screen()
        temp_screen.screen.append(rating_scale)
        # add the question to the screen
        text_stim = TextStim(pygaze.expdisplay, text, color='black', height=50, wrapWidth=1000)
        temp_screen.screen.append(text_stim)
        # add the stimtracker signal to the screen
        if self.stimtracker_black:
            temp_screen.draw_rect(colour=self.stimtracker_parameters['color'],
                                  x=self.stimtracker_parameters['position'][0],
                                  y=self.stimtracker_parameters['position'][1],
                                  w=self.stimtracker_parameters['size'][0],
                                  h=self.stimtracker_parameters['size'][1], fill=True)
        self.stimtracker_black = not self.stimtracker_black
        # add the mucap pixel to the screen
        self.make_mucap_trigger_pixel(temp_screen, mucap_marker)
        draw_time = libtime.get_time()
        # wait for input on the rating scale
        while rating_scale.noResponse:
            self.display.fill(temp_screen)
            self.display.show()
        return rating_scale.getHistory(), draw_time

    def show(self, screen, color='green', tracker=None):
        """Show the screen, to which the images and texts are added by
        :py:func`darw_image` and :py:func:`draw_text`. This needs to be done in
        order to get the screen to the display.

        :param screen: psychopy screen to be shown
        :type screen: psychopy screen
        :param color: Color of fixation cross
        :type color:
        """

        # if there is a EyeTracker object given to the EventHandler, add a fixation cursor to the screen
        if tracker:
            active_screen = libscreen.Screen()
            active_screen.copy(screen)
            screen.draw_fixation(colour=color, pos=tracker.sample())
            self.display.fill(active_screen)
        else:
            self.display.fill(screen)

        self.display.show()

    def give_stim_tracker_signal(self, screen):
        """Method that will create a little black square for stim tracking using a Tobii stim_tracker_square,
        if also a white sqare is used, bugs in blinking appear...
        :param screen: screen to give stimtracker stimulus
        """

        if self.stimtracker_black:
            screen.draw_rect(colour=(0, 0, 0), x=72, y=1052, w=20, h=20, fill=True)
        self.stimtracker_black = not self.stimtracker_black

    def make_screenshot(self, filename='screenshot.png'):
        """
        Save an image of the current screen.
        """

        # print(encapsulate_text(str(self.display), color='red'))
        # self.display.getMovieFrame()
        self.display.make_screenshot(filename)


class TriggerTimer(Thread):

    """A small class to trigger events.

    :param trigger_event: The event to be triggert
    :type trigger_event: threading.Event
    :param trigger_time: The time intervalls in ms, within which trigger_event should be triggerd. Default: 1000
    :param_type: int or float

    """

    def __init__(self, trigger_event, trigger_time=1000, message=None, name='TriggerTimer'):
        super(TriggerTimer, self).__init__(name=name)
        self.trigger_event = trigger_event
        self.trigger_time = trigger_time
        self.message = message
        self.is_running = False
        self.daemon = True
        self.name = name
        print('TriggerTimer initialized...')

    def stop(self):
        self.is_running = False

    def run(self):
        self.is_running = True
        print('TriggerTimer running...')
        while self.is_running:
            # print('\033[9' + str(self.a) + 'mPINGPONG\033[0m')
            if self.message:
                self.trigger_event.set(self.message)
            else:
                self.trigger_event.set()
            self.trigger_event.clear()
            time.sleep(self.trigger_time/1000.)


class LogManager(object):
    """	A class to manage participant personal and behaviorial data and what is happening on the screen screen
        :param data_dir: Directory where data shall be written to
        :type data_dir: str
        :param tracker:
        :type tracker:
   """

    class TobiiDumper(Thread):
        """ A class to collect all eyetracking comming from a Tobii eyetracker.

        So far this was only tested with a Tobii TX300. The outfile will contain one line per data package
        received by the tracker.
        1st column: timestamp

        Data produced by this class can easily be read and filtered in by :py:func jap_analyzer.py

        :param tracker: Eyetracker to collect data from
        :type tracker: Pygaze eyetracker object
        :param path: Directory where data shall be written to
        :type path: str
        :param time: Time in [ms] how often data shall be written to disk
        :type time: int
        :param verbose:
        :type verbose: boolean
        :param name: Name for thread
        :type name: str
        """

        def __init__(self, tracker, path, prob_code, time=1000, verbose=False, save_event=Event(), name='TobiiDumper'):
            super(LogManager.TobiiDumper, self).__init__(name=name)

            self.tracker = tracker
            self.time = time
            self.verbose = verbose
            self.name = name
            self.path = path
            self.save_event = save_event
            # set file names
            self.last_len = 0
            self.dump_file = os.path.join(path, prob_code + '_tobii_dump')
            self.time_dump = os.path.join(path, 'dump_time')
            self.dump_time = []

            if os.path.isfile(self.dump_file):
                with open(self.dump_file, 'w') as dump_file:
                    dump_file.write('')

            self.running = False
            self.save_trigger = Event()
            self.save_lock = Lock()
            self.daemon = True
            self.event = Event()
            self.trigger_timer = TriggerTimer(self.event, trigger_time=time, name='TobiiDumperTrigger')
            # Stimtracker stuff
            self.stimtracker_log = liblog.Logfile(filename=os.path.join(self.path, prob_code+'_Stimtrackerlog'))
            self.stimtracker_log.write(['device_time_stamp', 'experiment_time', 'system_time_stamp', 'change_type',
                                        'value'])
            self.tracker.eyetracker.subscribe_to(tr.EYETRACKER_EXTERNAL_SIGNAL, self.stimtracker_callback,
                                                 as_dictionary=True)

        def __convert_2d(self, point):
            """
            Convert a Point to a vector
            """

            return (point.x, point.y)

        def __convert_3d(self, point):
            """
            Convert a Point to a vector
            """

            return (point.x, point.y, point.z)

        def stimtracker_callback(self, stimtracker_data):
            self.stimtracker_log.write([stimtracker_data['device_time_stamp'], libtime.get_time(),
                                        stimtracker_data['system_time_stamp'], stimtracker_data['change_type'],
                                        stimtracker_data['value']])

        def get_data(self, last_len):
            """
            Get the last chunk of data from the eyetracker
            """
            raw_data = copy.copy(self.tracker.gaze)
            self.dump += raw_data[last_len:]
            return len(raw_data)

        def save(self):
            """
            Convert the data to a string and append it to the given save file
            """

            out = ''
            for n, item in enumerate(self.dump):
                out_list = []
                out_list.append(str(item['device_time_stamp']))
                out_list.append(str(item['left_gaze_point_on_display_area']))
                out_list.append(str(item['right_gaze_point_on_display_area']))
                out_list.append(str(item['left_gaze_point_in_user_coordinate_system']))
                out_list.append(str(item['right_gaze_point_in_user_coordinate_system']))
                out_list.append(str(item['left_gaze_origin_in_user_coordinate_system']))
                out_list.append(str(item['right_gaze_origin_in_user_coordinate_system']))
                out_list.append(str(item['left_gaze_origin_in_trackbox_coordinate_system']))
                out_list.append(str(item['right_gaze_origin_in_trackbox_coordinate_system']))
                out_list.append(str(item['left_pupil_diameter']))
                out_list.append(str(item['right_pupil_diameter']))
                out_list.append(str(item['left_gaze_origin_validity']))
                out_list.append(str(item['right_gaze_origin_validity']))
                out_list.append(str(0))  # item['TrigSignal']))
                out += '\t'.join(out_list) + '\n'
            with open(self.dump_file, 'a') as dump_file:
                dump_file.write(out)

        def run(self):
            self.running = True
            # self.trigger_timer.start()
            while self.running:
                # time.sleep(60)
                # wait for the signal to save eyetracking data
                self.save_trigger.wait()
                # only save data when the dumper is actually still running
                if not self.running:
                    break
                # self.running = False
                # self.evnet.wait()
                self.event.clear()
                time_a = libtime.get_time()
                self.dump = []
                if self.verbose:
                    print(encapsulate_text('STARTED SAVING ', color='red'))
                try:
                    self.save_lock.acquire()
                    # get the data from the eyetracker
                    self.last_len = self.get_data(self.last_len)
                    # actually save the data
                    self.save()
                    self.save_lock.release()
                except:
                    print(encapsulate_text('ERROR ERROR ERROR', color='red', background='yellow'))
                    print(sys.exc_info())
                    print(encapsulate_text('ERROR ERROR ERROR', color='red', background='yellow'))
                self.save_event.set()
                self.save_trigger.set()
                self.save_trigger.clear()
                time_b = libtime.get_time()
                self.dump_time.append(str(time_a) + '\t' + str(self.last_len) + '\t' + str(time_b - time_a))
                # with open(self.time_dump, 'w') as time_file:
                #     time_file.write('\n'.join(self.dump_time))
                if self.verbose:
                    print(encapsulate_text('FINISHED SAVING', color='green'))

        def stop(self, stop_event=Event()):
            self.running = False
            self.dump = []
            self.tracker.eyetracker.unsubscribe_from(tr.EYETRACKER_EXTERNAL_SIGNAL, self.stimtracker_callback)
            # save the data one last time before actually stopping
            if self.verbose:
                print(encapsulate_text('STARTED SAVING ', color='blue'))
            self.stimtracker_log.close()
            self.save_lock.acquire()
            self.last_len = self.get_data(self.last_len)
            self.save()
            self.save_lock.release()
            if self.verbose:
                print(encapsulate_text('FINISHED SAVING', color='yellow'))
            stop_event.set()

    class DataRecorder(Thread):
        """ A class to record the course of the paradigm (what is shown on the screen)

        :param log_dir: Directory where data shall be stored
        :param code: Some sort of subject ID
        :type code: str
        :param name: Name for Thread
        :type name: str

        """

        def __init__(self, log_dir, code, log_event, tracker=None, header=None, name='DataRecorder'):
            super(LogManager.DataRecorder, self).__init__(name=name)
            self.do_write = log_event
            self.tracker = tracker
            self.log_name = os.path.join(log_dir, code + '_' + name)
            # create Pygaze logfile
            self.log = liblog.Logfile(filename=self.log_name)
            if header:
                self.log.write(header)
            else:
                self.log.write(['Time', 'Screen'])
            print('Some DataRecorder initialized')

        def run(self):
            self.is_running = True
            while self.is_running:
                # wait till some other thread wants to log anything
                message = self.do_write.wait()
                self.do_write.clear()
                exp_time = libtime.get_time()
                # if there is an eyetracker, get the current time from the last data package
                if self.tracker:
                    try:
                        tracker_time = self.tracker.gaze[-1]['device_time_stamp']
                    except IndexError:
                        tracker_time = 0
                else:
                    tracker_time = 0.
                # write data to log file
                if type(message) is list:
                    self.log.write([exp_time, tracker_time] + message)
                else:
                    self.log.write([exp_time, tracker_time, message])

        def stop(self):
            self.is_running = False
            self.do_write.set('finished')
            libtime.pause(500)
            self.log.close()

    def __init__(self, data_dir, block_name=None, tracker=None, participant_data=None, age_group=None, verbose=False,
                 mucap_dir=None, mucap_marker=None, mucap_wmv=None, fixation_data=None, log_dict={}, screenshots=False,
                 tobii_save_event=None):
        # ?
        self.check_data = 'n'
        # log dir
        self.data_dir_all_subj = data_dir
        self.fixation_data = fixation_data
        # Trying to automatically start mucap.exe DOES NOT WORK
        # ctypes.WinDLL(os.path.join(mucap_dir,'DirectShowLib-2005.dll'))
        # os.system(os.path.join(mucap_dir,'muCap.exe'))
        # min age of participant
        min_age = 8
        # max age of participant
        max_age = 60
        # get current date
        date = time.strftime("%Y-%m-%dT%H_%M_%S")
        # rountine to enter participant data via console
        # TODO: check what is still needed from this manual data input and get rid of the deprecated stuff
        if not participant_data:
            while not self.check_data == 'y':
                self.part_name = raw_input('Name of participant:')
                part_age = input('Age of participant:')
                while not isinstance(part_age, int):
                    part_age = input('Age of participant:')
                while part_age < min_age:
                    part_age = input('Age too low, reenter :')
                while part_age > max_age:
                    part_age = input('Age too high, reenter :')

                part_type = raw_input('Participant group: Autistic(a) or control(c)?')
                while not (part_type == 'a' or part_type == 'c'):
                    part_type = raw_input('Not a correct participant type, autistic(a) or control(c)?')

                part_sex = raw_input('Sex of participant(m/f)?')
                while not (part_sex == 'm'or part_sex == 'f'):
                    part_sex = raw_input('Not a correct sex (m/f)')

                print('---------------------------------------')
                print('CHECK DATA:')
                print('Participant group: ' + part_type)
                print('Participant age: ' + str(part_age))
                print('Participant sex: ' + part_sex)
                print('---------------------------------------')
                self.check_data = raw_input('All data entered correctly(y/n)?')
            self.data = {
                    'code': subject_code,
                    'date': part_age,
                    'sex': part_sex,
                    'group': part_type}
        else:
            # get the participant data from the parameters of this class. This is the normal way to get the data
            self.data = participant_data

        # check for a participant folder and if it doesn't exist, create it
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        self.data_dir = os.path.join(data_dir, self.data['code'])
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        else:
            print('Participant ' + self.data['code'] + ' has already data, will be overwritten!')
        # if the block name was given, make sure there is a folder for that given block
        if block_name:
            self.data_dir = os.path.join(self.data_dir, block_name)
            if not os.path.exists(self.data_dir):
                os.mkdir(self.data_dir)

        # save the participant data
        self.log_name = os.path.join(self.data_dir, self.data['code'] + '_info')

        self.log = liblog.Logfile(filename=self.log_name)
        self.log.write(['Date', date])
        self.log.write(['Code', self.data['code']])
        if 'group' in self.data.keys():
            self.log.write(['Group', self.data['group']])
        self.log.write(['Age', self.data['date']])
        self.log.write(['Sex', self.data['sex']])
        if age_group:
            self.log.write(['Age Group', age_group])
        self.log.close()
        print('Participant data written to ' + self.log_name + '.txt')

        # create all needed logger given in the log_dict
        self.logger_dict = {}
        for name, parameters in log_dict.items():
            if tracker:
                self.logger_dict[name] = self.DataRecorder(self.data_dir, self.data['code'], parameters[0],
                                                           tracker, header=parameters[1], name=name)
            else:
                self.logger_dict[name] = self.DataRecorder(self.data_dir, self.data['code'], parameters[0],
                                                           tracker=None, header=parameters[1], name=name)
        print(self.logger_dict)
        # self.do_write = MyEvent()

        # if an eyetracker is given as a parameter, create a TobiiDumper to save the eyetracking data
        # TODO: This needs to be modified to accommodate other eyetracker types
        if tracker:
            if tobii_save_event:
                self.tobii_dumper = self.TobiiDumper(tracker, self.data_dir, self.data['code'],
                                                     verbose=verbose, save_event=tobii_save_event)
            else:
                self.tobii_dumper = self.TobiiDumper(tracker, self.data_dir, self.data['code'], verbose=verbose)
        else:
            self.tobii_dumper = None

        # mucap marker file
        self.marker_file = mucap_marker if mucap_marker else None
        # mucap video file
        self.video_file = mucap_wmv if mucap_wmv else None
        # relative path to mucap dir
        self.mucap_dir = mucap_dir if mucap_dir else None
        # remove old marker and video files
        if mucap_dir:
            old_maker_file = os.path.join(self.mucap_dir, self.marker_file)
            os.remove(old_maker_file) if os.path.exists(old_maker_file) else None
            old_video_file = os.path.join(self.mucap_dir, self.video_file)
            os.remove(old_video_file) if os.path.exists(old_video_file) else None

        # prepare the folder and counter to create screenshots
        if screenshots:
            self.screenshot_number = 0
            self.screenshot_dir = os.path.join(self.data_dir, 'screenshots')
            # check whether there are already screenshots and if so remove them.
            if not os.path.exists(self.screenshot_dir):
                os.mkdir(self.screenshot_dir)
            else:
                screenshot_list = os.listdir(self.screenshot_dir)
                if len(screenshot_list) > 0:
                    for screenshot in screenshot_list:
                        os.remove(os.path.join(self.screenshot_dir, screenshot))

    def start(self):
        """ Start logging eyetracking data
        """
        if self.tobii_dumper:
            self.tobii_dumper.start()
        for recorder in self.logger_dict.values():
            print(recorder)
            recorder.start()

    def move_n_rename_data(self):
        """ Move all data where it belongs: HI's dir
        """
        self.move_n_rename_data_file(self.mucap_dir, self.marker_file)
        self.move_n_rename_data_file(self.mucap_dir, self.video_file)
        self.move_n_rename_data_file(self.tobii_dumper.path, 'tobii_dump.txt')
        self.move_n_rename_data_file(self.data_dir_all_subj, 'sequence.txt')

    def move_n_rename_data_file(self, directoy, tar_file):
        """ Move a particular file to HI's data dir and put subjectID as prefix, old files
        will be deleted
        :param directory: relative path where file to move is located
        :type: str
        :param tar_file: File to move and rename
        :type tar_file: str
        """
        m_file = os.path.join(directoy, tar_file)
        new_m_file = os.path.join(self.data_dir,  self.data['code'] + '_' + tar_file)
        os.remove(new_m_file) if os.path.exists(new_m_file) else None
        os.rename(m_file, new_m_file) if os.path.exists(m_file) else None

    def save_list(self, data_list, name):
        """
        Save any given list to a file
        """

        out_list = []
        for i in data_list:
            if type(i) == list:
                temp_list = []
                for j in i:
                    temp_list.append(str(j))
                out_list.append('\t'.join(temp_list))
            else:
                out_list.append(str(i))

        with open(os.path.join(self.data_dir, self.data['code']+'_'+name), 'w') as out_file:
            out_file.write('\n'.join(out_list))

    def get_screenshot_name(self, file_format='png'):
        """
        Get the file name including the path for the next screenshot.
        """
        self.screenshot_number += 1
        return os.path.join(self.screenshot_dir, 'screenshot_{:03d}.'.format(self.screenshot_number)+file_format)

    def stop(self):
        """ Stop data collection
        """
        if self.tobii_dumper:
            stop_event = Event()
            stop_event.clear()
            self.tobii_dumper.stop(stop_event)
            stop_event.wait()
        for recorder in self.logger_dict.values():
            recorder.stop()
