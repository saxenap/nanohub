import logging
from dataclasses import dataclass
import pymysql
from sqlalchemy import create_engine
from sshtunnel import create_logger , SSHTunnelForwarder
from paramiko import Transport
from nanoHUB.dataaccess.sql import CachedConnection, TunneledConnection
import os

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
    db_charset: str
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
            port=self.params.db_port,
            charset=self.params.db_charset
        )

    def set_port(self, port: int) -> None:
        self.params.db_port = port


class SqlAlchemyConnectionFactory(IDbConnectionFactory):

    def __init__(self, params: DbConnectionParams):
        self.params = params

    def get_connection_for(self, db_name: str):
        return create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset={}'.format(
            self.params.db_username,
            self.params.db_password,
            self.params.db_host,
            self.params.db_port,
            db_name,
            self.params.db_charset
        ))

    def set_port(self, port: int) -> None:
        self.params.db_port = port


@dataclass
class TunneledConnectionParams:

    ssh_host: str
    ssh_username: str
    ssh_password: str
    remote_bind_address: str
    remote_bind_port: int
    banner_timeout: int
    ssh_port: int = 22


class TunneledConnectionFactory(IDbConnectionFactory):

    def __init__(
            self, db_factory: IDbConnectionFactory,
            params: TunneledConnectionParams,
            logger,
            loglevel: str = 'ERROR',
            capture_warnings: bool = False
    ):

        self.db_factory = db_factory
        self.params = params
        self.logger = logger
        self.loglevel = loglevel
        self.capture_warnings = capture_warnings

    def get_connection_for(self, db_name: str):

        logger = create_logger(loglevel=self.loglevel, capture_warnings=self.capture_warnings)
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
        # self.logger.info("Started SSH Tunnel with %s" % self.params.ssh_host)
        tunnel._get_transport().banner_timeout = self.params.banner_timeout
        tunnel.start()

        self.db_factory.set_port(tunnel.local_bind_port)
        return self.db_factory.get_connection_for(db_name)



def get_connection():
    return CachedConnection(TunneledConnection(
        ssh_host = os.getenv('tunnel_ssh_host'),
        ssh_username = os.getenv('tunnel_ssh_username'),
        ssh_password = os.getenv('tunnel_ssh_password'),
        ssh_port = int(os.getenv('tunnel_ssh_port')),
        remote_bind_address = os.getenv('tunnel_remote_bind_address'),
        remote_bind_port = int(os.getenv('tunnel_remote_bind_port')),
        db_host = os.getenv('db_host'),
        db_username = os.getenv('db_user'),
        db_password = os.getenv('db_password')
    ))

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