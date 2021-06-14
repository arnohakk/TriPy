import csv
from random import shuffle
import datetime
import time
import sys
from itertools import chain, repeat


def read_csv_file(csv_path, delimiter='\t'):
    csv_list = []
    with open(csv_path, 'rb') as csv_file:
        csv_in = csv.reader(csv_file, delimiter=delimiter)
        for row in csv_in:
            csv_list.append(row)
    return csv_list


def read_stim_time(tobii_dump):
    tobii_list = read_csv_file(tobii_dump)
    signal_old = -1
    stim_time = []
    for date in tobii_list:
        if date[-1] != signal_old:
            stim_time.append(int(date[0]))
            signal_old = date[-1]

    if len(stim_time) <= 1:
        raise ValueError('No stimtracker signal!')

    return stim_time


def read_recorder_log(screen_dump):
    screen_list = read_csv_file(screen_dump)
    last_screen = None
    screen_list_out = []
    for row in screen_list[1:]:
        try:
            # if row[4] != last_screen or row[4] == 'startgaze':
            screen_list_out.append(row)
            last_screen = row[4]
        except IndexError:
            pass
    return screen_list_out


def make_janirs_sequence(sequence):
    shuffled = False
    while not shuffled:
        shuffle(sequence)
        shuffled = True
        for i in range(len(sequence)-1):
            if sequence[i]['name'][:5] == sequence[i+1]['name'][:5]:
                shuffled = False
    return sequence

def make_sequence_from_list(state_list, times=None):
    if times:
        long_state_list = list(chain.from_iterable(repeat(e, times[0]) for e in state_list))
        shuffle(long_state_list)
        return True, long_state_list


def make_now_really_real_jap_sequence(items, times_per_item=None):
    if times_per_item:
        if len(times_per_item) == 1:
            times_per_item = times_per_item * len(items)
        source_list = []
        for i, item in enumerate(items):
            source_list.extend([item] * times_per_item[i])
    else:
        source_list = items

    items = []
    print(source_list)
    for item in source_list:
        if item[2] not in items:
            items.append(item[2])

    shuffle(items)
    print(items)

    while True:
        shuffle(source_list)
        if source_list[0][2] == items[0]:
            break

    for i in range(1, len(source_list)):
        if (not source_list[i][2] == source_list[0][2]) and any(k[2] == source_list[0][2] for k in source_list[i:]):
            rest_list = [k[2] for k in source_list[i:]]
            j = 0
            while True:
                if rest_list[j] == source_list[0][2]:
                    break
                j += 1
            insert_item = source_list.pop(i+j)
            source_list.insert(i, insert_item)

    return True, source_list


def waiting_animation(end_event):
    def spinning_cursor():
        while True:
            for cursor in '|/-\\':
                yield cursor

    spinner = spinning_cursor()
    print(spinner)
    while not end_event.is_set():
        sys.stdout.write(spinner.next())
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
