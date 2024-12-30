from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, exc
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from view import View

Base = declarative_base()

class Author(Base):
    __tablename__ = 'author'
    author_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    def __repr__(self):
        return f"<Author(name='{self.name}', surname='{self.surname}')>"

class Collection(Base):
    __tablename__ = 'collection'
    collection_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    view = Column(String, nullable=False)

    def __repr__(self):
        return f"<Collection(name='{self.name}', type='{self.type}', view='{self.view}')>"

class Edition(Base):
    __tablename__ = 'edition'
    edition_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    number_of_pages = Column(Integer, nullable=False)
    languages = Column(String, nullable=False)

    def __repr__(self):
        return f"<Edition(name='{self.name}', branch='{self.branch}', pages='{self.number_of_pages}', languages='{self.languages}')>"

class AuthorCollectionEdition(Base):
    __tablename__ = 'author_collection_edition'
    author_id = Column(Integer, ForeignKey('author.author_id'), primary_key=True)
    edition_id = Column(Integer, ForeignKey('edition.edition_id'), primary_key=True)
    author = relationship("Author", backref="author_collections")
    edition = relationship("Edition", backref="edition_collections")

    def __repr__(self):
        return f"<AuthorCollectionEdition(author_id='{self.author_id}', edition_id='{self.edition_id}')>"

class AuthorCollectionEditionED(Base):
    __tablename__ = 'author_collection_edition_ed'
    edition_id = Column(Integer, ForeignKey('edition.edition_id'), primary_key=True)
    collection_id = Column(Integer, ForeignKey('collection.collection_id'), primary_key=True)
    date = Column(String)
    edition = relationship("Edition", backref="edition_collections_ed")
    collection = relationship("Collection", backref="collection_editions")

    def __repr__(self):
        return f"<AuthorCollectionEditionED(edition_id='{self.edition_id}', collection_id='{self.collection_id}', date='{self.date}')>"


class Model:
    def __init__(self):
        self.engine = create_engine("postgresql://postgres:1234@localhost/science_test")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.view = View()

    def get_all(self, table_class):
        session = self.Session()
        try:
            results = session.query(table_class).all()
            return results
        except exc.SQLAlchemyError as e:
            self.view.show_message(str(e))
        finally:
            session.close()


    def add_data(self, table_name, data):
        session = self.Session()

        table_classes = {
            "Author": Author,
            "Collection": Collection,
            "Edition": Edition,
            "Author_Collection_Edition": AuthorCollectionEdition,
            "Author_Collection_Edition_ED": AuthorCollectionEditionED
        }

        table_class = table_classes.get(table_name)
        if not table_class:
            self.view.show_message(f"Invalid table name: {table_name}")
            return

        try:
            obj = table_class()
            for key, value in data.items():
                setattr(obj, key, value)
            session.add(obj)
            session.commit()
            self.view.show_message("Added successfully!")
        except exc.IntegrityError as e:
            session.rollback()
            self.view.show_message(f"ERROR: Integrity constraint violated.\n{e}")
        except exc.SQLAlchemyError as e:
            session.rollback()
            self.view.show_message(str(e))
        finally:
            session.close()


    def update_data(self, table_class, data, condition):
        session = self.Session()
        try:
            obj = session.query(table_class).filter_by(**condition).first()
            if obj:
                for key, value in data.items():
                    setattr(obj, key, value)
                session.commit()
                self.view.show_message("Updated successfully!")
            else:
                self.view.show_message("No record found to update.")
        except exc.SQLAlchemyError as e:
            session.rollback()
            self.view.show_message(str(e))
        finally:
            session.close()

    def delete_data(self, table_class, condition):
        session = self.Session()
        try:
            obj = session.query(table_class).filter_by(**condition).first()
            if obj:
                session.delete(obj)
                session.commit()
                self.view.show_message("Deleted successfully!")
            else:
                self.view.show_message("No record found to delete.")
        except exc.SQLAlchemyError as e:
            session.rollback()
            self.view.show_message(str(e))
        finally:
            session.close()
