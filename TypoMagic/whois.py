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
import re

from publicsuffix import PublicSuffixList

#Seed the whois server map with special cases that aren't in our whois-servers.txt list nor returned by iana
#Based on http://www.nirsoft.net/whois-servers.txt
tld_to_whois = dict()

with open("datasources/whois-servers.txt", "r") as whois_servers:
    for line in whois_servers:
        if line.startswith(';'):
            continue
        parts = line.split(' ')
        tld_to_whois['.' + parts[0].strip()] = parts[1].strip()

psl = PublicSuffixList(input_file=codecs.open("datasources/effective_tld_names.dat", "r", "utf8"))

def _dowhois(sServer, sDomain):
    """
    Perform the network connection to the Whois Server and query for the given domain.

    @param sServer: The hostname of the whois server to query.
    @param sDomain: The domain to query for.
    @return: The whois result string.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sServer, 43))
    try:
        query = str(codecs.encode(sDomain, "idna"), "ascii") + '\r\n'
    except:
        query = sDomain + '\r\n'
    s.send(query.encode())
    response = ''
        
    while len(response) < 10000:
        bytes = s.recv(1000)
        try:
            block = bytes.decode("utf-8")
        except:
            block = bytes.decode("iso-8859-1")

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

    result = _recursivewhois(sServer, sDomain)
    #Special case to handle the fuzzy matching at the ICANN whois server
    if 'To single out one record, look it up with "xxx", where xxx is one of the' in result:
        all_domain_records = _dowhois(sServer, '=' + sDomain)
        next_whois_server = extract_field(all_domain_records, "Whois Server").split(', ')[-1]
        return _recursivewhois(next_whois_server, sDomain)
    else:
        return result

def _recursivewhois(sServer, sDomain):
    """
    A recursive whois function which will follow the "Whois Server:" referals.

    @param sServer: The hostname of the whois server to query.
    @param sDomain: The domain to query for.
    @return: The whois result string.
    """
    result = _dowhois(sServer,sDomain)

    try:
        next_whois_server = extract_field(result, "Whois Server")
        if next_whois_server and next_whois_server != sServer:
            return _recursivewhois(next_whois_server, sDomain)
    except:
        pass

    return result.lstrip()

def extract_field(whois_blob, *args):
    result = list()

    if len(args) == 1:
        field_name = args[0]
    else:
        field_name = "(?:"

        field_list = list()
        for arg in args:
            field_list.append("(?:" + arg + ")")

        field_name += "|".join(field_list)
        field_name += ")"

    regex = field_name + r":(?: |\t)*(.+)\n"

    match_list = re.finditer(regex, whois_blob, flags=re.IGNORECASE)
    if match_list:
        for match in match_list:
            if match.group(1):
                value = match.group(1).strip()
                if value:
                    result.append(value)

    return ", ".join(result)
