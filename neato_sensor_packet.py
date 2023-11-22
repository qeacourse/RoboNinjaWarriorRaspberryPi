import struct
import pickle

class NeatoSensorPacket(object):
    def __init__(self):
        self.response_dict = {}
        self.state = {"LeftWheel_PositionInMM": 0,
		      "RightWheel_PositionInMM": 0,
                      'LFRONTBIT':0,
                      'LSIDEBIT': 0,
                      'RFRONTBIT': 0,
                      'RSIDEBIT': 0,
		      "PitchInDegrees":0.0,
                      "RollInDegrees":0.0,
                      "XInG":0.0,
		      "YInG":0.0,
            	      "ZInG":0.0,
		      "SumInG":0.0,
                      "BatteryVoltage":0.0,
                      "FuelPercent": 0}

    def parse_packet(self, raw_packet, use_pickle):
        neato_outputs = raw_packet.split(chr(26))
        self.response_dict = {resp[:resp.find('\r')]: resp for resp in neato_outputs}
        ranges, intensites = self.getScanRanges()
        self.getMotors()
        self.getAnalogSensors()
        self.getCharger()
        self.getDigitalSensors()
        self.getAccel()
        packet_dict = {}
        packet_dict['ldsscanranges'] = (len(ranges), struct.pack('<%sH' % len(ranges), *[int(r*1000) for r in ranges]))
        packet_dict['motors'] = struct.pack('<2d', self.state['LeftWheel_PositionInMM'], self.state['RightWheel_PositionInMM'])
        packet_dict['digitalsensors'] = struct.pack('<4d', self.state['LFRONTBIT'],self.state['LSIDEBIT'],self.state['RFRONTBIT'],self.state['RSIDEBIT'])
        packet_dict['accel'] = struct.pack('<6f',
					   self.state["PitchInDegrees"],
                		           self.state["RollInDegrees"],
            				   self.state["XInG"],
                			   self.state["YInG"],
                 			   self.state["ZInG"],
                			   self.state["SumInG"] )
        if use_pickle:
            self.serialized_packet = pickle.dumps(packet_dict)
        else:
            # experimenting with sending battery voltage to MATLAB
            self.serialized_packet = packet_dict['accel'] + \
                                     packet_dict['motors'] + \
                                     packet_dict['digitalsensors'] + \
                                     packet_dict['ldsscanranges'][1] + \
                                     struct.pack('<1H', self.state['BatteryVoltage']) + \
                                     struct.pack('<1H', self.state['FuelPercent'])

    def getMotors(self):
        """ Update values for motors in the self.state dictionary.
            Returns current left, right encoder values. """
        #self.port.send("getmotors\r\n")
        # for now we will rely on the raspberry pi to request motors by itself
        if 'getmotors' in self.response_dict:
            line = self.response_dict['getmotors']

            if line.find('Unknown Cmd') != -1:
                # something weird happened bail
                raise IOError('Get Motors Failed')
            listing = [s.strip() for s in line.splitlines()]
            for i,l in enumerate(listing):
                if l.startswith('Parameter,Value'):
                    listing = listing[i+1:]
                    break
            for i in range(len(listing)):
                try:
                    values = listing[i].split(',')
                    self.state[values[0]] = int(values[1])
                except Exception as inst:
                    print("exception!")
                    pass
        else:
            print("failed to get odometry information")
        return [self.state["LeftWheel_PositionInMM"],self.state["RightWheel_PositionInMM"]]

    def getAnalogSensors(self):
        if 'getanalogsensors' in self.response_dict:
            line = self.response_dict['getanalogsensors']
            if line.find('Unknown Cmd') != -1:
                raise IOError('Get Analog Sensors Failed')

            listing = [s.strip() for s in line.splitlines()]
            for i in range(len(listing)-1):
                try:
                    values = listing[i+1].split(',')
                    self.state[values[0]] = int(values[2])
                except:
                    pass

    def getCharger(self):
        if 'getcharger' in self.response_dict:
            line = self.response_dict['getcharger']
            if line.find('Unknown Cmd') != -1:
                raise IOError('Get Charger Failed')
            listing = [s.strip() for s in line.splitlines()]
            for i in range(len(listing)-1):
                try:
                    values = listing[i+1].split(',')
                    self.state[values[0]] = int(values[1])
                except:
                    pass


    def getAccel(self):
        """ Update values for motors in the self.state dictionary.
            Returns current left, right encoder values. """
        #self.port.flushInput()
        #self.port.send("getaccel\r\n")
        if 'getaccel' in self.response_dict:
            line = self.response_dict['getaccel']
        
            if line.find('Unknown Cmd') != -1:
                # something weird happened bail
                raise IOError('Get Accel Failed')
            listing = [s.strip() for s in line.splitlines()]

            for i,l in enumerate(listing):
                if l.startswith('Label,Value'):
                    listing = listing[i+1:]
                    break

            for i in range(len(listing)):
                try:
                    values = listing[i].split(',')
                    self.state[values[0]] = float(values[1])
                except Exception as inst:
                    pass
        else:
            pass

        return [self.state["PitchInDegrees"],
                self.state["RollInDegrees"],
                self.state["XInG"],
                self.state["YInG"],
                self.state["ZInG"],
                self.state["SumInG"]]

    def getDigitalSensors(self):
        """ Update values for digital sensors in the self.state dictionary. """
        #self.port.send("getdigitalsensors\r\n")
        # for now we will let the raspberry pi request the digital sensors by itself
        if 'getdigitalsensors' in self.response_dict:
            line = self.response_dict['getdigitalsensors']

            if line.find('Unknown Cmd') != -1:
                # something weird happened bail
                raise IOError('Get Digital Sensors Failed')

            listing = [s.strip() for s in line.splitlines()]
            for i in range(len(listing)-1):
                try:
                    values = listing[i+1].split(',')
                    self.state[values[0]] = int(values[1])
                except:
                    pass
        else:
            pass
        return [self.state['LFRONTBIT'],self.state['LSIDEBIT'],self.state['RFRONTBIT'],self.state['RSIDEBIT']]


    def getScanRanges(self):
        """ Read values of a scan -- call requestScan first! """
        ranges = list()
        intensities = list()
        if 'getldsscan' not in self.response_dict:
            return ([],[])

        try:
            remainder = ""
            line = self.response_dict['getldsscan']
            if line.find('Unknown Cmd') != -1:
                # something weird happened. bail.
                pass
            listing = [s.strip() for s in line.splitlines()]

            for i in range(len(listing)):
                entry = listing[i]
                if entry.startswith('AngleInDegrees') and (len(listing)-1>i or line.endswith('\n')):
                    listing = listing[i+1:]
                    break

            for i in range(len(listing)):
                entry = listing[i]
                vals = entry.split(',')
                try:
                    a = int(vals[0])
                    r = int(vals[1])
                    intensity = int(vals[2])
                    if len(ranges) > a:
                        # got a value we thought we lost
                        ranges[a] = r/1000.0
                        intensities[a] = intensity
                    else:
                        ranges.append(r/1000.0)
                        intensities.append(intensity)
                except:
                    ranges.append(0.0)
                    intensities.append(0.0)
                    # should not happen too much... debug if it does
                    pass
                if len(ranges) >= 360:
                    return NeatoSensorPacket.filter_outliers(ranges, intensities)

            return NeatoSensorPacket.filter_outliers(ranges, intensities)
        except Exception as inst:
            return ([],[])        

    @staticmethod
    def filter_outliers(ranges,intensities):
        # debug: turn off filtering for now
        #return (ranges,intensities)
        if len(ranges) == 0:
            return (ranges,intensities)
        # filter out lone detections
        for i in range(len(ranges)):
            previous = (i-1)%len(ranges)
            next = (i+1)%len(ranges)
            if (ranges[previous] == 0 and ranges[next] == 0) or intensities[i] < 10:
                ranges[i] = 0.0
                intensities[i] = 0.0
        # filter out ranges that are too long or too short
        for i in range(len(ranges)):
            if ranges[i] < .2 or ranges[i] > 5.0:
                ranges[i] = 0.0
                intensities[i] = 0.0
        return (ranges,intensities)
 
