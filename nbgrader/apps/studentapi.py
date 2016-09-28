#TODO: integrate this to nbgrader/api.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table
from ..api import Assignment, SubmittedAssignment, SubmittedNotebook, Grade, Student


Base = declarative_base()
db_url = 'sqlite:///gradebook.db'
session = None


def init_database(db_url=db_url):
    global session
    """
    Initialise the database:
    Connect to database with given url
    creates new table 'groupmember' if not exists
    saves current session to 'self.session'
    :return:
    """
    #TODO mode_debug = False
    mode_debug = False
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

init_database()


class Groupmember(Base):
    """
    Class for sqlalchemie to access the database
    """
    __tablename__ = 'groupmember'

    #id of submitted assignment
    sub_notebook_id = Column(String, primary_key=True)

    #i.e. Matrikelnr
    groupmember_id = Column(String, primary_key=True)
    mail = Column(String)

    def __repr__(self):
        return "<Groupmeber(identifier='%s', notebook=%s, mail='%s'" \
               % (self.groupmember_id, self.sub_notebook_id, self.mail)


def get_assignment_id(assignment_name):
    """
    Database has to be connected with 'init_database'
    :param assignment_name:
    :return: assignment id from database
    """
    return session.query(Assignment.id).filter(Assignment.name == assignment_name).first()[0]


def get_assignment_name(assignment_id):
    return session.query(Assignment.name).filter(Assignment.id == assignment_id).first()[0]


def get_assignment_id_from_sub_ass_id(submitted_assignment_id):
    return session.query(SubmittedAssignment.assignment_id).filter(
        SubmittedAssignment.id == submitted_assignment_id).first()[0]


def get_submitted_nb_id(assignment_id):
    return session.query(SubmittedNotebook.id).filter(
        SubmittedNotebook.assignment_id == assignment_id).first()[0]


def get_assignment_list():
    return list(map(lambda x: x[0], session.query(Assignment.name).all()))


def get_points(sub_notebook_id):
    grades = session.query(Grade).filter(Grade.notebook_id == sub_notebook_id)
    res = 0
    for g in grades:
        if g.auto_score is None:
            res += g.manual_score
        elif g.manual_score is None:
            res += g.auto_score
        else:
            res += min(g.auto_score, g.manual_score)
    return res


def get_student_list_point():
    res = dict()
    ass_list = get_assignment_list()
    for p in session.query(Groupmember).all():
        if p.groupmember_id not in res:
            res[p.groupmember_id] = dict(zip(ass_list, [0 for _ in ass_list]))
        res[p.groupmember_id][get_assignment_name(get_assignment_id_from_sub_ass_id(p.sub_notebook_id))] = \
            get_points(get_submitted_nb_id(p.sub_notebook_id))
    return res


def get_student_list_mail():
    res = dict()
    ass_list = get_assignment_list()
    for p in session.query(Groupmember).all():
        if p.groupmember_id not in res:
            res[p.groupmember_id] = dict(zip(ass_list, ["" for _ in ass_list]))
        res[p.groupmember_id][get_assignment_name(get_assignment_id_from_sub_ass_id(p.sub_notebook_id))] = \
            p.mail
    return res