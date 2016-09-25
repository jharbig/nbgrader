from .baseapp import NbGrader
import json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean
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

        if len(self.extra_args) != 2:
            self.fail("Assignment id not provided. Usage: nbgrader studentgrade assinment_id")

#TODO Path for Submited Notebooks, inclusiv accountname (from pathname)
        notepath = [{"acc": "GP1_00_01", "file": "./B2_A1(1).ipynb"}]

        assignment = self.extra_args[0]
        rootpath = ':/autograded'
        notepath = get_notepath(assignment, rootpath)
        for p in notepath:
            note = json.load(open(p["file"]))
            id_note = note["cells"][0]["source"]
            for st in id_note:
                st = str.replace(st, "\n", "")
                st = str.split(st, " ", 1)
                if len(st) > 1:
                    self.save_identifier(st[0], p["acc"], assignment, st[1])
                elif len(st) > 0:
                    self.save_identifier(st[0], p["acc"], assignment)

    def save_identifier(self, identifier, account, assignment, mail=""):
        print("save id", identifier, account, assignment, mail)
        #TODO write to DB

    def init_database(self):
        db_url = 'sqlite:///gradebook.db'
        #TODO mode_debug = False
        mode_debug = True
        Session = sessionmaker(bind=engine)
        self.session = Session()

        #Add table 'groupmember' if not exist
        metadata = MetaData()
        groupemember = Table('groupmember', metadata,
                             Column('sub_notebook_id', String, primary_key=True),
                             Column('groupmember_id', String),
                             Column('mail', String)
        )
        metadata.create_all(engine)

    def get_notepath(self, assignment, root_path):
        res = []
        for p in os.listdir(root_path):
            if os.path.isdir(p):
                np = dict()
                np['acc'] = p
                assignment_dir = os.path.join(root_path, p, assignment)
                if os.path.exists(assignment_dir):
                    for f in os.listdir(assignment_dir):
                        if f.rfind('.ipynb') != -1:
                            np['file'] = os.path.join(assignment_dir, f)
                            break
                    res += [np]
        return res


Base = declarative_base()
class Groupmember(Base):
    __tablename__ = 'groupmember'

    sub_notebook_id = Column(String, primary_key=True)
    groupmember_id = Column(String)
    mail = Column(String)

    def __repr__(self):
        return "<Groupmeber(identifier='%s', notebook=%s, mail='%s'" % (self.groupmember_id, self.sub_notebook_id, self.mail)

class Student(Base):
    __tablename__ = 'student'

    id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)

    def __repr__(self):
        return "<Student(id='%s', name='%s, %s')>" % (self.id, self.first_name, self.last_name)