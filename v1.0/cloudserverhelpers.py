import sys
from httplib import HTTPException, HTTPSConnection, HTTPConnection
import urllib
import json
import base64
from urlparse import urlparse, urlunparse, urljoin
import time

# Helper Functions

# Calling Cloud Servers and returning the JSON Payload
# 

def send_api_call(parsed, verb, params, headers,debug=False):
    """Calls the Rackspace Cloud API
        
    Establishes a connection.  Sends a message and recieves
    a message. Expects JSON encoding will return JSON.
    
    Args:
    urlr: urlparsed usually the url of the api listener
    verb:  Actions to perform, GET OR PUT
    params: the parameters and calls usually what you want to do
    headers: Usually 
    { "X-Auth-Token":apitoken, "Content-type":"application/json" } 
    with a auth token or {"Content-Type": "application/json"} for without it
    
    Optional Args:
    debug: Default to false otherwise will print out debug info
    Returns:
    A JSON encoded response.
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    # Figure out if connection is https or http and connect to it
    
    if parsed.scheme == 'http':
        conn = HTTPConnection(parsed.netloc)
    elif parsed.scheme == 'https':
        conn = HTTPSConnection(parsed.netloc)
    else:
        raise Exception('Cannot handle protocol scheme %s for url %s' %
                              (parsed.scheme, repr(url)))

    conn.request(verb, parsed.path, params, headers)

    # HTTP response #1

    response = conn.getresponse()
    data = response.read()
 
    dd = None

    # Try to read data if not check for error and die

    if data:
        try:
            dd = json.loads(data)
        except ValueError:
            data = None

    # Add a check for range between 200 and 300 first 
    # for things that don't have a body but are successful
    # otherwise check for error status and die

    if (not data and response.status >= 200 and response.status < 300):
        print 'Success!', response.status, response.reason
        dd = { 
            "response": "Ok", 
            "status": response.status, 
            "reason": response.reason,
            }
    elif not data or response.status < 200 or response.status >= 300:
        print 'http_scheme:', parsed.scheme
        print 'http_host:',conn.host
        print 'http_port:',conn.port
        print 'http_path:', parsed.path
        print 'http_status:', response.status
        print 'http_reason', response.reason
        raise Exception('API Request Failed!', response.status, response.reason)

    if (debug == True):
        print '-' * 10
        print json.dumps(dd, indent=4)
        print '-' * 10

    conn.close()

    # Return response body
    # TODO: also return response status and reason so that
    # functions can handle error codes more gracefully

    return dd
 
# Calling Cloud Servers and fetching credentials and apiurl
# 

def get_credentials(username,apikey):
    """Gets Cloud Servers Credentials for use in further calls
        
    Args:
    username, apikey
    
    Returns:
    A dictonary containing {'apitoken': apitoken, 'apiurlt': apiurlt}
    
    Raises:
    Error when no apitoken and apiurlt returned
    
    """
    
    ### Get Credentials
    
    # arguments
    
    ## make sure that url is set to the actual hostname/IP address,
    ## port number
    ## Change this to match yours
    
    url = "https://auth.api.rackspacecloud.com/v1.1/auth"
    
    # parse the url
    
    urlt = urlparse(url)
    
    # Prepare request for auth token
    
    authrequest = {
    "credentials":{
        "username":username,
        "key":apikey,
        }
    }
    
    # Encode dictonary to a valid json call
    
    params = json.dumps(authrequest)
    
    headers = {"Content-Type": "application/json"}
    
    # Call service

    dd = send_api_call( urlt, "POST", params, headers)
   
    # extract token and url
            
    try:
        apiurl = dd['auth']['serviceCatalog']['cloudServers'][0]['publicURL']
        apitoken = dd['auth']['token']['id']
        apiurlt = urlparse(apiurl)
        return {'apitoken': apitoken, 'apiurlt': apiurlt}
    except:
        print json.dumps(dd, indent=4)
        raise

# Calling Cloud Servers and ask the Compute API server 
# for the image id
# 

def get_image_id(apitoken, apiurlt, imagename):
	

    """Gets CloudServer image references
    
    With the token and the URL we can now ask the CloudServer Compute API 
    server for the image reference
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    imagename: name of the image
    TODO Add option to use imageid instead
    
    Returns:
    A image id
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """

    ### Get Images

    # Setup params and headers
    # no params are sent with this call
    
    params = urllib.urlencode({})
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    # unparsing url to attach /images to the path
    
    unapiurl = urlunparse(apiurlt)
    
    url = "%s/images" % unapiurl
    
    # reparse to send back in
    
    urlt = urlparse(url)
    
    # send the api request
    
    dd = send_api_call(urlt, "GET", params, headers)

    # extract id
    # find the image name
    
    imageid = None
    for index in dd['images']:
        if (index['name'] == imagename):
            imageid =  index['id']
    
    # If no image id found exit

    if (imageid is None):
        sys.exit("Image not found! Try again.")
    else:
        return imageid
        
# Calling Cloud Servers and ask the Compute API server for the flavor reference
# 

def get_flavor_id(apitoken, apiurlt, flavorname):
    """Gets Cloud Server flavor id
        
    With the token and the URL we can now 
    ask the Cloud Server Compute API server for the flavor id
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    flavorname: name of the flavor
    
    Returns:
    An image id
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    ### Get Flavors
 
    # Setup params and headers
    # no params are sent with this call
    
    params = urllib.urlencode({})
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }

    # unparsing url to attach /images to the path
    
    unapiurl = urlunparse(apiurlt)
    
    url = "%s/flavors" % unapiurl
    
    # reparse to send back in
    
    urlt = urlparse(url)
    
    dd = send_api_call(urlt, "GET", params, headers)

    # extract id
    # find the flavor id
    
    flavorid = None
    for index in dd['flavors']:
        if (index['name'] == flavorname):
            flavorid = index['id']

    # If no flavor id found exit

    if (flavorid is None):
        sys.exit("Flavor not found! Try again.")
    else:
        return flavorid

