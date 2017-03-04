from pprint import pprint
from boto import ec2
import os
import re
import ConfigParser

#Need to allocate elastic IP address. - Done
#Once address is allocated, go into the vm that is spun up and change the configuration in openswan
#to accomodate the new elastic ip address.
#Unassociate address
#Associate new address
#Go into vm, restart the openswan service.

# def main():
class vpn(object):

    def __init__(self):
        #Grabbing credentials
        config = ConfigParser.ConfigParser()
        config.read('credentials.txt')
        AWS_ACCESS_KEY_ID = config.get('Amazon-Creds','aws_access_key_id')
        AWS_SECRET_ACCESS_KEY = config.get('Amazon-Creds','aws_secret_access_key')

        #Logic here to change public ip address#
        self.ec2conn = ec2.connection.EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    def getVPNInstance(self):
        #Getting list of all instances
        reservations = self.ec2conn.get_all_instances()

        #This for loop ultimately determines the vm that is the vpn vm.
        for res in reservations:
            for inst in res.instances:
                if 'Name' in inst.tags:
                    if inst.tags['Name'] == 'vpn':
                        return inst

        return 'sorry there is no tag of vpn on any of these vms.'

    def getOldEndpoint(self):
        '''This function grabs the old vpn endpoint. This can probably go later.'''
        f = open('/Library/Preferences/SystemConfiguration/preferences.plist')

        ip = re.compile('(([2][5][0-5]\.)|([2][0-4][0-9]\.)|([0-1]?[0-9]?[0-9]\.)){3}'
                        +'(([2][5][0-5])|([2][0-4][0-9])|([0-1]?[0-9]?[0-9]))')

        #Need to come up with a better way of getting this ip address later. There might
        #be a library that can easily parse xml.
        ipList = []

        for line in f.readlines():
            match = ip.search(line)
            if match:
                ipList.append(match.group())
        f.close()

        return ipList[-1]

    def disassociateAddress(self):
        '''This method will disassociate the public ip address assocaited with the vm.'''
        pass

    def allocateNewAddress(self):
        '''This function allocates a new public ip address. This address will be used by the new openswan vm.'''
        elasticIP = self.ec2conn.allocate_address()
        return elasticIP

    def changeOpenSwanConfiguration(self):
        '''This method will change'''

if __name__ == "__main__":
    #Creating new vpn object.
    vpnObj = vpn()

    #Getting vpn instance
    vpnInstance = vpnObj.getVPNInstance()

    #Getting old endpoint currently configured in mac os
    oldEndpoint = vpnObj.getOldEndpoint()

    #Getting public ip address associated with with vpn vm.
    publicIPAddress = vpnInstance.ip_address

    #New public ip address
    newPublicIP = vpnObj.allocateNewAddress()

    print 'OldEndpoint in preferences.plist file: ' + oldEndpoint
    print 'Current Public IP Address associated with VM: ' + publicIPAddress
    print 'New public IP address: ' + str(newPublicIP)

    #Changing public ip address that the vpn is connecting to
    # os.system('sed -i -e \'s/' + oldEndpointAddress + '/' + publicIPAddress + '/g\' /Library/Preferences/SystemConfiguration/preferences.plist')
    # print 'vpn endpoint changed'





    # main()