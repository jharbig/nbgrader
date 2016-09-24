from .baseapp import NbGrader
import json

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

#TODO Path for Submited Notebooks, inclusiv accountname (from pathname)
        notepath = [{"acc": "GP1_00_01", "file": "./B2_A1(1).ipynb"}]
        assignment = self.extra_args[0]
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