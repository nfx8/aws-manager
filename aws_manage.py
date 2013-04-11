'''
============
aws manager
============

1. all you need is an AWS account

2. then with pip install:
* fabric
* boto

uses boto and fabric to easily manage aws instances

============
further info
============

standard ssh login works like this
#ssh -i mykey.pem ec2-user@ec2-23-20-241-197.compute-1.amazonaws.com


you might want to redirect port 80 to 8080 like this
#redirect port
#iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
'''

import os

from boto import ec2
import mysettings
from local_settings import *
from pprint import pprint

from fabric.api import env
from fabric.api import sudo, run, put
from fabric.exceptions import NetworkError

from fabric.api import *
from time import sleep

import argparse
import getopt
import sys
import time

import sys

try:
    from mysettings import AWS
    from mysettings import APP
    from mysettings import github_user
except:
    print """Error: You need to create a myettings.py file
                 with your amazon secret variables!"""
    sys.exit(1)

appname = 'app.py'
remote_dir = '/home/ec2-user/'



def create_instance():
    """ Create an Amazon Instance """
    print 'firing up an instance'
    ec2conn = get_conn()
    reservation = ec2conn.run_instances( **mysettings.SERVER)
    print reservation
    instance = reservation.instances[0]
    time.sleep(1)
    while instance.state != 'running':
        time.sleep(5)
        instance.update()
        print "Instance state: %s" % (instance.state)
        
    # Sleep for a bit more before trying to connect
    print 'waiting some more to initalize'
    time.sleep(60) 

    print "instance %s done!" % (instance.id)

    return instance    



def set_env(ipa):
    env.hosts = [ipa] 
    env.user = 'ec2-user'
    env.key_filename = mysettings["AWS"]["keypath"]
    env.host_string = "ec2-user@%s" % (ipa) 
    #hs = 'ec2-107-20-62-157.compute-1.amazonaws.com'
    #env.host_string = "ec2-user@%s" % (hs) 
    

def install_web(ipa):
    set_env(ipa)
    
    remote_dir = '/home/ec2-user/'
    
    sudo('curl -O http://pypi.python.org/packages/source/p/pip/pip-1.0.tar.gz')
    run('tar xvfz pip-1.0.tar.gz')

    sudo('cd pip-1.0 && python setup.py install')

    #sudo('pip install flask-bootstrap')

    # start nginx
    #sudo('yum install -y git nginx')

    #put('nginx.conf', '/etc/nginx/', use_sudo=True)
    #sudo('service nginx start')

    put('requirements.txt', remote_dir)
    sudo('pip install -r %s/requirements.txt' % (remote_dir))

    #pip install 
    #sudo yum install numpy
    
    put(appname,remote_dir)




def checkout_github():    
    '''
    # Code from GitHub
    github_fingerprint = "github.com,ABC ssh-rsa ..."

    sudo(""" echo '%s' >> .ssh/known_hosts """ % github_fingerprint , pty=True)
    put("ssh-config", ".ssh/config", mode=0600)
    put('keys/deploy_key', '.ssh/', mode=0600)
    run('git clone github:%s %s' % (settings.REPO, remote_code_dir) )
    '''


def runapp(instance):
    ''' run the python app on the AWS server '''
    set_env(ipa)
    #redirect 8080 to 80
    sudo('iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080')
    sudo('nohup python ' + mysettings['APP']['appname'] + ' >& /dev/null < /dev/null &')
    

def copy(ipa,from_file,to_dir=None):
    ''' copy the app and run it '''
    set_env(ipa)
    remote_dir = '/home/ec2-user/'
    if to_dir:
        remote_dir+=to_dir

    #put(localwd + appname,remote_dir + 'showcase/' + appname)
    #return

    #appdir = localwd + '/app'
    #sudo('rm -if ' + appdir)

    put(from_file,remote_dir)



def get_conn():
    ec2conn = ec2.connection.EC2Connection(mysettings.AWS['secrets']['aws_key'], mysettings.AWS['secrets']['aws_secret'])
    return ec2conn

def get_instances():
    ec2conn = get_conn()
    reservations = ec2conn.get_all_instances()
    instances = [i for r in reservations for i in r.instances]
    return instances

def showInstances():   
    ''' show running instances ''' 
    instances = get_instances()

    ips = list()

    for i in instances:
        d = i.__dict__
        #pprint(i.__dict__)
        if i.state=='running':
            print d['ip_address'],d['dns_name']
            #print ('AWS instance %s * ip %s * launched at %s'%(d['dns_name'],d['ip_address'],d['launch_time']))
            ips.append(d['ip_address'])
        
    print ('number of instances %i'%len(ips))
    #rs = ec2conn.get_all_security_groups()
    #print ('security groups')
    #print (rs)


def get_ips():
    ''' get ips of all running instances '''
    instances = get_instances()

    ips = list()

    for i in instances:
        d = i.__dict__
        if i.state=='running':
            ips.append(d['ip_address'])
        
    return ips


def get_single_ip():
    ''' get the ip of your running instance '''
    ips = get_ips()
    if len(ips)!=1: raise ValueError

    return ips[0]


def installhello():
    ips = get_ips()
    if len(ips)!=1: return

    ip = ips[0]
    deploy_web(ip)
    


def stop_all():
    ''' stop all instances '''
    ec2conn = get_conn()
    instances = get_instances()
    for instance in instances:
        iid = instance.__dict__['id']
        print 'deleting ',iid
        
        while instance.state == 'running':
            ec2conn.terminate_instances(instance_ids=[iid])
            time.sleep(5)
            instance.update()
            print "Instance state: %s" % (instance.state)


if __name__=='__main__':

    try:
        optlist, args = getopt.getopt(sys.argv[1:], '')

        if args[0]=='show':
            print 'showing instances'
            showInstances()
        elif args[0]=='create':
            create_instance()
        elif args[0]=='printip':
            get_ip_running()
        elif args[0]=='stop':
            stop_all()
        elif args[0]=='install':
            ips = get_ips()
            if len(ips)==1:
                install_web(ips[0])
        elif args[0]=='run':
            ipa = get_single_ip()
            instances = get_instances()
            #runapp(ipa)
            runapp(instances[0])
        elif args[0]=='sudo':
            ipa = get_single_ip()
            instances = get_instances()
            set_env(ipa)
            sudo(args[1])
        elif args[0]=='copy':
            ipa = get_single_ip()            
            if args[1]:          
                print 'copying %s using ip %s'%(args[1],ipa)
                copy(ipa,args[1])



    except getopt.GetoptError as err:
        #usage()
        sys.exit(2)

