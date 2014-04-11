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
#          and Stephen Tomkinson
#
# http://www.github.com/nccgroup/typofinder
#
# Released under AGPL see LICENSE for more information
#

import socket
import codecs
import re

from publicsuffix import PublicSuffixList
import datetime
import pprint


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
    """
    Extract from the given WHOIS result blob the value that is associated with the given field name.

    @param whois_blob The whois data to search for the value
    @param *args One or more field names (interpreted as regexes) that the requested value may be referred to as.
    """
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
                if value and value != "null":
                    result.append(value)

    return ", ".join(result)

def date_parse(date_string):
    """
    Date parser which attempts to work with a range of date formats.

    @param date_string The string representing a date or date/time.
    @return A datetime object if one could be parsed, or None
    """
    if not date_string:
        return None
    date_string = date_string.replace('T', '')
    date_string = date_string.replace(' ', '')
    date_string = date_string.replace('.', '-')
    date_string = date_string.rstrip('Z')

    for format in ("%Y-%m-%d%H:%M:%S", "%Y-%m-%d%H:%M:%S%z", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(date_string, format)
        except ValueError:
            #Attempt the next format
            continue
    return None

contact_types = {"registrant": "Registrant(?: Contact)?",
                 "tech": "Tech(?:nical)?(?: Contact)?",
                 "admin" : "Admin(?:istrative)?(?: Contact)?"}

contact_fields = {"name": "(?:Name)?",
                  "organization": "Organization",
                  "street": "Street",
                  "city": "City",
                  "state": "State/Province",
                  "country": "Country",
                  "post_code": "Postal ?Code",
                  "email": "E-?mail",
                  "phone": "Phone",
                  "phone_ext": "Phone Ext",
                  "fax": "Fax",
                  "fax_ext": "Fax Ext"}

registrar_fields = {"name": "Registrar(?: Name)?",
                    "url": "Registrar URL",
                    "abuse_email": "Abuse Contact Email",
                    "abuse_phone": "Abuse Contact Phone",
                    "iana_id": "Registrar IANA ID"}

date_fields = {"created": ("Creation Date", "created", "Registered"),
               "updated": ("Last Modified", "Updated Date"),
               "expires": ("Expiration Date", "Expiry Date", "renewal date", "Expires")}

def parse(whois_str):
    """
    Parses the given whois result string in an attempt to extract common fields.

    @param whois_str The raw WHOIS result
    @return A dictionary of dictionaries containing the parsed data.
    """
    result_dict = {}

    for type in contact_types.keys():
        person_dict = dict()

        for field in contact_fields.keys():
            person_dict[field] = extract_field(whois_str, contact_types[type] + " " + contact_fields[field])

        result_dict[type] = person_dict

    registrar_dict = dict()
    for field in registrar_fields.keys():
        registrar_dict[field] = extract_field(whois_str, registrar_fields[field])

    result_dict['registrar'] = registrar_dict

    result_dict['reseller'] = {'name': extract_field(whois_str, "Reseller")}

    dates_dict = {}
    for field in date_fields.keys():
        date_str = extract_field(whois_str, *date_fields[field])
        if date_str:
            dates_dict[field] = date_parse(date_str)

    result_dict['date'] = dates_dict

    return result_dict
