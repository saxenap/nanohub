from dataclasses import dataclass
import pymysql
from sshtunnel import SSHTunnelForwarder


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

    def __init__(self, db_factory: IDbConnectionFactory, params: TunneledConnectionParams):
        self.db_factory = db_factory
        self.params = params

    def get_connection_for(self, db_name: str):
        tunnel = SSHTunnelForwarder((
            self.params.ssh_host, int(self.params.ssh_port)
        ),
            ssh_password=self.params.ssh_password,
            ssh_username=self.params.ssh_username,
            remote_bind_address=(
                self.params.remote_bind_address, int(self.params.remote_bind_port)
            )
        )
        tunnel.start()

        self.db_factory.set_port(tunnel.local_bind_port)
        return self.db_factory.get_connection_for(db_name)