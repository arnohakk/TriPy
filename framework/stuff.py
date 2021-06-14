from threading import enumerate
import datetime
import time
import threading


def colored_text(text, color='', background=''):
    """ A small function to print colored text in consoles.

    This function returns a given string wraped in ANSI color codes,
    so it is printed in the given color, if the console used to
    execude the code suppots ANSI color codes. Current colors are:
    * red
    * yellow
    * green
    * blue
    * magenta or purple
    * cyan
    * black
    * white
    All those colors are possible to be used as foreground colors by just
    giving them through the color parameter or as background colors by giving
    them through the background parameter"""

    ansi_end = '\033[0m'
    color_ansi = '\033['
    background_ansi = '\033['
    if color == 'yellow':
        color_ansi += '93m'
    elif color == 'red':
        color_ansi += '91m'
    elif color == 'blue':
        color_ansi += '94m'
    elif color == 'green':
        color_ansi += '92m'
    elif color == 'magenta' or color == 'purple':
        color_ansi += '35m'
    elif color == 'cyan':
        color_ansi += '36m'
    elif color == 'white':
        color_ansi += '37m'
    elif color == 'black':
        color_ansi += '30m'
    else:
        color_ansi += '39m'

    if background == 'black':
        background_ansi += '40m'
    elif background == 'red':
        background_ansi += '41m'
    elif background == 'green':
        background_ansi += '42m'
    elif background == 'yellow':
        background_ansi += '43m'
    elif background == 'blue':
        background_ansi += '44m'
    elif background == 'magenta' or background == 'purple':
        background_ansi += '45m'
    elif background == 'cyan':
        background_ansi += '46m'
    elif background == 'white':
        background_ansi += '47m'
    else:
        background_ansi += '49m'
    return background_ansi + color_ansi + str(text) + ansi_end


def encapsulate_text(text, enc_char='#', wrap='', color='', background=''):
    '''A small function to encapsulate text with a given character.'''
    text_lines = text.split('\n')
    length = 0
    for line in text_lines:
        if len(line) > length:
            length = len(line)
    if color or background:
        out_text = colored_text(wrap + enc_char * (length + 4), color=color, background=background) + '\n'
    else:
        out_text = wrap + enc_char * (length + 4) + '\n'
    for line in text_lines:
        if color or background:
            out_text += colored_text(enc_char + ' ' + line + ' ' * (length - len(line) + 1) + enc_char, color=color,
                                     background=background)
            out_text += '\n'
        else:
            out_text += enc_char + ' ' + line + ' ' * (length - len(line) + 1) + enc_char + '\n'
    if color or background:
        out_text += colored_text(enc_char * (length + 4) + wrap, color=color, background=background)
    else:
        out_text += enc_char * (length + 4) + wrap

    return out_text


def print_threads():
    print('====================================')
    print(encapsulate_text('Threads running:'))
    running_threads = enumerate()
    for thread in running_threads:
        print('\t' + str(thread))
    print('<<<< ' + str(len(running_threads)) + ' threads running')
    print('====================================')


class StopWatch(threading.Thread):

    def __init__(self, interval=10, color='blue', name='StopWatch'):
        super(StopWatch, self).__init__(name=name)
        self.interval = interval
        self.color = color
        self.daemon = True
        self.is_running = False

    def run(self):
        self.is_running = True
        time_start = datetime.datetime.now()
        while self.is_running:
            time_now = datetime.datetime.now()
            time_delta = time_now - time_start
            print(encapsulate_text(str(time_delta), color=self.color))
            time.sleep(self.interval)
