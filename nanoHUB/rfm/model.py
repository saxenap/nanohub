from sqlalchemy import Column
from sqlalchemy import Integer, String, Numeric, Text, DateTime, TIMESTAMP, BigInteger
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class UserDescriptors(Base):
    __tablename__ = "user_descriptors"
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(150), unique=True)
    name: str = Column(String(255))
    email: str = Column(String(150))

    earliest_simulation: str = Column(DateTime, nullable=True, index=True)
    latest_simulation: str = Column(DateTime, nullable=True, index=True)

    simulation_lifetime_days: int = Column(Integer, nullable=True)
    simulations_run_count: int = Column(Integer, nullable=True)
    tools_used_names: str = Column(Text,nullable=True)
    tools_used_count: int = Column(Integer, nullable=True)

    days_spent_on_nanohub: int = Column(Integer, comment='total number of days spent on nanoHUB')
    user_lifetime_days: int = Column(Integer, comment='last day - registration day')
    average_freqency: int = Column(Numeric, index=True, comment='F = lifetime in days / Days spent on nanoHUB')

    registerDate: str = Column(DateTime, index=True)
    lastvisitDate: str = Column(DateTime, index=True)

    timestamp_last_updated: str = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, index=True)

    '''
    http://dev.mysql.com/doc/refman/5.5/en/timestamp.html
    By default, TIMESTAMP columns are NOT NULL, cannot contain NULL values, and assigning NULL assigns the current timestamp.
    '''
    timestamp_created: str = Column(DateTime, nullable=True)

    def __repr__(self):
        return "<UserDescriptor(name='%s', username='%s', email='%s', " \
               "average_frequency='%f')" % (self.name, self.username, self.email,
                                      self.average_freqency)


class LastUpdateRecord(Base):
    __tablename__ = "last_update_record"
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}

    id: int = Column(Integer, primary_key=True)
    last_processed_toolstart_id: int = Column(BigInteger, server_default='0', unique=True, nullable=False, index=True)
    last_processed_toolstart_id_updated: str = Column(DateTime)