# Calling Cloud Servers and ask the Compute API server for the server id
# 

def get_server_id(apitoken, apiurlt, servername, servercheck=False):
    """Gets Cloud Server id
    
    With the token and the URL we can now ask the Cloud Server Compute API 
    for the server id
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    servername: name of the server
    servercheck: If true script won't exit. Useful for checking to see 
    if server exists
    
    Returns:
    A server id
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    ### Get Servers

    # Setup params and headers
    # no params are sent with this call  
    
    params = urllib.urlencode({})
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    # unparsing url to attach /servers to the path
    
    unapiurl = urlunparse(apiurlt)
    
    url = "%s/servers" % unapiurl
    
    # reparse to send back in
    
    urlt = urlparse(url)
    
    dd = send_api_call(urlt, "GET", params, headers)

    # extract id
    # find the server ids
    
    serverid = None
    for index in dd['servers']:
        if (index['name'] == servername):
            serverid = index['id']
    
    # If no server id found exit

    if (serverid is None):
        
        # if checking for server and it doesn't exist retun false
        # if not checking exit since script expect to recieve an id for use
        
        if (servercheck is True):
            return False
        else:
            sys.exit("Server not found! Try again.")
    else:
        return serverid

# Calling Cloud Servers and ask the Compute API server to boot a new server
# 

def boot_server(apitoken, apiurlt, sname, imagename, flavorname):
    """Boot a Cloud Server e.g. create a new server
    
    With the token and the URL we can now ask the CloudServers Compute API 
    for a new server
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    imagename: name of the image
    flavorname: name of the flavor
    
    Returns:
    A JSON encoded response.
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """

    # Get Servers Image Id
    
    sImageId = get_image_id(apitoken, apiurlt, imagename)

    # Get Servers Flavors Id
    
    sFlavorId = get_flavor_id(apitoken, apiurlt, flavorname) 

    # Server Metadata
    # Leaving blank for now
    
    sMetadata = {}
    
    # Server Personalization
    # Leaving blank for now
    
    sPersonalityPath = ""
    sPersonalityContents = ""
    sPersonality = [ { "path": sPersonalityPath, 
                    "contents": base64.b64encode( sPersonalityContents ) } ]
    
    # Check to see if the name already exist if so append time stamp
    # and let user know
    
    if (get_server_id(apitoken, apiurlt, sname, servercheck=True)):
        print 'Name already exists... Changing name...'
        sname = sname + repr(time.time())
    
    # Call Cloud Server Compute API to create a new server

    s = { 
    "server": { 
        "name": sname, 
        "imageId": sImageId, 
        "flavorId": sFlavorId, 
        "metadata": sMetadata, 
        "personality": sPersonality,
        } 
    }

    # Encode dictonary to a valid json call
    
    sj = json.dumps(s)            

    # unparsing url to attach /images to the path

    unapiurl = urlunparse(apiurlt)
    
    url = "%s/servers" % unapiurl
    
    # reparse to send back in
            
    urlt = urlparse(url)

    params = sj
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    dd = send_api_call(urlt, "POST", params, headers)

    # extract id
    # find the server ids

    try:
        serverid = dd['server']['id']
    except ValueError:
        print "Server create was unsuccessful! Try again."
        raise
    
    return dd

# Calling Cloud Servers and ask the Compute API server to resize server
# 

def resize_server(apitoken, apiurlt, serverid, flavorname):
    """Resizes a Cloud Server e.g. resize a server
    
    With the token and the URL we can now ask the CloudServers Compute API 
    for a server resize
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    serverid: id of server
    flavorname: name of the flavor
    
    Returns:
    True or False
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    # Get Servers Flavors Id
    
    sFlavorId = get_flavor_id(apitoken, apiurlt, flavorname) 

    
    # Call Cloud Server Compute API to resize server
    
    s = { 
    "resize": { 
        "flavorId": sFlavorId, 
        } 
    }
    
    # Encode dictonary to a valid json call
    
    sj = json.dumps(s)            
    
    # unparsing url to attach /images to the path

    unapiurl = urlunparse(apiurlt)
    
    url = "%s/servers/%s/action" % (unapiurl, serverid)
    
    # reparse to send back in
            
    urlt = urlparse(url)
    
    params = sj
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }

    dd = send_api_call(urlt, "POST", params, headers)
  
    return dd

