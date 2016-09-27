from .baseapp import NbGrader
import json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table

import os



aliases = {}
flags = {}

class StudentgradeApp(NbGrader):

    name = u'nbgrader-studentgrade'
    description = u'Save connection between submitted assignments and students (with identifier)'

    aliases = aliases
    flags = flags

    examples = """
        You can run `nbgrader studentgrade` just in the course folder.
        To connect the students identifier (written by the students in the first cell of the
        collected notebook with syntax:

            identifier1 student1@mail.de
            identifier2 student2@mail.de
                .
                .
                .

        ) for their submittions on asignment01 run:

            nbgrader studentgrade asignment01

        This also saves the mailadress to the datebase for mailing the results with
        nbgrader studentmail

        If the syntax is not correct in one line, the other lines will not be effected.
        If there is no correct line, this call will not do anything.
        If there is no mailadress, the identifier will still be saved.
        The identifier must only contain letters, numbers and underscores. No spaces or
        other special signs.

        """



    def _classes_default(self):
        classes = super(StudentgradeApp, self)._classes_default()
        classes.append(StudentgradeApp)
        return classes

    def start(self):
        super(StudentgradeApp, self).start()

        if len(self.extra_args) != 1:
            self.fail("Assignment id not provided. Usage: nbgrader studentgrade assinment_id")
        self.session = init_database(db_url='sqlite:///gradebook.db')
        assignment = self.extra_args[0]
        rootpath = './autograded'
        notepath = self.get_notepath(assignment, rootpath)
        #print("notepath", notepath)
        for p in notepath:
            note = json.load(open(p["file"]))
            id_note = note["cells"][0]["source"]
            for st in id_note:
                st = str.replace(st, "\n", "")
                st = str.split(st, " ", 1)
                assignment_id = self.get_assignment_id(assignment)
                if len(st) > 1:
                    self.save_identifier(st[0], p["acc"], assignment_id, st[1])
                elif len(st) > 0:
                    self.save_identifier(st[0], p["acc"], assignment_id)
        self.session.commit()
        gr = self.session.query(Groupmember).all()
        print("len", len(gr))
        for g in self.session.query(Groupmember).all():
            print("saved ids", g)

    def save_identifier(self, identifier, account, assignment_id, mail=""):
        """
        Saves groupmeber entry to database. Database as to be connected with 'init_database'
        :param identifier: unique identifier of each groupmember (like matrikel number)
        :param account: name of the group account
        :param assignment_id: id of assignment where the groubmembers shell be collected
        :param mail: mail address of that groupmember (optional)
        :return:
        """
        #print("save id:", identifier, account)
        sub_ass = self.session.query(SubmittedAssignment).filter(
                SubmittedAssignment.assignment_id == assignment_id,
                SubmittedAssignment.student_id == account
            ).first()
        #print("sub_ass", sub_ass)
        if sub_ass is not None:
            if self.session.query(Groupmember).filter(
                            Groupmember.sub_notebook_id == sub_ass.id,
                            Groupmember.groupmember_id == identifier
            ).first() is not None:
                #print("exists", identifier, sub_ass.id)
                return
            new_mem = Groupmember(sub_notebook_id=sub_ass.id, groupmember_id=identifier, mail=mail)
            self.session.add(new_mem)



    def get_notepath(self, assignment, root_path):
        """
        :param assignment: assignment name
        :param root_path: path of folder were the accounts have their sub folders
        :return: a list of dicts with each two entry
            'acc': name of the student account
            'file': path of the notebook file where the students have written the identifier
                    and mail addresses of all group members of in that assignment
        """
        res = []
        for p in os.listdir(root_path):

            #if os.path.isdir(p):
                np = dict()
                np['acc'] = p
                assignment_dir = os.path.join(root_path, p, assignment)
                #print("assignment_dir", assignment_dir)
                if os.path.exists(assignment_dir):
                    for f in os.listdir(assignment_dir):
                        if f.rfind('.ipynb') != -1:
                            np['file'] = os.path.join(assignment_dir, f)
                            break
                    #print("notepath np:", np)
                    res += [np]
        return res

    def get_assignment_id(self, assignment_name):
        """
        Database has to be connected with 'init_database'
        :param assignment_name:
        :return: assignment id from database
        """
        return self.session.query(Assignment.id).filter(Assignment.name == assignment_name).first()[0]


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
