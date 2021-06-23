import logging
from dataclasses import dataclass
import pymysql
from sshtunnel import create_logger , SSHTunnelForwarder
from paramiko import Transport


class IDbConnectionFactory:

    def get_connection_for(self, db_name: str):
        raise NotImplemented

    def set_port(self, port: int) -> None:
        raise NotImplemented


@dataclass
class DbConnectionParams:

    db_host: str
    db_username: str
    db_password: str
    db_port: int = 3306


class PyMysqlConnectionFactory(IDbConnectionFactory):

    def __init__(self, params: DbConnectionParams):
        self.params = params

    def get_connection_for(self, db_name: str):

        return pymysql.connect(
            host=self.params.db_host,
            database=db_name,
            user=self.params.db_username,
            passwd=self.params.db_password,
            port=self.params.db_port
        )

    def set_port(self, port: int) -> None:
        self.params.db_port = port


@dataclass
class TunneledConnectionParams:

    ssh_host: str
    ssh_username: str
    ssh_password: str
    remote_bind_address: str
    remote_bind_port: int
    ssh_port: int = 22


class TunneledConnectionFactory(IDbConnectionFactory):

    def __init__(self, db_factory: IDbConnectionFactory, params: TunneledConnectionParams, logger: logging.Logger):

        self.db_factory = db_factory
        self.params = params
        self.logger = logger

    def get_connection_for(self, db_name: str):

        logger = create_logger(loglevel="INFO")
        tunnel = SSHTunnelForwarder(
            (
                self.params.ssh_host, int(self.params.ssh_port)
            ),
            ssh_password=self.params.ssh_password,
            ssh_username=self.params.ssh_username,
            remote_bind_address=(
                self.params.remote_bind_address, int(self.params.remote_bind_port)
            ),
            logger=logger
        )
        self.logger.info("Started SSH Tunnel with %s" % self.params.ssh_host)
        tunnel.start()

        self.db_factory.set_port(tunnel.local_bind_port)
        return self.db_factory.get_connection_for(db_name)



'''
Problem with packet sizing - Paramiko drops connection
Edge case testing needed
1. https://github.com/paramiko/paramiko/issues/175#issuecomment-24125451
2. https://stackoverflow.com/a/55796683
'''


class FastTransport(Transport):

    def __init__(self, sock):
        super(FastTransport, self).__init__(sock)
        self.window_size = 2147483647
        self.packetizer.REKEY_BYTES = pow(2, 40)
        self.packetizer.REKEY_PACKETS = pow(2, 40)