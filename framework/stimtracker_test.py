import os
import csv
import argparse
from framework.stuff import encapsulate_text


def count_stimtracker_signal_switches(dump_file):

    stim_signal = None
    stim_signal_switch = -1

    with open(dump_file, 'rb') as dumpin_file:
        dumpin = csv.reader(dumpin_file, delimiter='\t')

        for row in dumpin:
            if row[-1] != stim_signal:
                stim_signal = row[-1]
                stim_signal_switch += 1
    return stim_signal_switch, stim_signal

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test tobii_dump files for stimtracker signals')
    parser.add_argument('-f', '--dump_file', default='logs/1337_H4x0r/1337_H4x0r_tobii_dump',
                        metavar='DUMP_FILE', help='tobii dump file to test')
    args = parser.parse_known_args()

    signal_switch, signal = count_stimtracker_signal_switches(args[0].dump_file)

    if signal_switch > 0:
        print(encapsulate_text(str(signal_switch)+' stimtracker signal switches. Signal ok', color='green'))
    else:
        print(encapsulate_text(str(signal_switch)+' stimtracker signal switches. No signal!\nSignal in data: ' +
                               str(signal), color='red'))
