
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc

from utils import generate_hash_key
import settings

Base = declarative_base()


class WordCounter(Base):
    __tablename__ = 'word_counter'
    word_key = Column(String(250), primary_key=True)
    word = Column(String(250))
    frequency = Column(Integer)

    def __repr(self):
        return self.word_key

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


def save_word_list_to_db(words, encryptor):
    if words:
        for word, frequency in words:
            try:
                word_counter = db_session.query(WordCounter).filter_by(word_key=generate_hash_key(word)).one()
                word_counter.frequency += frequency
            except NoResultFound:
                word_counter = WordCounter(
                        word_key=generate_hash_key(word),
                        word=encryptor.encrypt_content(word),
                        frequency=frequency)
            db_session.add(word_counter)
        db_session.commit()


def read_word_counter_list(decryptor):
    entities = db_session.query(WordCounter).order_by(desc(WordCounter.frequency))
    words = []
    for entity in entities:
        words.append({
            'word': decryptor.decrypt_content(entity.word),
            'frequency': entity.frequency
        })
    return words


def reset_word_counter():
    entities = db_session.query(WordCounter).all()
    for item in entities:
        db_session.delete(item)
    db_session.commit