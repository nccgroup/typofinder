from abc import ABCMeta, abstractmethod


class ExtraInfoQuery(object):
    """
    Abstract superclass for classes which query 3rd party services for additional info about hosts.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def query(self, hostname, ipaddress):
        """
        Queries the service implemented in the subclass for additional information about the hostname and/or associated
         ip address supplied.

        @param hostname: The hostname to query the specific service for.
        @param ipaddress: The ip address associated with the hostname parameter to query the specific service for.
        @return A 2 part tuple of HTML compatible strings. The first should be a short representation of a few words.
         The second string should be a more detailed explanation of the result. If there is no additional information
         available, (None, None) should be returned.
        """
        pass
