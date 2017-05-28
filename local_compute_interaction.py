import os
import ConfigParser
import subprocess
import time

class lci(object):
    # Connect vpn
    # Disconnect vpn
    # Need to write something to change the endpoint.

    def __init__(self):
        #Grabbing credentials
        self.config = ConfigParser.ConfigParser()
        self.config.read('credentials.txt')

    def getCurrentIP(self):
        cmd = 'curl ipinfo.io/ip'
        currentPublicIP = subprocess.check_output(cmd,shell=True)

        # Returning public ip address
        return currentPublicIP


    def connect_vpn(self):

        # Setting vpn secret key.
        VPN_SECRET_KEY = self.config.get('Vpn-Creds', 'secret_key')

        cmd = """scutil --nc start Amazon --secret """ + VPN_SECRET_KEY
        os.system(cmd)

        # Check

    def disconnect_vpn(self):
        # Write something to disconnect
        cmd = """osascript -e "tell application \"System Events\"" -e "tell current location of network preferences" -e "set VPN to service \"Amazon\"" -e "if exists VPN then disconnect VPN" -e "end tell" -e "end tell"""""
        os.system(cmd)


if __name__ == "__main__":
    lciObj = lci()

    # Getting current public ip address
    originalPublicIPAddress = lciObj.getCurrentIP()

    # Connecting vpn
    lciObj.connect_vpn()

    # Sleeping for three seconds
    time.sleep(5)

    # Loop to check to check for a new IP address over and over again
    while True:
        newIPaddress = lciObj.getCurrentIP()
        if originalPublicIPAddress is not newIPaddress:
            print ' New IP address is: ' + newIPaddress
            break

        #Sleeping for a second and trying again
        time.sleep(2)