#TODO: integrate this to nbgrader/api.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table


Base = declarative_base()

def init_database(db_url):
    """
    Initialise the database:
    Connect to database with given url
    creates new table 'groupmember' if not exists
    saves current session to 'self.session'
    :return:
    """
    #TODO mode_debug = False
    mode_debug = True
    engine = create_engine(db_url, echo=mode_debug)
    Session = sessionmaker(bind=engine)
    session = Session()

    #Add table 'groupmember' if not exist
    metadata = MetaData()
    groupemember = Table('groupmember', metadata,
                         Column('sub_notebook_id', String, primary_key=True),
                         Column('groupmember_id', String, primary_key=True),
                         Column('mail', String)
    )
    metadata.create_all(engine)
    return session


class Groupmember(Base):
    """
    Class for sqlalchemie to access the database
    """
    __tablename__ = 'groupmember'

    sub_notebook_id = Column(String, primary_key=True)
    groupmember_id = Column(String, primary_key=True)
    mail = Column(String)

    def __repr__(self):
        return "<Groupmeber(identifier='%s', notebook=%s, mail='%s'" \
               % (self.groupmember_id, self.sub_notebook_id, self.mail)


class Assignment(Base):
    """
    Class for sqlalchemie to access the database
    """
    __tablename__ = 'assignment'

    id = Column(String, primary_key=True)
    name = Column(String)
    duedate = Column(DateTime)


class SubmittedAssignment(Base):
    """
    Class for sqlalchemie to access the database
    """
    __tablename__ = 'submitted_assignment'

    id = Column(String, primary_key=True)
    assignment_id = Column(String)
    student_id = Column(String)
    timestamp = Column(DateTime)
    extension = Column(DateTime)

    def __repr__(self):
        return "<SubmittedAssignment(id='%s', assignment_id='%s', studnet_id='%s', timestamp='%s', extension='%s')" \
               % (self.id, self.assignment_id, self.student_id, self.timestamp, self.extension)