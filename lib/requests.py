from collections import namedtuple
import inspect

# create a named tuple which you can pass default values to
# by name and by args
def nnamedtuple(cls,*_tuple,**namedvalues):

    # make our tuple maluable for now
    _tuple = list(_tuple)

    # get the args for cls creation, minus cls
    args = inspect.getargspec(cls.__new__)[0][1:]

    # pad the tuple out
    arg_count = len(args)
    if len(_tuple) != arg_count:
        # we need the tuple to be the min len, pad w/ none's
        diff = arg_count - len(_tuple)
        _tuple = _tuple + [None for x in xrange(diff)]

    # fill in our args
    for index, arg in enumerate(args):
        if arg in namedvalues:
            _tuple[index] = namedvalues.get(arg)

    # now that we've got our tuple sorted out create the namedtuple
    nt = cls(*_tuple)

    return nt


# easy way to provide default non-None values for named tuple values
def dnamedtuple(name,fields,**defaults):
    # we are going to return a callable which
    # creates the named tuple and fills in the defaults
    NT = namedtuple(name,fields)
    print name,fields
    def create_named_tuple(*args,**kwargs):
        # the kwargs are going to set values when from nnamedtuple
        for k,v in defaults.iteritems():
            if not kwargs.get(k):
                kwargs[k] = v

        # this function returns a named tuple w/ initial values
        # set via kwargs
        nt = nnamedtuple(NT,*args,**kwargs)

        return nt
    return create_named_tuple


# simple way to make sure we're all making similar requests / responses

request_fields = ['key','msg_type','request_type']
response_fields = ['key','msg_type','url','port']

def Request(name,request,*extra_fields,**defaults):
    if not defaults.get('msg_type'):
        defaults['msg_type'] = 'request'
    defaults['request_type'] = request
    extra_fields = list(extra_fields)
    return dnamedtuple(name,request_fields+extra_fields,**defaults)

def Response(name,*extra_fields,**defaults):
    if not defaults.get('msg_type'):
        defaults['msg_type'] = 'response'
    extra_fields = list(extra_fields)
    return dnamedtuple(name,response_fields+extra_fields,**defaults)

# create our response / request named tuples
RawRequest = Request('RawRequest','udp_row_in','vformat')
RawResponse = Response('RawResponse')

ConvertRequest = Request('ConvertRequest','tcp_convert_row','vformat')
ConvertResponse = Response('ConvertResponse')

StoreRequest = Request('StoreRequest','tcp_store_processed')
StoreResponse = Response('StoreResponse')

ReadRequest = Request('ReadRequest','tcp_read_processed','offset',offset=0)
ReadResponse = Response('ReadResponse')
