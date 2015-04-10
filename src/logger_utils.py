import logging
import time


class Unique(logging.Filter):
    """Messages are allowed through just once in second.
    """
    def __init__(self, name=""):
        logging.Filter.__init__(self, name)
        self.reset()

    def reset(self):
        self.__logged = {}

    def filter(self, rec):
        return logging.Filter.filter(self, rec) and self.__is_first_time(rec)

    def __is_first_time(self, rec):
        n = time.time()
        """Emit a message only once in second."""
        msg = rec.msg %(rec.args)
        if msg in self.__logged:
            ret = True
            if self.__logged[msg][1] > (n - 1.0):
                ret = False
                self.__logged[msg][0] += 1
            else:
                self.__logged[msg][1] = time.time()
                if self.__logged[msg][0] > 1:
                    rec.msg = "Repeated %s times: %s" % (self.__logged[msg][0], msg)
                self.__logged[msg][0] = 1
            return ret
        else:
            self.__logged[msg] = [1, time.time()]

            return True
