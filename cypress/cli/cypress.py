
import usb.core
import usb.util
from array import array
from random import randint
import cmd, sys

class CypressError(Exception):
    """Base class for other exceptions"""
    pass 

class CypressWriteRequestError(CypressError):
    """Raised if an USB write error occours"""
    pass

class CypressReadResponseError(CypressError):
    """Raised if an USB read error occours"""
    pass

class CypressOpcError(CypressError):
    """Raised for wrong operation code"""
    pass

class CypressSeqError(CypressError):
    """Raised for response wrong sequence number"""
    pass

class Cypress():

    def __init__(self):
        self.opc_rd = 0x20
        self.opc_wr = 0x10
        self.ep_rd = (6 | 128)
        self.ep_wr = 2
        self.ep_data = (8 | 128)
        self.dev = None

    def open(self, index):
        self.lst = list(usb.core.find(idVendor=0x04b4, idProduct=0x8613, find_all=True))

        try:
           self.dev = self.lst[index]
        except Exception as e:
          print("ERROR: Cypress device not found")
          sys.exit(1)
        else:
           self.dev.set_configuration(1)
           self.dev.set_interface_altsetting(interface = 0, alternate_setting = 1)

    def busclear(self):
        while True:
            try:
                data = self.dev.read(self.ep_rd, 1)
            except usb.core.USBError as e:
                break

    def readmem(self, addr):
        wrbuf = array('B')
        wrbuf.append(self.opc_rd)
        seq = randint(1,15)
        wrbuf.append(seq)
        wrbuf.append((addr & 0xFF00) >> 8)
        wrbuf.append(addr & 0x00FF)

        wrbuf[0], wrbuf[1] = wrbuf[1], wrbuf[0]
        wrbuf[2], wrbuf[3] = wrbuf[3], wrbuf[2]

        # write request
        try:
            self.dev.write(self.ep_wr, wrbuf)
        except:
            raise CypressWriteRequestError("Cypress error sending READ(addr) request")

        # read response
        try:
           rdbuf = self.dev.read(self.ep_rd, 4)
        except:
           raise CypressReadResponseError("Cypress error receiving READ(addr) response")

        rdbuf[0], rdbuf[1] = rdbuf[1], rdbuf[0]
        rdbuf[2], rdbuf[3] = rdbuf[3], rdbuf[2]

        if(rdbuf[0] != self.opc_rd):
            raise CypressOpcError("Cypress op code error in WRITE(addr,val) response")

        if(rdbuf[1] != seq):
            raise CypressSeqError("Cypress seq number error in WRITE(addr,val) response")

        value = rdbuf[3] + (rdbuf[2] << 8)

        return(value)

    def writemem(self, addr, value):
        wrbuf = array('B')
        wrbuf.append(self.opc_wr)
        seq = randint(1,15)
        wrbuf.append(seq)
        wrbuf.append((addr & 0xFF00) >> 8)
        wrbuf.append(addr & 0x00FF)
        wrbuf.append((value & 0xFF00) >> 8)
        wrbuf.append(value & 0x00FF)

        wrbuf[0], wrbuf[1] = wrbuf[1], wrbuf[0]
        wrbuf[2], wrbuf[3] = wrbuf[3], wrbuf[2]
        wrbuf[4], wrbuf[5] = wrbuf[5], wrbuf[4]

        # write request
        try:
            self.dev.write(self.ep_wr, wrbuf)
        except:
            raise CypressWriteRequestError("Cypress error sending WRITE(addr,val) request")

        # read response 
        try:
            rdbuf = self.dev.read(self.ep_rd, 4)
        except:
            raise CypressReadResponseError("Cypress error receiving WRITE(addr,val) response")

        rdbuf[0], rdbuf[1] = rdbuf[1], rdbuf[0]

        if(rdbuf[0] != self.opc_wr):
            raise CypressOpcError("Cypress op code error in WRITE(addr,val) response")

        if(rdbuf[1] != seq):
            raise CypressSeqError("Cypress seq number error in WRITE(addr,val) response")

    def readhist(self):
        rdhist = array('B')
        # read histogram
        try:
           rdhist = self.dev.read(self.ep_data, 1024)
        except Exception as e:
           #print(e)
           raise CypressReadResponseError("Cypress error receiving histogram data")

        return(rdhist)

class CypressShell(cmd.Cmd):
    intro = 'Welcome to Cypress USB shell.   Type help or ? to list commands.\n'
    prompt = '(cy) '
    file = None

    cy = Cypress()
    
    def open(self, index):
       try:
          self.cy.open(index)
       except Exception as e:
          print(str(e))
       else:
          self.cy.busclear()

    def do_load(self, arg):
        'Playback commands from a file: LOAD play.cmd'
        try:
            f = open(arg)
        except Exception as e:
            print(str(e))
        else:
            with f:
                self.cmdqueue.extend(f.read().splitlines())

    def do_bye(self, arg):
        'Exit from shell'
        print('Thank you for using Cypress USB')
        return True

    def do_read(self, arg):
        'Send a READ command to Cypress: READ <addr> (addr in hexadecimal)'
        param = self.parse(arg)
        if(len(param)):
            try:
                addr = int(param[0], 16)
            except Exception as e:
                print(str(e))
            else:
                try:
                    value = self.cy.readmem(addr)
                except CypressError as e:
                    print(str(e))
                else:
                    print("READ address(0x%04X" % addr + ") = " + "0x%04X" % value)

    def do_write(self, arg):
        'Send a WRITE command to Cypress: WRITE <addr> <value> (addr, value in hexadecimal)'
        param = self.parse(arg)
        if(len(param) >= 2):
            try:
                addr = int(param[0], 16)
                value = int(param[1], 16)
            except Exception as e:
                print(str(e))
            else:
                try:
                    self.cy.writemem(addr, value) 
                except CypressError as e:
                    print(str(e))
                else:
                    print("WRITE address(0x%04X" % addr + ") with value(0x%04X" % value + ") DONE")

    def do_hist(self, arg):
        'READ histogram from FPGA: hist'
        rdsize = 0
        self.cy.writemem(0x0002, 0x0001)	 # generate histogram
        while True:
           try:
               hist = self.cy.readhist()
               rdsize += hist.buffer_info()[1] * hist.itemsize
           except CypressError as e:
               print(str(rdsize) + " bytes read" )
               #print(str(e))
               break;

    def emptyline(self):
        None

    def parse(self, arg):
        'Convert a series of zero or more strings to an argument tuple'
        return tuple(map(str, arg.split()))
