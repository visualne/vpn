from pprint import pprint
from boto import ec2
import os
import re
import ConfigParser

#Left off trying to determine how to interact with mac os to change the server ip address
#to a new elastic ip address of the vm when it is given a new one.
class vpn(object):
# def main():
    def __init__(self):

        #Grabbing credentials
        config = ConfigParser.ConfigParser()
        config.read('credentials.txt')
        AWS_ACCESS_KEY_ID = config.get('Amazon-Creds','aws_access_key_id')
        AWS_SECRET_ACCESS_KEY = config.get('Amazon-Creds','aws_secret_access_key')

        #Getting Credentials

        #Logic here to change public ip address#

        ec2conn = ec2.connection.EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        reservations = ec2conn.get_all_instances()

        #Getting instance associated with the vpn
        vpnInstance = getVPNInstance(reservations)

        #Getting old public ip address
        oldEndpointAddress = getOldEndpoint()

        #Getting new public address
        publicIPAddress = vpnInstance.ip_address

        #Changing public ip address that the vpn is connecting to
        os.system('sed -i -e \'s/' + oldEndpointAddress + '/' + publicIPAddress + '/g\' /Library/Preferences/SystemConfiguration/preferences.plist')
        print 'vpn endpoint changed'


    def getVPNInstance(reservations):
        '''This function gets the instance object that corresponds to the vpn instance'''
        for res in reservations:
            for inst in res.instances:
                if 'Name' in inst.tags:
                    if inst.tags['Name'] == 'vpn':
                        return inst

        return 'sorry there is vm witha  tag of vpn instance'

    def getOldEndpoint():
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


if __name__ == "__main__":
    main()