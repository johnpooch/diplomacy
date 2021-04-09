class DiplomacyManagementCommandMixin:

    def prompt(self):
        if not self.noinput:
            response = input('Are you sure you want to continue? [Y/n]: ')
            if response not in ['y', 'Y']:
                self.stdout.write('Exiting...')
                return