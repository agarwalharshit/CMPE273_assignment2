import socket
import threading
import signal
import sys
import redis
from CircuitBreaker import CircuitBreaker

config =  {
            "HOST_NAME" : "localhost",
            "BIND_PORT" : 9090,
            "MAX_REQUEST_LEN" : 1024,
            "CONNECTION_TIMEOUT" : 2
          }


class Server:
    """ The server class """

    def __init__(self, config):
        signal.signal(signal.SIGINT, self.shutdown)     # Shutdown on Ctrl+C
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Create a TCP socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Re-use the socket
        self.serverSocket.bind((config['HOST_NAME'], config['BIND_PORT'])) # bind the socket to a public host, and a port
        self.serverSocket.listen(10)    # become a server socket
        self.__clients = {}


    def listenForClient(self):
        """ Wait for clients to connect """
        i=-1

        while True:
            (clientSocket, client_address) = self.serverSocket.accept()   # Establish the connection
            i=i+1

            r = redis.Redis('localhost')
            s = r.lrange('Instances', 0, -1)
            sset = set(s)
            s = list(sset)
            print s
            listlen = len(s)

            url=s[i%listlen].split(':')
            urlname=s[i%listlen]
            ip=url[0]
            print ip
            port=url[1]
            print port
            try:
                d = threading.Thread(name=self._getClientName(client_address), target=self.proxy_thread, args=(clientSocket, client_address, i,ip ,port,urlname))
            except Exception as e:
                print e
            d.setDaemon(True)
            d.start()
        self.shutdown(0,0)


    def proxy_thread(self, conn, client_addr, i, ip, port, urlname):
        """
        *******************************************
        *********** PROXY_THREAD FUNC *************
          A thread to handle request from browser
        *******************************************
        """
        try:
            self.proxy_thread_CB(conn, client_addr, i, ip, port, urlname)
        except Exception as e:
            print 'ERROR: ',e.message


    @CircuitBreaker(max_failure_to_open=3, reset_timeout=50)
    def proxy_thread_CB(self, conn, client_addr, i, ip, port, urlname):
        request = conn.recv(config['MAX_REQUEST_LEN'])        # get the request from browser
        first_line = request.split('\n')[0]                   # parse the first line


        try:
            print port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)

            s.connect((ip, int(port)))
            s.sendall(request)                           # send request to webserver

            while 1:
                data = s.recv(config['MAX_REQUEST_LEN'])          # receive data from web server
                if (len(data) > 0):
                    conn.send(data)                               # send to browser
                else:
                    break
            s.close()
            conn.close()
        except socket.error as error_msg:
            print 'ERROR: ',client_addr,error_msg
            if s:
                s.close()
            if conn:
                conn.close()
            raise Exception






    def _getClientName(self, cli_addr):
        """ Return the clientName.
        """
        return "Client"


    def shutdown(self, signum, frame):
        """ Handle the exiting server. Clean all traces """
        self.serverSocket.close()
        sys.exit(0)


if __name__ == "__main__":
    server = Server(config)
    server.listenForClient()
