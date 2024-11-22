from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from server.database.confdb import Base


class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    following_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    apikey = Column(String, unique=True, nullable=False)
    name = Column(String(50), nullable=False)

    tweets = relationship("Tweet", back_populates="author")
    likes = relationship("Like", back_populates="user")
    followers = relationship(
        "User",
        secondary="follows",
        primaryjoin=id == Follow.following_id,
        secondaryjoin=id == Follow.follower_id,
        backref="following",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String(280), nullable=False)

    author = relationship("User", back_populates="tweets")
    likes = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="tweet", cascade="all, delete-orphan")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tweet_id = Column(Integer, ForeignKey("tweets.id"))

    user = relationship("User", back_populates="likes")
    tweet = relationship("Tweet", back_populates="likes")


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
    tweet = relationship("Tweet", back_populates="media")
