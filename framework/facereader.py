import sys
import socket
import struct
import time
import xml.etree.cElementTree as ET
import threading
import json


def extract_message(msg):
    msg_type_length = struct.unpack('I', msg[:4])[0]
    msg_type = msg[4:msg_type_length + 4].decode('utf-8')
    xml = ET.fromstring(msg[msg_type_length + 4:])
    return msg_type, xml


class FaceReader:
    """
    FaceReader class to use the API provided by Noldus

    The purpose of this class is to operate FaceReader by Noldus. It uses all
    functionality given by the API documentation from Noldus.

    :param host: IP address of the host running FaceReader
    :type host: str
    :param port: Listening port set in FaceReader
    :type port: int
    :param buffer_size: At the moment I have no idea, why I added this\
                        parameter or what it is doing.
    :type buffer_size: int
    """

    class MySocket(threading.Thread):
        """
        Class to send and receive messages via TCP.
        """

        def __init__(self, host, port, log=None, func=None, func_args=None, sock=None):
            threading.Thread.__init__(self)
            self.daemon = True
            self.done = False
            self.func = func
            self.func_args = func_args
            if sock is None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.sock = sock
            if log is None:
                self.log = []
            else:
                self.log = log
            self.sock.connect((host, port))
            self.out = ''

        def connect(self, host, port):
            """
            Connect to a host via TCP using socket.

            :param host: IP address of host
            :type host: str
            :param port: Listening port at host
            :type port: int
            """
            self.sock.connect((host, port))

        def run(self):
            while not self.done:
                msg = self.receive()
                # print(msg)
                if msg:
                    msg_type, xml = extract_message(msg)
                    log_entry = self.parse_xml_log(xml)
                    self.log.append(log_entry)
                    out_xml = ET.tostring(xml).decode('utf-8')
                    self.out += out_xml + '\n\n'
                    with open('xml_out', 'w') as xml_file:
                        xml_file.write(self.out)
                    json_out = json.dumps(self.log, sort_keys=False, indent=2)
                    with open('json_out', 'w') as json_file:
                        json_file.write(json_out)
                    if self.func is not None:
                        self.func(log_entry, self.func_args)
                #else:
                #    self.done = True

        def parse_xml_log(self, xml):
            log_entry = {}
            for child in xml:
                if child.tag != 'ClassificationValues':
                    log_entry[child.tag] = child.text
                else:
                    cv = {}
                    for entry in child:
                        value = None
                        if entry.find('Type').text == 'Value':
                            entries = entry.find('Value').findall('float')
                            if len(entries) == 1:
                                value = float(entries[0].text)
                            else:
                                value = []
                                for i in entries:
                                    value.append(float(i.text))
                        elif entry.find('Type').text == 'State':
                            value = entry.find('State').find('string').text
                        cv[entry.find('Label').text] = value
                    log_entry[child.tag] = cv
            return log_entry

        def stop(self):
            """
            Stop the thread in which MySocket is running.
            """
            self.done = True

        def send(self, msg):
            """
            Send a message.

            :param msg: Message to be send
            :type msg: str
            """
            totalsent = 0
            msglen = len(msg)
            while totalsent < msglen:
                sent = self.sock.send(msg[totalsent:])
                if sent == 0:
                    raise RuntimeError('socket connection broke')
                totalsent = totalsent + sent

        def receive(self):
            """
            Receive a message from the set and connected host.

            :returns: str - the received message
            """
            raw_msglen = self.recv(4)
            if not raw_msglen:
                return None
            msglen = struct.unpack('I', raw_msglen)[0]
            return self.recv(msglen - 4)

        def recv(self, n):
            data = b''
            while len(data) < n:
                packet = self.sock.recv(n - len(data))
                if not packet:
                    return None
                data += packet
            return data

    def __init__(self, host, port, buffer_size=4, func=None, func_args=None):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.func = func
        self.func_args = func_args
        self.log = []
        self.mysocket = self.MySocket(self.host, self.port, self.log, func=self.func, func_args=self.func_args)
        self.logging = False
        self.events = []
        self.stimuli = []

    def start_analyzing(self):
        """
        Starts analyzing.

        This function sends an action message to FaceReader to start analyzing a preset data source.
        """
        self.create_action_message('FaceReader_Start_Analyzing')
        if self.logging:
            self.mysocket.start()

    def stop_analyzing(self):
        """
        Stops analyzing.

        This function sends an action message to Facereader to stop analyzing a preset data source.
        """
        self.create_action_message('FaceReader_Stop_Analyzing')
        if self.logging:
            self.mysocket.stop()

    def get_stimuli(self):
        """
        Receive a list of all stimuli set in the current FaceReader project

        :returns: A list of all stimuli
        """
        id_str, sock = self.create_action_message('FaceReader_Get_Stimuli')
        data = sock.receive()
        msg_type, xml = self.extract_message(data)
        self.stimuli = self.parse_xml(xml, 'FaceReader_Sends_Stimuli')
        return self.stimuli

    def score_stimulus(self, stimulus):
        """
        Scores a stimuli within the running anlysis

        :param stimulus: Name of the stimulus to score
        :type stimulus: str
        """
        id_str, sock = self.create_action_message('FaceReader_Score_Stimulus', stimulus)
        data = sock.receive()

    def get_events(self):
        """
        Receive a list of all event markers set in the current FaceReader project.

        :returns: A list of all event markers.
        """
        id_str, sock = self.create_action_message('FaceReader_Get_EventMarkers')
        data = sock.receive()
        msg_type, xml = self.extract_message(data)
        self.events = self.parse_xml(xml, 'FaceReader_Sends_EventMarkers')
        return self.events

    def score_event(self, event):
        """
        Scores a event marker within the running analysis.

        :param event: The name of the event marker to be scored.
        :type event: str
        """
        id_str, sock = self.create_action_message('FaceReader_Score_EventMarker', event)
        data = sock.receive()

    def start_state_log(self):
        """
        Starts a log mode, which returns the at the moment dominant facial expression.
        """
        id_str, sock = self.create_action_message('FaceReader_Start_StateLogSending')
        data = sock.receive()
        msg_type, xml = self.extract_message(data)
        if not self.logging:
            self.logging = True

    def stop_state_log(self):
        """
        Stops the log mode started with :py:func:`start_state_log`.
        """
        self.mysocket.stop()
        self.logging = False
        self.create_action_message('FaceReader_Stop_StateLogSending')
        data = self.mysocket.receive()
        msg_type, xml = self.extract_message(data)

    def start_detailed_log(self):
        """
        Starts a log mode, which returns all of the data known to man.
        """
        id_str, sock = self.create_action_message('FaceReader_Start_DetailedLogSending')
        data = sock.receive()
        msg_type, xml = self.extract_message(data)
        if not self.logging:
            self.logging = True

    def stop_detailed_log(self):
        """
        Stops the log mode started with :py:func:`start_detailed_log`.
        """
        self.mysocket.stop()
        self.logging = False
        self.create_action_message('FaceReader_Stop_DetailedLogSending')
        data = self.mysocket.receive()
        msg_type, xml = self.extract_message(data)

    def get_classification_value(self, value):
        """
        Get any value from within the ClassificationValues dictionary of the last log entry.
        """
        if len(self.mysocket.log) > 0:
            try:
                return self.mysocket.log[-1]['ClassificationValues'][value]
            except KeyError:
                return None
        else:
            return None

    def extract_message(self, msg):
        msg_type_length = struct.unpack('I', msg[:4])[0]
        msg_type = msg[4:msg_type_length + 4].decode('utf-8')
        xml = ET.fromstring(msg[msg_type_length + 4:])
        return msg_type, xml

    def parse_xml(self, xml, response_type_expected):
        response_type = xml.find('ResponseType').text
        if response_type == "FaceReader_Sends_Error":
            error_str = xml.find('Information').findall('string')
            for error in error_str:
                print('\033[91m' + error.text + '\033[0m')
            return None
        elif response_type != response_type_expected:
            print('\033[91mRepsonseType is ' + response_type + ' insted of ' + response_type_expected + '\033[0m')
            return None
        return_list = []
        for string in xml.find('Information').findall('string'):
            return_list.append(string.text)
        return return_list

    def create_action_message(self, am_type, information=None):
        am = ET.Element('ActionMessage')
        am.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        am.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
        ID = ET.SubElement(am, 'Id')
        id_str = str(int(time.time()))
        ID.text = id_str
        at = ET.SubElement(am, 'ActionType')
        at.text = am_type
        if information is not None:
            info = ET.SubElement(am, 'Information')
            string = ET.SubElement(info, 'string')
            string.text = information
        msg = self.create_message(b'FaceReaderAPI.Messages.ActionMessage', am)
        if self.mysocket.is_alive():
            sock = self.MySocket(self.host, self.port)
        else:
            sock = self.mysocket
        sock.send(msg)
        return id_str, sock

    def create_message(self, msg_type, xml):

        msg_type_len = struct.pack("I", len(msg_type))
        msg_data = msg_type_len + msg_type + \
            b"<?xml version='1.0' encoding='utf-8'?>" + ET.tostring(xml, encoding='utf-8')
        msg = struct.pack('I', len(msg_data) + 4) + msg_data
        return msg

    def connect(self):
        self.mysocket.connect(self.host, self.port)

    def print_xml(self, xml):
        print(ET.tostring(xml).decode('utf-8'))
