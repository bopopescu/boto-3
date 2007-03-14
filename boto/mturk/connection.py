# Copyright (c) 2006,2007 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import urllib
import xml.sax
from boto import handler
from boto.mturk.price import Price
from boto.connection import AWSQueryConnection
from boto.exception import EC2ResponseError
from boto.resultset import ResultSet

class MTurkConnection(AWSQueryConnection):

    APIVersion = '2006-10-31'
    SignatureVersion = '1'

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None,
                 is_secure=False, port=None, proxy=None, proxy_port=None,
                 host='mechanicalturk.amazonaws.com', debug=0):
        AWSQueryConnection.__init__(self, aws_access_key_id,
                                    aws_secret_access_key,
                                    is_secure, port, proxy, proxy_port,
                                    host, debug)

    def get_account_balance(self):
        params = {}
        response = self.make_request('GetAccountBalance', params)
        body = response.read()
        if response.status == 200:
            rs = ResultSet(['AvailableBalance', 'OnHoldBalance'], Price)
            h = handler.XmlHandler(rs, self)
            xml.sax.parseString(body, h)
            return rs
        else:
            raise EC2ResponseError(response.status, response.reason, body)

    def register_hit_type(self, title, description, reward, duration,
                          keywords=None, approval_delay=None, qual_req=None):
        """
        Register a new HIT Type
        \ttitle, description are strings
        \treward is a Price object
        \tduration can be an integer or string
        """
        params = {'Title' : title,
                  'Description' : description,
                  'AssignmentDurationInSeconds' : duration}
        params.update(reward.get_as_params('Reward'))
        response = self.make_request('RegisterHITType', params)
        body = response.read()
        if response.status == 200:
            rs = ResultSet()
            h = handler.XmlHandler(rs, self)
            xml.sax.parseString(body, h)
            return rs.HITTypeId
        else:
            raise EC2ResponseError(response.status, response.reason, body)
        