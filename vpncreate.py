from pprint import pprint
from boto import ec2
import os
import re
import ConfigParser
import ansible.runner
import ansible.playbook
import ansible.inventory
from ansible import callbacks
from ansible import utils
import json


#Problem UDP port 500 not listening after openswan restart for some reason. Need to look into this more.

#Need to allocate elastic IP address. - Done
#Once address is allocated, go into the vm that is spun up and change the configuration in openswan
#to accomodate the new elastic ip address.
#Unassociate address - Done
#Associate new address - Done
#Go into vm, restart the openswan service. - Done

class vpnVMInteraction(object):

    def __init__(self,oldIPAddress):
        #Setting the ansible inventory ip to be the old elastic ip address of the vm.
        self.hosts = [oldIPAddress]
        self.vpn_vm = ansible.inventory.Inventory(self.hosts)


    def runCommand(self,cmd):
        '''This function runs the command that was sent into the function.'''
        pm = ansible.runner.Runner(
            module_name = 'command',
            module_args = cmd,
            timeout = 5,
            inventory = self.vpn_vm,
            subset = 'all',
            remote_user='ubuntu',
            become='yes',
            become_method='sudo'
            )

        out = pm.run()

        print json.dumps(out, sort_keys=True, indent=4, separators=(',', ': '))

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

        #Getting vpn instance object
        self.vpnInstance = self.getVPNInstance()

        #Allocating new public ip address
        self.newElasticIP = self.ec2conn.allocate_address()

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

        # Getting vpn instance
        vpnInstance = self.getVPNInstance()

        #Getting allocation id of current public ip address
        for addr in self.ec2conn.get_all_addresses():
            if addr.public_ip == vpnInstance.ip_address:
                #Disassocating address from VM
                self.ec2conn.disassociate_address(vpnInstance.ip_address)

                #Releasing public IP address
                self.ec2conn.release_address(allocation_id=addr.allocation_id)

    def associateNewAddress(self):
        '''This function associates a new elastic ip address with an instance.'''

        #Associating public ip address with ec2 instance
        self.ec2conn.associate_address(self.vpnInstance.id,self.newElasticIP.public_ip)


if __name__ == "__main__":

    #Getting vpn object
    vpnObj = vpn()

    #Setting up old ip address
    oldIPAddress = vpnObj.vpnInstance.ip_address

    #Get new elastic ip address object
    newIPAddress = vpnObj.newElasticIP

    print 'New IP Address: ' + newIPAddress.public_ip
    print 'Old IP Address: ' + oldIPAddress

    #Sed command to replace public ip in ipsec.conf
    print 'sed -i \'s/^  leftid=.*/  leftid=%s/g\' /etc/ipsec.conf' %newIPAddress.public_ip

    #Sed command to replace public ip in /etc/ipsec.secrets
    print 'sed -i -e \'s/%s\\b/%s/g\' /etc/ipsec.secrets' % (newIPAddress.public_ip,oldIPAddress)

    newVpnObj = vpnVMInteraction(oldIPAddress)

    #Replacing old public ip address in /etc/ipsec.conf
    newVpnObj.runCommand('sed -i \'s/^  leftid=.*/  leftid=%s/g\' /etc/ipsec.conf' %newIPAddress.public_ip)

    #replacing old ip adddress with new ip address in /etc/ipsec.secrets
    newVpnObj.runCommand('sed -i -e \'s/%s\\b/%s/g\' /etc/ipsec.secrets' % (oldIPAddress,newIPAddress.public_ip))

    #restarting openswan
    newVpnObj.runCommand('service ipsec restart')

    # #Disassociating the public ip address associated with an instance.
    vpnObj.disassociateAddress()

    #Associating new ip address to the instance.
    vpnObj.associateNewAddress()