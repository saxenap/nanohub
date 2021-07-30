from sqlalchemy import Column
from sqlalchemy import Integer, String, Numeric, JSON
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class UserDescriptors(Base):
    __tablename__ = "user_descriptors"

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(150), unique=True)
    name: str = Column(String(255))
    email: str = Column(String(150))

    simulation_lifetime: int = Column(Integer, nullable=True)
    num_simulations_run: int = Column(Integer, nullable=True)

    name_tools_used: str = Column(JSON,nullable=True)
    num_tools_used: int = Column(Integer, nullable=True)

    num_days_spent: int = Column(Integer, comment='total number of days spent on nanoHUB')
    user_lifetime: int = Column(Integer, comment='last day - registration day')
    average_freqency: int = Column(Numeric, index=True, comment='F = lifetime in days / Days spent on nanoHUB')


    def __repr__(self):
        return "<UserDescriptor(name='%s', username='%s', email='%s', " \
               "average_frequency='%f')" % (self.name, self.username, self.email,
                                      self.average_freqency)

