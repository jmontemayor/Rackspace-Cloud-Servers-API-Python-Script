import sys
import httplib
import urllib
import json
import base64
from urlparse import urlparse


# Helper Functions

# Calling Open Stack and returning the JSON Payload
# 

def send_api_call(url, verb, path, params, headers, 
                usehttps=False,debug=False):
    """Calls the OpenStack API
        
    Establishes a connection.  Sends a message and recieves
    a message. Expects JSON encoding will return JSON.
    
    Args:
    url: usually the url of the api listern
    verb:  Actions to perform, GET OR PUT
    path: the resource path
    params: the parameters and calls ususally what you want to do
    headers: Usually 
    { "X-Auth-Token":apitoken, "Content-type":"application/json" } 
    with a auth token or {"Content-Type": "application/json"} for without it
    
    Optional Args:
    usehttps: Default to fales otherwise True for an https a secure connection
    debug: Default to false otherwise will print out debug info
    Returns:
    A JSON encoded response.
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    ## change to False when you are using the test environment

    usehttps = False
    # HTTP connection

    if (usehttps == True):
        # set key_file and cert_file to wherever the key and cert files
        # are located
        conn = httplib.HTTPSConnection(url1, 
                                        key_file='../cert/priv.pem', 
                                        cert_file='../cert/srv_test.crt')
    else:
        conn = httplib.HTTPConnection(url)

    conn.request(verb, path, params, headers)

    # HTTP response #1

    response = conn.getresponse()
    data = response.read()
    dd = json.loads(data)

    if (debug == True):
        print '-' * 10
        print json.dumps(dd, indent=4)
        print '-' * 10

    conn.close()
    return dd

# Calling Open Stack and fetching credentials and apiurl
# 

def get_openstack_credentials():
    """Gets OpenStack Credentials for use in further calls
    
    By default uses the following:
    OpenStack hostname/IP address: 192.168.1.128:5000
    osuser: admin, works for test installs on virtual machines, 
    but it's a hack
    
    Args:
    None, everything hardcoded for this excerise
    TODO allow server and user to be given as options
    
    Returns:
    A dictonary containing {'apitoken': apitoken, 'apiurlt': apiurlt}
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    ### Get OpenStack Credentials
    
    # arguments
    
    ## make sure that url1 is set to the actual hostname/IP address,
    ## port number
    ## Change this to match yours
    
    url = "192.168.2.35:5000"
    
    ## make sure that osuser is set to your actual username, "admin"
    ## works for test installs on virtual machines, but it's a hack
    ## Since I am using DevStack for this it should be fine
    
    osuser = "admin"
    
    ## use something else than "shhh" for you password
    
    ospassword = "test"
    params = ('{"auth":{"passwordCredentials":{"username":"' 
              +osuser 
              + '", "password":"'
              +ospassword
              +'"},"tenantName":"admin"}}')
    
    headers = {"Content-Type": "application/json"}
    
    # Call service
    #( usehttps, url, verb, path, params, headers)
    dd = send_api_call( url, "POST", "/v2.0/tokens", params, headers)
    
        # extract token and url
        # find compute node
    try:    
        for index in dd['access']['serviceCatalog']:
            if (index['type'] == "compute"):
                for urlIndex in index['endpoints']:
                    apiurl =  urlIndex['publicURL']
        
        
        apitoken = dd['access']['token']['id']
        apiurlt = urlparse(apiurl)
        return {'apitoken': apitoken, 'apiurlt': apiurlt}
    except:
        print dd['error']
        raise

# Calling Open Stack and ask the OpenStack Compute API server 
# for the image reference
# 

def get_openstack_image_reference(apitoken, apiurlt, imagename):
	
	try: 
	    """Gets OpenStack server image references
    
	    With the token and the URL we can now 
	    ask the OpenStack Compute API server for the image reference
    
	    Args:
	    apitoken: authenticated access token
	    apiurlt:  server url
	    imagename: name of the image
	    TODO Add option to use imageid instead
    
	    Returns:
	    A dictonary containing {sImageRef: href of image}
    
	    Raises:
	    No real error messages for the moment
	    TODO add expection handling
    
	    """
    
	    ### Get Images
    
	    url = apiurlt.netloc
	    params = urllib.urlencode({})
	    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
	    path = "%s/images" % apiurlt.path
    
	    dd = send_api_call(url, "GET", path, params, headers)

	    # extract url
	    # find the image name
    
	    for index in dd['images']:
	        if (index['name'] == imagename):
	            for urlIndex in index['links']:
	                if (urlIndex['rel'] == 'self'):
	                    imageurl =  urlIndex['href']
    
	    return imageurl
	except: 
		# print "unexpected error: ", sys.exc_info()[0]
		raise

# Calling Open Stack and ask the OpenStack Compute API server 
# for the flavor reference
# 

