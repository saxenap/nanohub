from dataclasses import dataclass
import pymysql
from sshtunnel import SSHTunnelForwarder


class IConnection:
    def get_connection_for(self, db_name: str):
        raise NotImplemented


class CachedConnection(IConnection):
    def __init__(self, connection: IConnection):
        self.connection = connection

    def get_connection_for(self, db_name: str):
        if not hasattr(self, 'cached_connection') or self.cached_connection == None:
            self.cached_connection = self.connection.get_connection_for(db_name)

        return self.cached_connection


@dataclass
class PyMysqlConnection(IConnection):
    db_host: str
    db_username: str
    db_password: str
    db_port: int = 3306

    def get_connection_for(self, db_name: str) -> pymysql.Connection:
        return pymysql.connect(
            host=self.db_host,
            database=db_name,
            user=self.db_username,
            passwd=self.db_password,
            port=self.db_port
        )


@dataclass
class TunneledConnection(IConnection):
    ssh_host: str
    ssh_username: str
    ssh_password: str
    remote_bind_address: str
    remote_bind_port: int

    db_host: str
    db_username: str
    db_password: str

    ssh_port: int = 22

    def get_connection_for(self, db_name: str) -> pymysql.Connection:
        tunnel = SSHTunnelForwarder((
            self.ssh_host, int(self.ssh_port)
        ),
            ssh_password=self.ssh_password,
            ssh_username=self.ssh_username,
            remote_bind_address=(
                self.remote_bind_address, int(self.remote_bind_port)
            )
        )
        tunnel.start()

        pymysql = PyMysqlConnection(
            db_host=self.db_host,
            db_username=self.db_username,
            db_password=self.db_password,
            db_port=tunnel.local_bind_port
        )

        return pymysql.get_connection_for(db_name)