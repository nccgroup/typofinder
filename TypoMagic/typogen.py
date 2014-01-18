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

    @staticmethod
    def generate_missing_character_typos(strHost):
        # missing characters

        result = list()
        idx = 0
        while idx < len(strHost):
            strTypo = strHost[0:idx] + strHost[idx + 1:]
            idx += 1
            result.append(strTypo)
        return result

    @staticmethod
    def generate_duplicate_character_typos(strHost):
        # duplicate characters

        result = list()
        idx = 0
        while idx < len(strHost):
            strHostList = list(strHost)
            if strHostList[idx] != '.':
                strHostList.insert(idx, strHostList[idx])
                strTypo = "".join(strHostList)
                result.append(strTypo)
            idx += 1
        return result

    @staticmethod
    def generate_miskeyed_typos(strHost, strCountry):
        # surrounding keys for each character

        result = list()
        # load keyboard mapping
        typoDict = typogen.loadkeyb(strCountry)

        for idx, char in enumerate(strHost):
            if char in typoDict:
                for replacement_char in typoDict[char]:
                    result.append(strHost[:idx] + replacement_char + strHost[idx + 1:])
        return result

    @staticmethod
    def generate_miskeyed_sequence_typos(strHost, strCountry):
        # repeated surrounding keys for any character sequences in the string

        result = list()
        # load keyboard mapping
        typoDict = typogen.loadkeyb(strCountry)

        idx = 0
        while idx < len(strHost):
            char = strHost[idx]
            #Loop through sequences of the same character, counting the sequence length
            sequence_len = 1
            while idx+1 < len(strHost) and strHost[idx+1] == char:
                sequence_len += 1
                idx+=1

            #Increment the index at this point to make the maths easier if we found a sequence
            idx += 1

            #Replace the whole sequence
            if sequence_len > 1:
                if char in typoDict:
                    for replacement_char in typoDict[char]:
                        result.append(strHost[:idx - sequence_len] + (replacement_char * sequence_len) + strHost[idx:])

        return result

    @staticmethod
    def generate_transposed_character_typos(strHost):
        result = list()
        for idx in range(0, len(strHost) - 1):
            result.append(strHost[:idx] + strHost[idx+1:idx+2] + strHost[idx:idx+1] + strHost[idx+2:])
        return result

    def generatetyposv2(self, strHost, strCountry, bTypos, iTypoIntensity, bTLDS, bBitFlip):
        """
        generate the typos

        @param strHost The hostname to generate typos for
        @param strCountry The country code of the keyboard to use when generating miskeyed typos
        @param bTypos Flag to indicate that typos should be generated
        @param iTypoIntensity A percentage of how intense the typo generation should be.
        @param bTLDS Flag to indicate that the TLDs should be swapped
        @param bBitFlip Flag to indicate that the hostname should be bitflipped
        """

        # result list of typos
        lstTypos = []

        if bBitFlip:
            lstTypos += self.bitflipstring(strHost)

        if bTypos:
            #Quick:
            lstTypos += self.generate_missing_character_typos(strHost)
            lstTypos += self.generate_duplicate_character_typos(strHost)
            #Balanced:
            if iTypoIntensity > 0:
                lstTypos += self.generate_miskeyed_typos(strHost, strCountry)
            #Rigorous:
            if iTypoIntensity > 50:
                lstTypos += self.generate_transposed_character_typos(strHost)
                lstTypos += self.generate_miskeyed_sequence_typos(strHost, strCountry)

        if bTLDS:
            lastdot = strHost.rfind(".")
            # tld swap out
            for gtld in self.lstTlds:
                newHost = strHost[:lastdot] + "." + gtld
                #print(newHost)
                lstTypos.append(newHost)

        uniqueTypos = set(lstTypos)

        # Add the original domain 
        try:
            uniqueTypos.add(strHost)
        except KeyError:
            pass

        # Remove any invalid typos
        for typo in copy.copy(uniqueTypos):
            if not self.is_domain_valid(typo):
                uniqueTypos.remove(typo)

        return sorted(uniqueTypos)
