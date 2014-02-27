#
# Typofinder for domain typo discovery
# 
# Released as open source by NCC Group Plc - http://www.nccgroup.com/
# 
# Simple whois query function
# 
# Based on RFC3912
# 
# Developed by Matt Summers, matt dot summers at nccgroup dot com
#
# http://www.github.com/nccgroup/typofinder
#
# Released under AGPL see LICENSE for more information#
#

import socket
import codecs

tld_to_whois = dict()

def dowhois(sServer, sDomain):
    #print ("Whois: " + sDomain + " @ " + sServer)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sServer, 43))
    query = str(codecs.encode(sDomain, "idna"), "ascii") + '\r\n'
    s.send(query.encode())
    response = ''
        
    while len(response) < 10000:
        block = s.recv(1000).decode()
        if block == '':
            break
        response = response + block
        
    try:
        s.shutdown()
        s.close()
    except:
        pass

    return response

def ourwhois(sDomain):
    sLDot = sDomain.rfind(".")
    tld = sDomain[sLDot:]

    if tld in tld_to_whois:
        sServer = tld_to_whois[tld]
    else:
        sServer = "whois.iana.org"

        try:
            for sLine in dowhois(sServer,tld).split('\n'):
                if "whois:" in sLine:
                    sServer = sLine.lstrip(' ')[14:]
                    tld_to_whois[tld] = sServer
                    break
        except:
            pass

    return recursivewhois(sServer, sDomain)

def recursivewhois(sServer, sDomain):
    result = dowhois(sServer,sDomain)

    try:
        for sLine in result.split('\n'):
            if "Whois Server:" in sLine:
                sServer = sLine.lstrip(' ')[14:]
                return recursivewhois(sServer, sDomain)

    except:
        pass

    return result.lstrip()
    