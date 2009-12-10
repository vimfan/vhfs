import exceptions

class VHFSException(exceptions.Exception):
    def __init__(self, msg = None, err_code = None):
        super(VHFSException, self).__init__(msg, err_code)
        self.msg = msg
        self.err_code = err_code
        
class VHFSOverloadException(VHFSException):
    def __init__(self, *arg, **kw):
        super(VHFSOverloadException, self).__init__(*arg, **kw)
