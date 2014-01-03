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

import re
import copy

class typogen(object):
    """generate typo"""

    def __init__(self):
        #Load up the list of TLDs
        self.lstTlds = list()
        filename = "./tlds.txt"
        with open(filename) as f:
            for line in f:
                if not line.lstrip().startswith('#'):
                    self.lstTlds.append(line.rstrip().lower())

    @staticmethod
    def loadkeyb(strCountry):
        keyDict = dict()

        # obviously you can have other maps here
        # I've only included this one
        filename = "./keyb" + strCountry + ".txt"
        with open(filename) as f:
            for line in f:
                split = line.rstrip().split(',')
                if split[0] in keyDict:
                    keyDict[split[0]].append(split[1])
                else:
                    keyDict[split[0]] = [split[1]]

        return keyDict

    def generatetypos(self, strHost, strCountry):
        """generate the typos"""

        # result list of typos
        lstTypos = []
        
        # debug
        #uniqueTypos = set(lstTypos)
        #uniqueTypos.add(strHost)
        #return uniqueTypos

        # missing characters
        idx = 0
        while idx < len(strHost):
            strTypo = strHost[0:idx]+strHost[idx+1:]
            idx+=1
            lstTypos.append(strTypo)

        # duplicate characters
        idx = 0
        while idx < len(strHost):
            strHostList = list(strHost)
            if strHostList[idx] != '.':
                strHostList.insert(idx,strHostList[idx])
                strTypo = "".join(strHostList)
                lstTypos.append(strTypo)
            idx+=1
            

        # tld swap out
        filename = "./tlds.txt"
        with open(filename) as f:
            lastdot = strHost.rfind(".")
            for line in f:
                if not line.lstrip().startswith('#'):
                    gtld = line.rstrip().lower()
                    newHost = strHost[:lastdot] + "." + gtld
                    #print(newHost)
                    lstTypos.append(newHost)

        # load keyboard mapping
        keyDict = typogen.loadkeyb(strCountry)

        # for the keyboard mapping
        for key in keyDict:
            for value in keyDict[key]:
                idx = 0
                while idx < len(strHost):
                    strHostList = list(strHost)
                    strHostList[idx] = strHostList[idx].replace(key, value)
                    strTypo = "".join(strHostList)
                    if strTypo != strHost:
                        lstTypos.append(strTypo)
                    idx+=1

        uniqueTypos = set(lstTypos)
        uniqueTypos.remove(strHost)

        return uniqueTypos

    def is_domain_valid(self, domain):
        #Ensure its in the correct character set
        if not re.match('^[a-z0-9.-]+$', domain):
            return False
        #Ensure the TLD is sane
        elif domain[domain.rfind(".") + 1:] not in self.lstTlds:
            return False
        # hostnames can't start or end with a -
        elif ".-" in domain or "-." in domain or domain.startswith("-"):
            return False
        #Ensure the location of dots are sane
        elif ".." in domain or domain.startswith("."):
            return False
        else:
            return True

    @staticmethod
    def bitflipbyte(inputbyte):
        """
        Flips the lowest 7 bits in the given input byte/int to build a list of mutated values.

        @param inputbyte: The byte/int to bit flip
        @return: A list of the mutated values.
        """
        result = list()
        mask = 1
        #As we know we're flipping ASCII, only do the lowest 7 bits
        for i in range(0,7):
            result.append(inputbyte ^ mask)
            mask <<= 1
        return result

    @staticmethod
    def bitflipstring(strInput):
        """
        Flips the lowest 7 bits in each character of the given string to build a list of mutated values.

        @param strInput: The string to bit flip
        @return: A list of the mutated values.
        """
        result = list()
        i = 0
        for character in strInput:
            flippedchars = typogen.bitflipbyte(character.encode("UTF-8")[0])
            for flippedchar in flippedchars:
                result.append(strInput[:i] + chr(flippedchar) + strInput[i + 1:])
            i+=1
        return result

    # v2 API with two new options
    def generatetyposv2(self, strHost,strCountry,bTLDS,bTypos,bBitFlip):
        """generate the typos"""

        # result list of typos
        lstTypos = []

        # debug
        #uniqueTypos = set(lstTypos)
        #uniqueTypos.add(strHost)
        #return uniqueTypos

        if bBitFlip:
            lstTypos += self.bitflipstring(strHost)

        if bTypos:
            # missing characters
            idx = 0
            while idx < len(strHost):
                strTypo = strHost[0:idx]+strHost[idx+1:]
                idx+=1
                lstTypos.append(strTypo)

            # duplicate characters
            idx = 0
            while idx < len(strHost):
                strHostList = list(strHost)
                if strHostList[idx] != '.':
                    strHostList.insert(idx,strHostList[idx])
                    strTypo = "".join(strHostList)
                    lstTypos.append(strTypo)
                idx+=1

            # load keyboard mapping
            keyDict = typogen.loadkeyb(strCountry)

            # for the keyboard mapping
            for key in keyDict:
                for value in keyDict[key]:
                    idx = 0
                    while idx < len(strHost):
                        strHostList = list(strHost)
                        strHostList[idx] = strHostList[idx].replace(key, value)
                        strTypo = "".join(strHostList)
                        lstTypos.append(strTypo)
                        idx+=1

        if bTLDS:
            lastdot = strHost.rfind(".")
            # tld swap out
            for gtld in self.lstTlds:
                newHost = strHost[:lastdot] + "." + gtld
                #print(newHost)
                lstTypos.append(newHost)

        uniqueTypos = set(lstTypos)

        try:
            uniqueTypos.remove(strHost)
        except KeyError:
            pass

        #Remove any invalid typos
        for typo in copy.copy(uniqueTypos):
            if not self.is_domain_valid(typo):
                uniqueTypos.remove(typo)

        return uniqueTypos
