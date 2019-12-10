class Logger(object):
    def __init__(self, args, classname):
        self.args = args
        self.classname = classname
    
    def log(self, text):
        print("[N][{0}] {1}".format(self.classname, text))
        
    def verbose(self, text):
        if self.args.verbose:
            print("[V][{0}] {1}".format(self.classname, text))
            
    def err(self, text):
        print("[E][{0}] {1}".format(self.classname, text))