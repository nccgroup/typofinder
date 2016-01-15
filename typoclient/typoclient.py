#
# Typofinder for domain typo discovery
# 
# Released as open source by NCC Group Plc - http://www.nccgroup.com/
# 
# Developed by Ollie Whitehouse, ollie dot whitehouse at nccgroup dot com
#
# http://www.github.com/nccgroup/typofinder
#
# Released under AGPL see LICENSE for more information#
#

import sys
import codecs
import argparse
import requests
import simplejson

def tryDomain(strURLEntity,dataFoo,strHTTPHdrs, intDepth):
    arrDomainResp = requests.post(strURLEntity, data=dataFoo, headers=strHTTPHdrs, verify=False)

    if arrDomainResp.status_code != requests.codes.ok:
        print("[!] Recieved error from web service please try again later")
        sys.exit(0)

    try:
        strDEntityJSON = arrDomainResp.json()
        strDomain = strDEntityJSON['strDomain']

        if args.verbose is True:
            print("[i] " + strDEntityJSON['strDomain'])
            if strDEntityJSON['bError'] is False:
                for server in strDEntityJSON['nameservers']:
                    print ("[i]    --- " + server);
            else:
                    print ("[!]    --- " + strDEntityJSON['strError'])
        else:
            if strDEntityJSON['bError'] is False:
                print("[i] " + strDEntityJSON['strDomain'] + " is active")                           
            elif args.errors is True:
                print("[i] " + strDEntityJSON['strDomain'] + " generated an error - " + strDEntityJSON['strError'])                           

    except simplejson.scanner.JSONDecodeError:
        print("[!] JSON decode error")

if __name__ == '__main__':

    print("[i] NCC Group DNS typo domain command line client - https://labs.nccgroup.trust");
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--domain', help='domain to analyze', required=False, type=str, default='nccgroup.com')
        parser.add_argument('-s', '--server',   help='server to use', required=False, type=str, default='https://labs.nccgroup.trust')
        parser.add_argument('-v', '--verbose',   help='verbose output', required=False, dest='verbose', action='store_true')
        parser.add_argument('-e', '--errors',   help='show errors in non verbose mode', required=False, dest='errors', action='store_true')
        parser.set_defaults(verbose=False);
        parser.set_defaults(errors=False);
        args = parser.parse_args()

        requests.packages.urllib3.disable_warnings()
    
        strURLTypos  = args.server + "/typofinder/typov2.ncc"
        strURLEntity = args.server +  "/typofinder/entitylight.ncc"

        strHTTPHdrs      = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'text/plain'}
        strTypoRequest   = "host="+args.domain+"&typos=typos&typoamount=100&tld=tld&bitflip=bitflip&homoglyph=homoglyph&doppelganger=doppelganger&charsetamount=100&alexafilter=neveralexa"
        strEntityRequest = "host="
    
        print("[i] Getting typo domains list....")
        arrTypoResp = requests.post(strURLTypos, data=strTypoRequest, headers=strHTTPHdrs, verify=False)

        if arrTypoResp.text.startswith("[!]"):
            print(arrTypoRest.text)
            sys.exit(0)

        strTypoJSON = arrTypoResp.json()

        print("[i] Total typo domains to check " + str(len(strTypoJSON)))

        print("[i] Checking typo domains list for active domains....")
        strDomain = ""
        for strTDomain in strTypoJSON:
            intDepth = 0
            dataFoo = strEntityRequest+strTDomain
            try:           
                tryDomain(strURLEntity,dataFoo,strHTTPHdrs, intDepth)
            except ConnectionAbortedError:
                intDepth = intDepth + 1
                if intDepth > 4:
                    print("[!] Connection abort whilst checking " + strDomain)
                else:
                    tryDomain(strURLEntity,dataFoo,strHTTPHdrs, intDepth)
            except ConnectionError:
                intDepth = intDepth + 1
                if intDepth > 4:
                    print("[!] Connection error whilst checking " + strDomain)
                else:
                    tryDomain(strURLEntity,dataFoo,strHTTPHdrs, intDepth)
            except requests.exceptions.ConnectionError:
                intDepth = intDepth + 1
                if intDepth > 4:
                    print("[!] Connection error whilst checking " + strDomain)
                else:
                    tryDomain(strURLEntity,dataFoo,strHTTPHdrs, intDepth)

    except ConnectionAbortedError:
        print("[!] Connection abort getting list of domains")
        pass

    except ConnectionError:
        print("[!] Connection error getting list of domains")
        pass
    
    except requests.exceptions.ConnectionError:
        print("[!] Connection error getting list of domains")
        pass

    except KeyboardInterrupt:
        pass

    except SystemExit:
        pass

    except:
        type, value, traceback = sys.exc_info()
        print("[i] Other error - " + str(type) + " - " + str(value))