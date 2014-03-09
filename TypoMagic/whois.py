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
from publicsuffix import PublicSuffixList

#Seed the whois server map with special cases that aren't returned by iana
tld_to_whois = {".ac.uk" : "whois.ja.net",
                ".gov.uk" : "whois.ja.net",
                ".br.com" : "whois.centralnic.com",
                ".cn.com" : "whois.centralnic.com",
                ".eu.com" : "whois.centralnic.com",
                ".gb.com" : "whois.centralnic.com",
                ".gb.net" : "whois.centralnic.com",
                ".qc.com" : "whois.centralnic.com",
                ".hu.com" : "whois.centralnic.com",
                ".no.com" : "whois.centralnic.com",
                ".sa.com" : "whois.centralnic.com",
                ".se.com" : "whois.centralnic.com",
                ".se.net" : "whois.centralnic.com",
                ".uk.com" : "whois.centralnic.com",
                ".uk.net" : "whois.centralnic.com",
                ".us.com" : "whois.centralnic.com",
                ".uy.com" : "whois.centralnic.com",
                ".za.com" : "whois.centralnic.com"}
psl = PublicSuffixList()

def _dowhois(sServer, sDomain):
    """
    Perform the network connection to the Whois Server and query for the given domain.

    @param sServer: The hostname of the whois server to query.
    @param sDomain: The domain to query for.
    @return: The whois result string.
    """
    #print ("Whois: " + sDomain + " @ " + sServer)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sServer, 43))
    try:
        query = str(codecs.encode(sDomain, "idna"), "ascii") + '\r\n'
    except:
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
    """
    Entry point for this package, which fetches whois data from the appropriate server.

    @param sDomain: The domain to query whois for.
    @return: The whois result.
    """
    sDomain = psl.get_public_suffix(sDomain)

    sLDot = sDomain.find(".")
    tld = sDomain[sLDot:]

    if tld in tld_to_whois:
        sServer = tld_to_whois[tld]
    else:
        sServer = "whois.iana.org"

        try:
            for sLine in _dowhois(sServer,tld).split('\n'):
                if "refer:" in sLine or "whois:" in sLine:
                    sServer = sLine[6:].lstrip()
                    tld_to_whois[tld] = sServer
                    break
        except:
            pass

    return _recursivewhois(sServer, sDomain)

def _recursivewhois(sServer, sDomain):
    """
    A recursive whois function which will follow the "Whois Server:" referals.

    @param sServer: The hostname of the whois server to query.
    @param sDomain: The domain to query for.
    @return: The whois result string.
    """
    result = _dowhois(sServer,sDomain)

    try:
        for sLine in result.split('\n'):
            if "Whois Server:" in sLine:
                sServer = sLine.lstrip(' ')[14:]
                return _recursivewhois(sServer, sDomain)
    except:
        pass

    return result.lstrip()
