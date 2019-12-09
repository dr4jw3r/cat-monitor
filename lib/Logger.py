class Logger(object):
    def __init__(self, args, classname):
        self.args = args
        self.classname = classname
    
    def log(self, text):
        print("[{0}] {1}".format(self.classname, text))
        
    def verbose(self, text):
        if self.args.verbose:
            print("[{0}] {1}".format(self.classname, text))