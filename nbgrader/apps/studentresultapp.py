from .baseapp import NbGrader
from .studentapi import *

aliases = {}
flags = {}


class StudentResultApp(NbGrader):

    name = u'nbgrader-studentmail'
    description = u'Send mails with results to given mailadress from student'

    aliases = aliases
    flags = flags

    examples = """
        Here should be an example for studentresult

        """

    def _classes_default(self):
        classes = super(StudentResultApp, self)._classes_default()
        classes.append(StudentResultApp)
        return classes

    def start(self):
        super(StudentResultApp, self).start()
        print("Results:")
        students = get_student_list_point()
        for p in sorted(students):
            print(p, students[p])

        #TODO return results for all students as JSON
        # (identifier, points_asignment01, points_asignment02, ..., points_sum)
