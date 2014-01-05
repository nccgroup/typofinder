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


def dowhois(sServer, sDomain):
    s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    s.connect((sServer , 43))
    query = sDomain + '\r\n'
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
    # TODO, add more whois servers for other TLDs

    sLDot = sDomain.rfind(".")
    tld = sDomain[sLDot:]

    sServer = ''

    if tld == ".com" or tld == '.org' or tld == ".net":
        sServer = 'whois.internic.net'
    elif tld ==".uk":
        sServer = 'whois.nic.uk'
    elif tld ==".de":
        sServer = 'whois.denic.de'
    else:
        return "Nowt"

    try:
        for sLine in dowhois(sServer,sDomain).split('\n'):
            if "Whois Server: " in sLine:
                sServer = sLine.lstrip(' ')[14:]
    except:
        pass

    return dowhois(sServer,sDomain)
    