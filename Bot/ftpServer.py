from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def run(ip, port):
    authorizer = DummyAuthorizer()
    # Define a new user having full r/w permissions.
    authorizer.add_user("CC", "Sicurezza", "./file", perm='r')

    handler = FTPHandler
    handler.authorizer = authorizer
    # Define a customized banner (string returned when client connects)
    handler.banner = "pyftpdlib based ftpd ready."
    # Optionally specify range of ports to use for passive connections.
    # handler.passive_ports = range(60000, 65535)
    address = (ip, port)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()
