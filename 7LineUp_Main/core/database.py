from django.conf import settings
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base

# Get the database URL from Django settings
DATABASE_URL = f"sqlite:///{settings.DATABASES['default']['NAME']}"

engine = create_engine(DATABASE_URL, echo=False)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = Session.query_property()

# Association table for team members
team_members = Table('team_members', Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id')),
    Column('member_id', Integer, ForeignKey('members.id'))
)

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    ingame = Column(String(100))
    role = Column(String(50))
    notes = Column(Text)

    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', ingame='{self.ingame}')>"

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    rank = Column(String(50))
    role = Column(String(50))  # team role
    members = relationship('Member', secondary=team_members, backref='teams')

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', rank='{self.rank}')>"

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    opponent = Column(String(100), nullable=False)
    match_date = Column(DateTime, nullable=False)
    rules = Column(String(200))
    win = Column(Boolean, nullable=True)  # True for win, False for loss, None for draw
    notes = Column(Text)
    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship('Team', backref='matches')

    def __repr__(self):
        return f"<Match(id={self.id}, opponent='{self.opponent}', date='{self.match_date}', win={self.win})>"