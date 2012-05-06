Rackspace-Cloud-Servers-API-Python-Script
=========================================

This script performs some simple actions on a cloud server using the Rackspace API v1.0 and v2.0

=========================================

v1.0/cloudserveractions.py

SYNOPSIS

cloudserveractions create|resize|rebuild|reboot|delete username apikey 

Optional
[-s,--servername] [-i, --imagename] [-f, --flavorname]
[-d,--serverid] [-r,--reboottype]
[-h,--help] [-v,--verbose] [--version]

DESCRIPTION

This script does the following actions on an rackspace cloud server:
Create Server
Resize Server
Rebuild Server
Reboot Server
Delete Server


EXAMPLES

cloudserveractions create username 12312321312 --servername=test --imagename=imagename --flavorname=m1.tiny

EXIT STATUS

TODO: List exit codes

TODO: Script assumes server is active.  
If sever is not active or unavailable, 
will return api error response and code

AUTHOR

Juan Montemayor <jam1@alum.mit.edu>

LICENSE

This script is in the public domain, free from copyrights or restrictions.

VERSION

1.0.1

--------------

v2.0/openstackactions.py

Same as 1.0.  Sill a work in progress

TODO Combine both script into one master script to handle both versions of API
