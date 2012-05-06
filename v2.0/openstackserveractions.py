#!/usr/bin/python
"""
SYNOPSIS

openstackserveractions [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

This script does the following actions on an openstack server:
Create Server
Resize Server
Rebuild Server
Delete Server

EXAMPLES

TODO: Show some examples of how to use this script.

EXIT STATUS

TODO: List exit codes

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

## Pretty Print for Debugging
# import pprint

# Import Help functions for some common tasks
from helpers import send_api_call
from helpers import get_openstack_credentials
from helpers import boot_openstack_server
from helpers import resize_openstack_server

# Basic script boilerplate

def main ():
    
    global options, args
    ### Get OpenStack Credentials
    credentials = get_openstack_credentials()

    apitoken = credentials['apitoken']
    apiurlt = credentials['apiurlt']
#    print apitoken
    # Going to use the CirrOS image that is already installed
    # Please change this if you would like a different image
    # TODO add ability to select other images
    imagename = 'cirros-0.3.0-x86_64-uec'

    # Going to use the m1.tiny flavor
    # Please change this if you would like a different flavor
    # TODO add ability to select other flavors
    flavorname = 'm1.tiny'
    
    # TODO Create Server
    servername = 'myserver'+time.asctime()
    
    myserver = boot_openstack_server(apitoken, apiurlt, servername, imagename, flavorname)
    print json.dumps(myserver, indent=4)
    


    # TODO Resize Server
    # Going to resize an existing server called ResizeMe
    resizeservername = 'ReSizeMe'
    
    # New flavorsize
    resizeflavorname = 'm1.tiny'
    
#    resizeresult = resize_openstack_server(apitoken, apiurlt, resizeservername, resizeflavorname)
#    print json.dumps(resizeresult)
    # TODO Rebuild Server
    # TODO Delete Server



if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(),
                                       usage=globals()['__doc__'], 
                                       version=__version__)
        parser.add_option ('-v', '--verbose', action='store_true', 
                           default=False, help='verbose output')
        (options, args) = parser.parse_args()
        #if len(args) < 1:
        #    parser.error ('missing argument')
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


