from .baseapp import NbGrader
from .studentapi import *
aliases = {}
flags = {}


class StudentMailApp(NbGrader):

    name = u'nbgrader-studentmail'
    description = u'Send mails with results to given mailadress from student'

    aliases = aliases
    flags = flags

    examples = """
        Here should be an example for studentmail

        """

    def _classes_default(self):
        classes = super(StudentMailApp, self)._classes_default()
        classes.append(StudentMailApp)
        return classes

    def start(self):
        super(StudentMailApp, self).start()
        if len(self.extra_args) != 1:
            self.fail("Assignment id not provided. Usage: nbgrader studentmail assinment_id")

        if self.extra_args[0] not in get_assignment_list():
            self.fail("Assingment id does not exist")

        points = get_student_list_point()
        mail = get_student_list_mail()

        for p in points:
            self.send_mail_to(mail[p][self.extra_args[0]], "Matrikel Nr: %s, Punkte in %s: %f" % (
                p, self.extra_args[0], points[p][self.extra_args[0]]))

    def send_mail_to(self, adress, message):
        print("Send mail", adress, message)
