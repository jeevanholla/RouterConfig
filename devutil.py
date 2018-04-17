import telnetlib, socket, time, re, pdb

class Device:

    def __init__(self):
        self.data = {'Ipaddr': None, 'Port': None, 'Username': None, 'Secret': None, 'Hostname': None, 'EnSecret': None}
        self.device = None
        return

    def UpdateDeviceData(self, ipaddr, port=23, username=None, secret=None, en_secret=None):
        if ipaddr != None or ipaddr != '':
            self.data['Ipaddr'] = ipaddr
        if port != self.data['Port']:
            self.data['Port'] = port
        if username != None:
            self.data['Username'] = username
        if secret != None:
            self.data['Secret'] = secret
        if en_secret != self.data['EnSecret']:
            self.data['EnSecret'] = en_secret
        return

    def Connect(self, ipaddr, port=23, update=False):
        if update == True:
            self.UpdateDeviceData(ipaddr, port)
        try:
            device = telnetlib.Telnet(self.data['Ipaddr'], self.data['Port'])
        except socket.error:
            print 'Unable to telnet to %s and %d. So returning with error now' % (ipaddr, port)
            return False

        self.device = device
        time.sleep(5)
        device.write('\n\n')
        return True

    def Login(self, device=None, username=None, secret=None, en_secret=None, update=False):
        if update == True:
            self.UpdateDeviceData(None, None, username, secret, en_secret)
        if device == None:
            device = self.device
        login_info = device.expect(['Username:', 'Password:', '#', '>'], 5)
        dev_prompt = False
        if login_info[0] == 0:
            device.write(self.data['Username'] + '\n')
            device.read_until('Password: ', 5)
            device.write(self.data['Secret'] + '\n')
        else:
            if login_info[0] == 1:
                device.write(self.data['Secret'] + '\n')
            else:
                if login_info[0] == 2:
                    dev_prompt = True
                else:
                    if login_info[0] == 3:
                        pass
                    else:
                        print (
                         login_info[0], login_info)
                        return False
        if dev_prompt == False:
            dev_info = device.expect(['#', '>'], 5)
            if dev_info[0] == 0:
                dev_prompt == True
            elif dev_info[0] == 1:
                device.write('enable\n')
                device.read_until('Password: ')
                device.write(self.data['EnSecret'] + '\n')
                dev_prompt == True
            else:
                device.write('\n\n')
                prompt_now = device.read_until('\n', 5)
                print 'Unable to login into right prompt, so exiting now with %s' % prompt_now
                return False
        device.write('\n')
        dev_prompt = device.read_until('#', 5).strip()
        self.data['Hostname'] = dev_prompt
        return True

    def ExecuteandIgnore(self, device, command):
        device.write(command + '\n')
        ig = device.read_until('#', 2)
        ig += device.read_until('#', 2)

    def Execute(self, device, command):
        device.write('\n')
        ig = device.read_until('#', 2)
        device.write(command + '\n')
        readdata = device.read_until('#', 2)
        readdata += device.read_until('#', 2)
        return readdata
