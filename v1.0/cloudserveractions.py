#!/usr/bin/python
"""
SYNOPSIS

cloudserveractions create|resize|rebuild|reboot|delete|list username apikey 

Optional
[-s,--servername] [-i, --imagename] [-f, --flavorname]
[-d,--serverid] [-r,--reboottype]
[-h,--help] [-v,--verbose] [--version]

DESCRIPTION

This script does the following actions on an rackspace cloud server:
Create Server - Creates a new server if no options are entered will use defaults
Resize Server - Resizes a server requires a server id
Rebuild Server - Rebuilds a server requires a server id
Reboot Server - Reboots a server requires a server id
Delete Server - Deletes a server requires a server id
List Servers - Lists all servers usefull for getting server ids


EXAMPLES

>>python cloudserveractions.py create username 12312321312 --servername=test --imagename=imagename --flavorname=m1.tiny   
>>python cloudserveractions.py resize username 1231212312323423421312 --serverid=1234 --flavorname="512 server"  
>>python cloudserveractions.py reboot username 1231212312323423421312 --serverid=1234 --reboottype=hard
>>python cloudserveractions.py rebuild username 1231212312323423421312 --serverid=1234 --imagename='Ubuntu 11.10'
>>python cloudserveractions.py delete username 1231212312323423421312 --serverid=1234
>>python cloudserveractions.py list username 1231212312323423421312    


EXIT STATUS

TODO: List exit codes

Script assumes server is active.  If sever is not active or unavailable, 
will return api error response and code

AUTHOR

Juan Montemayor <jam1@alum.mit.edu>

LICENSE

This script is in the public domain, free from copyrights or restrictions.

VERSION

1.0.1

"""

__version__ = "1.0.1"

import urllib
import httplib
import json
import os
from urlparse import urlparse
import sys, os, traceback, optparse
import time
import re

# Import Help functions for some common tasks
from cloudserverhelpers import get_credentials, confirm
from cloudserverhelpers import boot_server, resize_server, list_servers
from cloudserverhelpers import reboot_server, rebuild_server, delete_server


def main ():
    
    global options, args
  
    action = args[0]
    username = args[1]
    apikey = args[2]

    ### Get OpenStack Credentials
    credentials = get_credentials(username,apikey)

    apitoken = credentials['apitoken']
    apiurlt = credentials['apiurlt']

    # if no servername provide use a test name
    if options.servername is None:
        servername = 'myserver'+ repr(time.time())
    else:
        servername = options.servername

    # if no imagename provide use Ubuntu 10.04 LTS
    if options.imagename is None:
        imagename = 'Ubuntu 10.04 LTS'
    else:
        imagename = options.imagename

    # if no flavorname provide use 256 server
    if options.flavorname is None:
        flavorname = '256 server'
    else:
        flavorname = options.flavorname
    
    ##
    ## Find action to perform and call the api
    ##

    # Create Server
    if action == 'create':

        print 'creating server...'
        myserver = boot_server(
                               apitoken, 
                               apiurlt, 
                               servername, 
                               imagename, 
                               flavorname,
                               )
        
        # print out server details a simple json.dumps will do for now
        print 'Server Successfully created.'
        print 'Please run list server to check for status.'
        print json.dumps(myserver, indent=4)

    # Resize Server
    elif action == 'resize':

        print 'resizing server...'
 
        # Check for server id
        # if no id provided exit
        if options.serverid is None:
            print 'serverid is required for a resize'
        else:      
            myresize = resize_server(
                                   apitoken, 
                                   apiurlt, 
                                   options.serverid, 
                                   flavorname,
                                   )
        
            # print out server details a simple json.dumps will do for now
            print 'Server Successfully Resizing.'
            print 'Please run list server to check for status.'
            print json.dumps(myresize, indent=4)
        
    # TODO: Rebuild Server
    elif action == 'rebuild':

        print 'rebuilding server...'
                
        # Check for server id
        # if no id provided exit
        if options.serverid is None:
            print 'serverid is required for a resize'
        else:      
            myrebuild = rebuild_server(
                                     apitoken, 
                                     apiurlt, 
                                     options.serverid, 
                                     imagename,
                                     )
            
            # print out server details a simple json.dumps will do for now
            print 'Server Successfully Rebuilding.'
            print 'Please run list server to check for status.'
            print json.dumps(myrebuild, indent=4)

    # Reboot Server            
    elif action == 'reboot':

        # if reboot type is not provided
        # perform a soft reboot
        reboottype = 'SOFT'
        
        
        if (options.reboottype is not None 
            and options.reboottype.upper() == 'HARD'):
            reboottype = 'HARD'
 
        print '%s rebooting server...' % reboottype

        
        # Check for server id
        # if no id provided exit
        if options.serverid is None:
            print 'serverid is required for a reboot'
        else:      
            myreboot = reboot_server(
                                     apitoken, 
                                     apiurlt, 
                                     options.serverid, 
                                     reboottype,
                                     )
            
            # print out server details a simple json.dumps will do for now
            print 'Server Successfully Rebooting.'
            print 'Please run list server to check for status.'
            print json.dumps(myreboot, indent=4)

    elif action == 'delete':
        # TODO: Delete Server
        print 'deleting server...'

        # Check for server id
        # if no id provided exit
        if options.serverid is None:
            print 'serverid is required for a delete'
        else:
            # Just in case prompt user for delete confirmation
            if (confirm(prompt='Are you sure you want to delete?',resp=False)):

                mydelete = delete_server(
                                         apitoken, 
                                         apiurlt, 
                                         options.serverid, 
                                         )
                
                # print out server details a simple json.dumps will do for now
                print 'Server Successfully Deleting.'
                print 'Please run list server to check for status.'
                print json.dumps(mydelete, indent=4)

            else:
                print 'Server was NOT deleted'

    # List Server
    elif action == 'list':

        print 'listing servers...'
        allservers = list_servers(apitoken,apiurlt)
        print json.dumps(allservers, indent=4)
    else:
        print 'No valid action found...'

    return True

# Basic script boilerplate for options and error handling
if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(),
                                       usage=globals()['__doc__'], 
                                       version=__version__)
        parser.add_option ('-v', '--verbose', action='store_true', 
                           default=False, help='verbose output')
        parser.add_option ('-s', '--servername', help='the name of the server',
                           dest='servername', action='store')
        parser.add_option ('-d', '--serverid', help='the id of the server',
                           dest='serverid', action='store')
        parser.add_option ('-i', '--imagename', help='the name of the image',
                           dest='imagename', action='store')
        parser.add_option ('-f', '--flavorname', help='the name of the flavor',
                           dest='flavorname', action='store')
        parser.add_option ('-r', '--reboottype', help='the type of reboot',
                           dest='reboottype', action='store')
        (options, args) = parser.parse_args()
        if len(args) < 3:
            parser.error ('missing argument')
        if options.verbose: print time.asctime()
        main()
        if options.verbose: print time.asctime()
        if options.verbose: print 'TOTAL TIME IN MINUTES:',
        if options.verbose: print (time.time() - start_time) / 60.0
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)


