"""
Модуль моделей базы данных.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from server.database.confdb import Base


class Follow(Base):
    """
    Модель подписки, представляющая связь между пользователями.

    Атрибуты:
        follower_id (int): Идентификатор пользователя, который подписывается.
        following_id (int): Идентификатор пользователя, на которого подписываются.
    """

    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    following_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class User(Base):
    """
    Модель пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        apikey (str): Уникальный API-ключ пользователя.
        name (str): Имя пользователя, ограниченное 50 символами.

    Связи:
        tweets (list[Tweet]): Список твитов, созданных пользователем.
        likes (list[Like]): Список лайков пользователя.
        followers (list[User]): Список пользователей, которые подписаны на данного пользователя.
        following (list[User]): Список пользователей, на которых подписан данный пользователь.
    """

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
    """
    Модель твита.

    Атрибуты:
        id (int): Уникальный идентификатор твита.
        author_id (int): Уникальный идентификатор автора твита.
        content (str): Текст содержащийся в твите.

    Связи:
        author (User): Модель автора твита.
        likes (list[Like]): Список лайков пользователя.
        media (list[Media]): Список медия связанный с твитов.
    """

    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String(280), nullable=False)

    author = relationship("User", back_populates="tweets")
    likes = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="tweet", cascade="all, delete-orphan")


class Like(Base):
    """
    Модель лайка, представляющая связь между пользователем и твитом.

    Атрибуты:
        id (int): Уникальный идентификатор лайка.
        user_id (int): Идентификатор пользователя, который поставил лайк.
        tweet_id (int): Идентификатор твита, который был лайкнут.

    Связи:
        user (User): Пользователь, который поставил лайк.
        tweet (Tweet): Твит, который был лайкнут.
    """

    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tweet_id = Column(Integer, ForeignKey("tweets.id"))

    user = relationship("User", back_populates="likes")
    tweet = relationship("Tweet", back_populates="likes")


class Media(Base):
    """
    Модель медиафайла, связанного с твитом.

    Атрибуты:
        id (int): Уникальный идентификатор медиафайла.
        file_path (str): Путь к файлу на сервере.
        file_url (str): URL-адрес для доступа к файлу.
        tweet_id (int): Идентификатор твита, с которым связан медиафайл.

    Связи:
        tweet (Tweet): Твит, к которому относится медиафайл.
    """

    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
    tweet = relationship("Tweet", back_populates="media")
