
import argparse
from whois import whois
from datetime import datetime
import dateutil.parser
import sys

def howold(strDomain):

    strWhois = whois(args.domain).split('\n')

    if strWhois[0].startswith('Empty response from') or strWhois[0].startswith('Rate limited by '):
        return None

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
    

    return None
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', help='domain to analyze', type=str)
    args = parser.parse_args()

    resAge = howold(args.domain)
    if resAge:
       print(str(resAge))