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
import sys

#Seed the whois server map with special cases that aren't in our whois-servers.txt list nor returned by iana
#Based on http://www.nirsoft.net/whois-servers.txt
FIELD_SEPERATOR = ', '
RATE_LIMITTED_RESPONSES = ("WHOIS LIMIT EXCEEDED",
                           "Too many simulataneous connections from your host",
                           "Please try again later.",
                           "You have been banned for abuse.",
                           "has exceeded the established limit",
                           "WHOIS LIMI",
                           "Still in grace period, wait",
                           "Permission denied.")

_tld_to_whois = dict()

with open("datasources/whois-servers.txt", "r") as whois_servers:
    for line in whois_servers:
        if line.startswith(';'):
            continue
        parts = line.split(' ')
        _tld_to_whois['.' + parts[0].strip()] = parts[1].strip()

_psl = PublicSuffixList(input_file=codecs.open("datasources/effective_tld_names.dat", "r", "utf8"))


def _whois_lookup(sServer, sDomain):
    """
    Perform the network connection to the Whois Server and query for the given domain.

    @param sServer: The hostname of the whois server to query.
    @param sDomain: The domain to query for.
    @return: The whois result string.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((sServer, 43))
    except socket.timeout:
        return "Timeout connecting to " + sServer
    except socket.error:
        return "Unable to connect to " + sServer

    try:
        query = str(codecs.encode(sDomain, "idna"), "ascii") + '\r\n'
    except:
        #Assumes an encoding error, just send the raw string instead.
        query = sDomain + '\r\n'

    response = ''

    try:
        s.send(query.encode())

        while len(response) < 10000:
            bytes = s.recv(1000)
            try:
                block = bytes.decode("utf-8")
            except:
                #If it's not UTF-8, the second most popular encoding appears to be iso-8859-1
                block = bytes.decode("iso-8859-1")

            if block == '':
                break
            response = response + block
    except socket.error:
        pass
    finally:
        try:
            s.shutdown(socket.SHUT_RDWR)
        except socket.error:
            #Not much more we can do here
            pass
        finally:
            s.close()

    return response


def whois(sDomain):
    """
    Entry point for this package, which fetches whois data from the appropriate server.

    @param sDomain: The domain to query whois for.
    @return: The whois result.
    """
    sDomain = _psl.get_public_suffix(sDomain)

    sLDot = sDomain.find(".")
    tld = sDomain[sLDot:]

    if tld in _tld_to_whois:
        sServer = _tld_to_whois[tld]
    else:
        sServer = "whois.iana.org"

        try:
            for sLine in _whois_lookup(sServer, tld).split('\n'):
                if "refer:" in sLine or "whois:" in sLine:
                    sServer = sLine[6:].lstrip()
                    _tld_to_whois[tld] = sServer
                    break
        except:
            pass

    result = _recursive_whois(sServer, sDomain)

    #Special case to handle the fuzzy matching at the ICANN whois server
    if 'To single out one record, look it up with "xxx", where xxx is one of the' in result:
        all_domain_records = _whois_lookup(sServer, '=' + sDomain)
        all_whois_servers = _extract_field(all_domain_records, "Whois Server")
        if all_whois_servers != None:
            next_whois_server = all_whois_servers.split(', ')[-1]
            return _recursive_whois(next_whois_server, sDomain)
        else:
            return result
    else:
        return result


def _recursive_whois(sServer, sDomain):
    """
    A recursive whois function which will follow the "Whois Server:" referals.

    @param sServer: The hostname of the whois server to query.
    @param sDomain: The domain to query for.
    @return: The whois result string.
    """
    result = _whois_lookup(sServer, sDomain)

    next_whois_server = _extract_field(result, "Whois Server")
    if next_whois_server and next_whois_server != sServer and not next_whois_server.startswith("http"):
        return _recursive_whois(next_whois_server, sDomain)

    for error_message in RATE_LIMITTED_RESPONSES:
        if error_message in result:
            return "Rate limited by " + sServer

    if result.strip() == '':
        return "Empty response from " + sServer

    return result.lstrip()


def _extract_field(whois_blob, *args):
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

    regex = field_name + r"\.*:(?: |\t)*(.+)\n"

    match_list = re.finditer(regex, whois_blob, flags=re.IGNORECASE)

    for match in match_list:
        if match.group(1):
            value = match.group(1).strip()
            if value and value != "null":
                result.append(value)

    if not result:
        return None
    else:
        return FIELD_SEPERATOR.join(result)


def _date_parse(date_string):
    """
    Date parser which attempts to work with a range of date formats.

    @param date_string The string representing a date or date/time.
    @return A datetime object if one could be parsed, or None
    """

    if not date_string:
        return None
    date_string = date_string.rstrip('.')
    date_string = re.sub('(\d)T(\d)', '\g<1>\g<2>', date_string)
    date_string = date_string.replace(' ', '')
    date_string = date_string.replace('.', '-')
    date_string = date_string.rstrip('Z')

    #Handle timezones ourselves on python 2.X because the native datetime won't parse them
    tz_match = None
    if sys.version_info < (3,0):
        tz_match = re.match(r"(.*)(\+|-)(\d{2}):?(\d{2})$", date_string)
        if tz_match:
            date_string = tz_match.group(1)

    result = None

    for format in ("%Y-%m-%d%H:%M:%S", "%Y-%m-%d%H:%M:%S%z", "%Y-%m-%d", "%d-%b-%Y", "%a%b%d%H:%M:%S%Z%Y", "%Y-%d-%m", "%Y-%m-%d%H:%M:%S-%f", "%d-%b-%Y%H:%M:%S%Z"):
        try:
            result = datetime.datetime.strptime(date_string, format)
            break
        except ValueError:
            #Attempt the next format
            continue

    if result and tz_match:
        #Manipulate the datetime into UTC if we don't have timezone support
        delta = datetime.timedelta(hours=int(tz_match.group(3)), minutes=int(tz_match.group(4)))
        if tz_match.group(2) == '-':
            result += delta
        else:
            result -= delta

    return result

contact_types = {"registrant": "(?:Registrant|Owner)(?: Contact)?",
                 "tech": "Tech(?:nical)?(?: Contact)?",
                 "admin": "Admin(?:istrative)?(?: Contact)?"}

contact_fields = {"name": "(?:Name)?",
                  "organization": "Organi[sz]ation",
                  "street": "(?:(?:Street)|(?:Add?ress ?)1?)",
                  "city": "City",
                  "state": "State(?:/Province)?",
                  "country": "Country(?:/Economy)?",
                  "post_code": "Postal ?Code|zip",
                  "email": "E-?mail",
                  "phone": "(?:tele)?phone(?: Number)?",
                  "phone_ext": "Phone Ext",
                  "fax": "(?:Fax|Facsimile)[ -]?(?:Number|No)?",
                  "fax_ext": "Fax Ext"}

registrar_fields = {"name": "Registrar(?: Name)?",
                    "url": "Registrar (?:(?:URL)|(?:Homepage))",
                    "abuse_email": "Abuse Contact Email",
                    "abuse_phone": "Abuse Contact Phone",
                    "iana_id": "Registrar IANA ID"}

date_fields = {"created": ("Creation Date", "(?:Date )?created(?: on)?", "Registered(?: on)?", "Registration Date"),
               "updated": ("(?:Last )?Modified", "Updated Date", "(?:last )?updated?(?: on)?"),
               "expires": ("Expiration Date", "Expiry Date", "renewal date", "Expires(?: on)?", "Expire Date")}


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
            person_dict[field] = _extract_field(whois_str, contact_types[type] + "(?: |-)" + contact_fields[field])

        result_dict[type] = person_dict

    registrar_dict = dict()
    for field in registrar_fields.keys():
        registrar_dict[field] = _extract_field(whois_str, registrar_fields[field])

    result_dict['registrar'] = registrar_dict

    result_dict['reseller'] = {'name': _extract_field(whois_str, "Reseller")}

    dates_dict = {}
    for field in date_fields.keys():
        date_str = _extract_field(whois_str, *date_fields[field])
        if date_str:
            date_str = date_str.split(FIELD_SEPERATOR)[0]
            dates_dict[field] = _date_parse(date_str)
        else:
            dates_dict[field] = None

    result_dict['date'] = dates_dict

    return result_dict