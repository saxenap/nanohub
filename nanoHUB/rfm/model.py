from sqlalchemy import Column
from sqlalchemy import Integer, String, Numeric, Text, DateTime, TIMESTAMP, BigInteger
from sqlalchemy import text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class AbstractUserDescriptor(Base):
    __abstract__ = True
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}

    first_sim_date: str = Column(DateTime, nullable=True, index=True)
    last_sim_date: str = Column(DateTime, nullable=True, index=True)

    sims_lifetime: int = Column(Integer, nullable=True, comment='days from first to last simulation')
    sims_count: int = Column(Integer, nullable=True, comment='number of simulations')
    sims_activity_days: int = Column(Integer, comment='count of days spent performing simulations')
    tools_used_names: str = Column(Text,nullable=True, comment='names of tools used in simulations')
    tools_used_count: int = Column(Integer, nullable=True, comment='number of tools used in simulations')

    active_days: int = Column(Integer, comment='count of days performing any activity')
    average_freqency: int = Column(Numeric, index=True, comment='F = lifetime in days / Days spent on nanoHUB')

    '''
       http://dev.mysql.com/doc/refman/5.5/en/timestamp.html
       By default, TIMESTAMP columns are NOT NULL, cannot contain NULL values, and assigning NULL assigns the current timestamp.
       '''
    _last_updated: str = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, index=True)



def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

class TempUserDescriptors(AbstractUserDescriptor):
    __tablename__ = "temp_user_descriptor"

    temp_id: int = Column(Integer, primary_key=True)
    user: str = Column(String(150), unique=True)


class UserDescriptors(AbstractUserDescriptor):
    __tablename__ = "user_descriptor"

    id: int = Column(Integer, primary_key=True)

    username: str = Column(String(150), unique=True)
    name: str = Column(String(255))
    email: str = Column(String(150))

    registration_date: str = Column(DateTime, index=True)
    last_visit_date: str = Column(DateTime, index=True)
    lifetime_days: int = Column(Integer, comment='last day - registration day')

    _created: str = Column(DateTime, nullable=True)


class LastUpdateRecord(Base):
    __tablename__ = "record_update_history"
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}

    id: int = Column(Integer, primary_key=True)
    last_processed_toolstart_id: int = Column(BigInteger, server_default='0', unique=True, nullable=False, index=True)
    last_processed_toolstart_id_updated: str = Column(DateTime)