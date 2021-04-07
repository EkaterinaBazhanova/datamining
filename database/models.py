from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, UnicodeText


Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False, unique=False)
    picture = Column(String, nullable=False, unique=False)
    date = Column(String, nullable=False, unique=False)
    writer_id = Column(Integer, ForeignKey("writer.id"))
    writer = relationship("Writer")
    tags = relationship("Tag", secondary=tag_post)
    comments = relationship("Comment")

class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(Integer, nullable=False, unique=True)
    comment_writer = Column(String, nullable=False, unique=False)
    comment_text = Column(UnicodeText, nullable=False, unique=False)
    post_id = Column(Integer, ForeignKey("post.id"))
    posts = relationship(Post)

class Writer(Base):
    __tablename__ = "writer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=False)
    posts = relationship(Post)


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=False)
    posts = relationship(Post, secondary=tag_post)