def get_openstack_flavor_reference(apitoken, apiurlt, flavorname):
    """Gets OpenStack server flavor references
        
    With the token and the URL we can now 
    ask the OpenStack Compute API server for the flavor reference
    
    Args:
    apitoken: authenticated access token
    apiurlt:  server url
    imagename: name of the image
    flavorname: name of the flavor
    
    Returns:
    A dictonary containing {sImageRef: href of image}
    
    Raises:
    No real error messages for the moment
    TODO add expection handling
    
    """
    
    ### Get Flavors
    
    url = apiurlt.netloc
    params = urllib.urlencode({})
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    path = "%s/flavors" % apiurlt.path
    
    dd = send_api_call(url, "GET", path, params, headers)

    # extract url
    # find the flavor name

    for index in dd['flavors']:
        if (index['name'] == flavorname):
#            flavorurl = index['id']
            for urlIndex in index['links']:
                if (urlIndex['rel'] == 'self'):
                    flavorurl =  urlIndex['href']
 
    return flavorurl

# Calling Open Stack and ask the OpenStack Compute API server 
# to get a server ID
# 

def get_openstack_server_id(apitoken, apiurlt, servername):
    """Gets OpenStack server id from name
        
        With the token and the URL we can now 
        ask the OpenStack Compute API server for the server id
        
        Args:
        apitoken: authenticated access token
        apiurlt:  server url
        servername: name of the server
        
        Returns:
        A dictonary containing {sID: serverid}
        
        Raises:
        No real error messages for the moment
        TODO add expection handling
        
        """
    
    ### Get Server
    
    url = apiurlt.netloc
    params = urllib.urlencode({})
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    path = "%s/servers" % apiurlt.path
    
    dd = send_api_call(url, "GET", path, params, headers)
    # extract serverid
    # find the server name

    for index in dd['servers']:
        if (index['name'] == servername):
           serverid = index['id']
    
    return serverid

# Calling Open Stack and ask the OpenStack Compute API server 
# to boot a new server
# 

def boot_openstack_server(apitoken, apiurlt, sname, imagename, flavorname):
    """Boot an OpenStack server e.g. creat a new server
    
    With the token and the URL we can now 
    ask the OpenStack Compute API for a new server
    
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
    
    ##
    ## Get Servers Image Reference
    ##
    
    sImageRef = get_openstack_image_reference(apitoken, apiurlt, imagename)
    
    ##
    ## Get Servers Flavors Reference
    ##
    
    sFlavorRef = get_openstack_flavor_reference(apitoken, apiurlt, flavorname) 
    
    ### Server Metadata
    ### Leaving blank for now
    
    sMetadata = {}
    
    ###
    ### Server Personalization
    ### Leaving blank for now
    ###
    
    sPersonalityPath = ""
    sPersonalityContents = ""
    sPersonality = [ { "path": sPersonalityPath, 
                    "contents": base64.b64encode( sPersonalityContents ) } ]
    
    ###
    ### Call OpenStack Compute API to create a new server
    ###
    print sFlavorRef,sImageRef
    s = { 
    "server": { 
        "name": sname, 
        "imageRef": sImageRef, 
        "flavorRef": sFlavorRef, 
        "metadata": sMetadata, 
        "personality": sPersonality,
        "OS-DCF:diskConfig": "AUTO",
        } 
    }

    # Encode dictonary to a valid json call
    sj = json.dumps(s)            
                    
    url = apiurlt.netloc
    params = sj
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    path = "%s/servers" % apiurlt.path
    
    dd = send_api_call(url, "POST", path, params, headers)
    
    return dd

# Calling Open Stack and ask the OpenStack Compute API server 
# to resize a server
# 

def resize_openstack_server(apitoken, apiurlt, sname, flavorname):
    """Resize an OpenStack server
        
        With the token and the URL we can now 
        ask the OpenStack Compute API for to resize server
        
        Args:
        apitoken: authenticated access token
        apiurlt:  server url
        flavorname: name of the flavor
        
        Returns:
        A JSON encoded response.
        
        Raises:
        No real error messages for the moment
        TODO add expection handling
        
        """
    
    ##
    ## Get Servers Id
    ##
    
    sServerId = get_openstack_server_id(apitoken, apiurlt, sname)
    print "sID", sServerId
    ##
    ## Get Servers Flavors Reference
    ##
    
    sFlavorRef = get_openstack_flavor_reference(apitoken, apiurlt, flavorname) 
    print "sFlavor", sFlavorRef
    ###
    ### Call OpenStack Compute API to resize server
    ###
    s = { 
    "resize": { 
        "Name": sname,
        "flavorRef": sFlavorRef, 
        } 
    }
    
    # Encode dictonary to a valid json call
    sj = json.dumps(s)            
    
    url = apiurlt.netloc
    params = sj
    headers = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
    
    path = "%s/servers/%s/action" % (apiurlt.path, sServerId)
    print "url", url
    print "path", path
    print "params", params
    print "headers", headers
    dd = send_api_call(url, "POST", path, params, headers)
    
    return dd
