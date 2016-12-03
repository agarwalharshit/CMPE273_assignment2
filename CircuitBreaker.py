from functools import wraps
from datetime import datetime, timedelta
import redis


class CircuitBreaker(object):
    def __init__(self, name=None, expected_exception=Exception, max_failure_to_open=3, reset_timeout=50):
        self._name = name
        self._expected_exception = expected_exception
        self._max_failure_to_open = max_failure_to_open
        self._reset_timeout = reset_timeout
        self.failureDict={}
        # Set the initial state
        self.close()

    def close(self):
        self._is_closed = True
        self._failure_count = 0

    def open(self,url):
        r = redis.Redis('localhost')
        r.lrem('Instances', url, num=0)
        self.failureDict[url] = 0
        #self._is_closed = False
        #self._opened_since = datetime.utcnow()

    def can_execute(self):
        if not self._is_closed:
            self._open_until = self._opened_since + timedelta(seconds=self._reset_timeout)
            self._open_remaining = (self._open_until - datetime.utcnow()).total_seconds()
            return self._open_remaining <= 0
        else:
            return True

    def __call__(self, func, *args, **kwargs):
        if self._name is None:
            self._name = func.__name__
            print "Failure count before is: ",self._failure_count

        @wraps(func)
        def with_circuitbreaker(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return with_circuitbreaker

    def call(self, func, *args, **kwargs):
        url=args[args.__len__()-1]
        if not self.can_execute():
            err = 'CircuitBreaker[%s] is OPEN until %s (%d failures, %d sec remaining)' % (
                self._name,
                self._open_until,
                self._failure_count,
                round(self._open_remaining)
            )
            raise Exception(err)

        try:
           # print "Failure count before is: ", self.failureDict[url]
            result = func(*args, **kwargs)
            self.failureDict[url]=0
            print "Failure count after is: ", self.failureDict[url]
        except self._expected_exception:
            print "Inside CB exception"
            #self._failure_count += 1
            if url in self.failureDict:
                self.failureDict[url]=self.failureDict[url]+1
                print "self.failureDict[url]=",self.failureDict[url]
            else:
                self.failureDict[url]=1
            if self.failureDict[url] >= self._max_failure_to_open:
                self.open(url)
            print "Failure count after is: ", self.failureDict[url]
            raise

        self.close()
        return result