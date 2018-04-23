
import cmd, sys
from cypress import Cypress, CypressError

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
              print(hist)
           except CypressError as e:
              #print(str(rdsize) + " bytes read" )
              #print(str(e))
              break;
           else:
              rdsize += len(hist)
        print("elements read: {}".format(rdsize))

    def emptyline(self):
        None

    def parse(self, arg):
        'Convert a series of zero or more strings to an argument tuple'
        return tuple(map(str, arg.split()))
