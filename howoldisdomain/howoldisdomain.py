#
# Discover how old a domain is
# 
# Released as open source by NCC Group Plc - http://www.nccgroup.com/
# 
# Developed by Ollie Whitehouse, ollie dot whitehouse at nccgroup dot trust
#
# http://www.github.com/nccgroup/typofinder
#
# Released under AGPL see LICENSE for more information#
#

import argparse
from whois import whois
from datetime import datetime
import dateutil.parser
import sys

def howold(strDomain):

    strWhois = whois(strDomain).split('\n')

    if strWhois[0].startswith('Empty response from') or strWhois[0].startswith('Rate limited by '):
        return None

    try:
        for strLine in strWhois:
            if strLine.startswith('Creation Date: '):
                strDate = strLine[15:]
                dateThen = dateutil.parser.parse(strDate)
                dateThen = dateThen.replace(tzinfo=None)
                dateNow  = datetime.now()
                dateDiff = dateNow - dateThen
                return dateDiff.days

        # FR
        for strLine in strWhois:
            strLine = strLine.strip(' ')
            if strLine.startswith('created:     '):
                strDate = strLine[15:]
                dateThen = dateutil.parser.parse(strDate)
                dateThen = dateThen.replace(tzinfo=None)
                dateNow  = datetime.now()
                dateDiff = dateNow - dateThen
                return dateDiff.days
            
        # UK
        for strLine in strWhois:
            strLine = strLine.strip(' ')
            if strLine.startswith('Registered on: '):
                strDate = strLine[15:]
                dateThen = dateutil.parser.parse(strDate)
                dateThen = dateThen.replace(tzinfo=None)
                dateNow  = datetime.now()
                dateDiff = dateNow - dateThen
                return dateDiff.days
                     

        # CN
        for strLine in strWhois:
            strLine = strLine.strip(' ')
            if strLine.startswith('Registration Time: '):
                strDate = strLine[19:]
                dateThen = dateutil.parser.parse(strDate)
                dateThen = dateThen.replace(tzinfo=None)
                dateNow  = datetime.now()
                dateDiff = dateNow - dateThen
                return dateDiff.days
    except ValueError:
        return None

    return None
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', help='domain to analyze', type=str)
    parser.add_argument('-t', '--test', help='unit tests',  dest='tests', action='store_true')
    parser.set_defaults(tests=False)
    args = parser.parse_args()

    if args.tests:
        arryDomains  = ['nccgroup.trust','nccgroup.com','facebook.cn','facebook.com','facebook.fr','facebook.de','facebook.co.uk','facebook.net','facebook.gr','facebook.nl','facebook.se','facebook.fi','facebook.ae','facebook.cm','facebook.co'
                        ,'facebook.it','facebook.es','facebook.za','facebook.ca','facebook.pl','facebook.su','facebook.ru','facebook.tw','facebook.jp','facebook.au','facebook.nz','facebook.ar','facebook.mx','facebook.is','facebook.io']
        for strDomain in arryDomains:
            resAge = howold(strDomain)
            print("[i] " + strDomain + " - ", end="")
            if resAge:
                print(str(resAge) + " - pass")
            else:
                print(" unknown - fail")
    else:
        if args.domain and len(args.Domain) > 0:
            resAge = howold(args.domain)
            if resAge:
                print(str(resAge))
                sys.exit(0)
            else:
                sys.exit(-1)