# Calling Cloud Servers and ask the Compute API server to rebuild server
# 

def rebuild_server(apitoken, apiurlt, serverid, imagename):
    """Reimages a Cloud Server e.g. rebuild a server
    
    With the token and the URL we can now 
    ask the CloudServers Compute API for a server rebuild
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    serverid: id of server
    imagename: name of the flavor
    
    Returns:
    True or False
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    # Get Servers Flavors Id
    
    sImageId = get_image_id(apitoken, apiurlt, imagename) 
    
    
    # Call Cloud Server Compute API to resize server
    
    s = { 
    "rebuild": { 
        "imageId": sImageId, 
        } 
    }
    
    # Encode dictonary to a valid json call
    
    sj = json.dumps(s)            
    
    # unparsing url to attach /images to the path

    unapiurl = urlunparse(apiurlt)
    
    url = "%s/servers/%s/action" % (unapiurl, serverid)
    
    # reparse to send back in
            
    urlt = urlparse(url)
    
    params = sj
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    dd = send_api_call(urlt, "POST", params, headers)

    return dd

# Calling Cloud Servers and ask the Compute API server to reboot a server
# 

def reboot_server(apitoken, apiurlt, serverid, reboottype):
    """Reboots a Cloud Server e.g. reboot a server
    
    With the token and the URL we can now ask the CloudServers Compute API 
    for a server reboot
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    serverid: id of server
    
    Returns:
    True or False
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """

    # Call Cloud Server Compute API to reboot server
    
    s = { 
    "reboot": { 
        "type": reboottype, 
        } 
    }
    
    # Encode dictonary to a valid json call
    
    sj = json.dumps(s)            
    
    # unparsing url to attach /images to the path

    unapiurl = urlunparse(apiurlt)
    
    url = "%s/servers/%s/action" % (unapiurl, serverid)
    
    # reparse to send back in
            
    urlt = urlparse(url)
    
    params = sj
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    dd = send_api_call(urlt, "POST", params, headers)
    
    return dd


# Calling Cloud Servers and ask the Compute API server for the flavor reference
# 

def list_servers(apitoken, apiurlt):
    """List all Cloud Servers
    
    With the token and the URL we can now ask the Cloud Server Compute API 
    for a list of servers
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    
    Returns:
    A JSON encoded response.
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    ### List Servers
    
    params = urllib.urlencode({})
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    # unparsing url to attach /servers to the path
    
    unapiurl = urlunparse(apiurlt)
    
    url = "%s/servers/detail" % unapiurl
    
    # reparse to send back in
    
    urlt = urlparse(url)
    
    dd = send_api_call(urlt, "GET", params, headers)
    
    return dd

# Calling Cloud Servers and ask the Compute API to delete a server
# 

def delete_server(apitoken, apiurlt, serverid ):
    """Delete a Cloud Servers
    
    With the token and the URL we can now 
    ask the Cloud Server Compute API server to delete a servers
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    serverid: id of server
    
    Returns:
    A JSON encoded response.
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    ### Delete Server
    
    params = urllib.urlencode({})
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    # unparsing url to attach /servers to the path
    
    unapiurl = urlunparse(apiurlt)
    
    url = "%s/servers/%s" % (unapiurl, serverid)
    
    # reparse to send back in
    
    urlt = urlparse(url)
    
    dd = send_api_call(urlt, "DELETE", params, headers)
    
    return dd

# confirm function
# Source: http://code.activestate.com/recipes/541096-prompt-the-user-for-confirmation/

def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
        False for no.
        
        'resp' should be set to the default value assumed by the caller when
        user simply types ENTER.
        
        >>> confirm(prompt='Create Directory?', resp=True)
        Create Directory? [y]|n: 
        True
        >>> confirm(prompt='Create Directory?', resp=False)
        Create Directory? [n]|y: 
        False
        >>> confirm(prompt='Create Directory?', resp=False)
        Create Directory? [n]|y: y
        True
        
        """
    
    if prompt is None:
        prompt = 'Confirm'
    
    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
    
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

