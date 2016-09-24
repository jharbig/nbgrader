from .baseapp import NbGrader

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
        message = "Hier die Ergebnisse"
        for adress in self.get_mail_adresses():
            self.send_mail_to(adress, message)

    def get_mail_adresses(self):
        #TODO get mail adresses and solutions from DB
        return ["abc@mail.de"]

    def send_mail_to(self, adress, message):
        print("Send mail", adress, message)
