import os
from django.conf import settings
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base

# Ưu tiên dùng DATABASE_URL từ biến môi trường (Postgres khi host trên Render).
# Nếu không có biến này (ví dụ khi chạy ở máy local), fallback về SQLite như cũ.
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Một số nhà cung cấp (Render/Heroku) trả URL dạng "postgres://",
    # nhưng SQLAlchemy hiện tại yêu cầu "postgresql://".
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
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

# Tự động tạo bảng nếu chưa tồn tại (áp dụng cho cả SQLite lẫn Postgres).
# An toàn khi gọi nhiều lần: nếu bảng đã có sẵn, lệnh này sẽ bỏ qua, không xóa dữ liệu cũ.
Base.metadata.create_all(engine)