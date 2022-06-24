from dataclasses import dataclass, astuple
from sqlalchemy import Column
from sqlalchemy import (
    UniqueConstraint, Integer, String, Text, DateTime, TIMESTAMP, Date, Enum
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from datetime import datetime
from nanoHUB.domain.cluster import (
    IClusterSpan, IAlgorithmInfo, IClusterInfo, SpanTypes, IClusterName
)

Base = declarative_base()

class AbstractModel:
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset':'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }


class ClusterName(IClusterName):
    name: str = None

    def __init__(self, name):
        self.name = name

    def get(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class Meta:
    create_datetime: str = Column(DateTime(timezone=True), default=datetime.now())
    last_updated_datetime: str = Column(DateTime(timezone=True), onupdate=func.now(), default=datetime.now())
    meta_json: str = Column(Text, default='')
    comment: str = Column(String(255), default='')

    def get_create_datetime(self) -> datetime:
        return datetime.strptime(self.create_datetime, '%Y-%m-%d %H:%M:%S')

    def get_last_updated_datetime(self) -> datetime:
        return datetime.strptime(self.last_updated_datetime, '%Y-%m-%d %H:%M:%S')

    def get_meta_json(self) -> str:
        return self.meta_json

    def get_comment(self) -> str:
        return self.comment


class ClusterSpanImp(Base, IClusterSpan, Meta, AbstractModel):
    __tablename__ = "cluster_span"
    __table_args__ = (
        UniqueConstraint(
        'from_datetime', 'to_datetime', name='_from_to_datetime_uc'
        ),
    )

    id: int = Column(Integer, primary_key=True)
    type: str = Column(Enum(
        SpanTypes.ByDay, SpanTypes.ByMonth, SpanTypes.BySemester, SpanTypes.ByYear, SpanTypes.ByWeek
    ))
    from_datetime = Column(DateTime(timezone=True))
    to_datetime = Column(DateTime(timezone=True))

    def get_id(self) -> int:
        return self.id

    def get_type(self) -> str:
        return self.type

    def get_spans_from(self) -> datetime:
        return self.from_datetime

    def get_spans_to(self) -> datetime:
        return self.to_datetime


class AlgorithmInfoImp(Base, IAlgorithmInfo, Meta, AbstractModel):
    __tablename__ = "algorithm_info"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(60), unique=True)
    clusters: relationship(
        'ClusterInfoImp', backref='algorithm_info', lazy='subquery'
    )

    def get_clusters(self) -> []:
        return self.name

    def get_name(self) -> str:
        return self.name


class ClusterInfoImp(Base, IClusterInfo, Meta, AbstractModel):
    __tablename__ = "cluster_info"

    id: int = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    algorithm_id: int = Column(Integer, ForeignKey(AlgorithmInfoImp.id))
    algorithm = relationship(
        'AlgorithmInfoImp', foreign_keys=[algorithm_id], primaryjoin='AlgorithmInfoImp.id == ClusterInfoImp.algorithm_id'
    )

    span_id: int = Column(Integer, ForeignKey(ClusterSpanImp.id))
    span = relationship(
        'ClusterSpanImp', foreign_keys=[span_id], primaryjoin='ClusterSpanImp.id == ClusterInfoImp.span_id'
    )

    def get_name(self) -> str:
        return self.cluster_name

    def get_span(self) -> IClusterSpan:
        return self.span

    def get_algorithm_info(self) -> IAlgorithmInfo:
        return self.algorithm

    def get_id(self) -> int:
        return self.id


# Index('user_username_index', func.lower(User.username), unique=True)


class ClusteredUsers(Base, Meta, AbstractModel):
    __tablename__ = "clusters_users"

    user_id: int = Column(Integer, primary_key=True)
    cluster_id: int = Column(Integer, ForeignKey(ClusterInfoImp.id), primary_key=True)
    cluster = relationship(
        'ClusterInfoImp', foreign_keys=[cluster_id], primaryjoin='ClusterInfoImp.id == ClusteredUsers.cluster_id'
    )


class LastUpdateRecord(Base, AbstractModel):
    __tablename__ = "record_update_history"

    id: int = Column(Integer, primary_key=True)
    last_processed_id: int = Column(Integer, server_default='0', unique=True, nullable=False, index=True)
    # last_processed_id: int = Column(Integer, server_default='0', nullable=False)
    last_processed__updated: str = Column(DateTime)