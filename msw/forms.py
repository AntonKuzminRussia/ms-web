from django.forms import ModelForm, ValidationError
from msw.models import Filters, Accounts
import re
import imaplib

class AbstractFilterForm(ModelForm):
    class Meta:
        model = Filters
        fields = ['name', 'target', 'type', 'content']

    def clean_content(self):
        if self.cleaned_data['type'] == 'regex':
            try:
                re.compile(self.cleaned_data['content'])
            except re.error:
                raise ValidationError("Bad regexp")
        return self.cleaned_data['content']

class EditFilterForm(AbstractFilterForm):
    pass

class AddFilterForm(AbstractFilterForm):
    pass

class AbstractAccountForm(ModelForm):
    class Meta:
        model = Accounts
        fields = ['host', 'ssl', 'login', 'password', 'check_interval', 'active']

    def clean_password(self):
        try:
            imap = imaplib.IMAP4_SSL(self.cleaned_data['host']) if \
                self.cleaned_data['ssl'] else \
                imaplib.IMAP4(self.cleaned_data['host'])
            imap.login(self.cleaned_data['login'], self.cleaned_data['password'])
        except BaseException as ex:
            raise ValidationError("IMAP error: " + str(ex))
        del imap

        return self.cleaned_data['password']

class EditAccountForm(AbstractAccountForm):
    pass

class AddAccountForm(AbstractAccountForm):
    pass