from tastypie.resources import ModelResource
from msw.models import Accounts, Folders, Filters, Letters, Attachments, FiltersFinds, AccountsErrors
from django.http import HttpResponse
from tastypie.authorization import Authorization
from tastypie import resources, fields
from django.db.models import Count
import html
import time
import datetime
from bs4 import BeautifulSoup
from django.conf import settings

def build_content_type(format, encoding='utf-8'):
    """
    Appends character encoding to the provided format if not already present.
    """
    if 'charset' in format:
        return format

    return "%s; charset=%s" % (format, encoding)

class MyModelResource(resources.ModelResource):
    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Extracts the common "which-format/serialize/return-response" cycle.

        Mostly a useful shortcut/hook.
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)

class AccountsResource(MyModelResource):
    class Meta:
        queryset = Accounts.objects.all()
        resource_name = 'accounts'

class AccountsErrorsResource(MyModelResource):
    class Meta:
        filtering = {
            "account_id": ('exact',),
        }
        queryset = AccountsErrors.objects.all().order_by('-when_add')
        resource_name = 'accounts-errors'

    def dehydrate(self, bundle):
        today_timestamp = datetime.date.today().strftime('%s')
        bundle.data['is_today'] = int(int(today_timestamp) <= int(bundle.data['when_add']))
        bundle.data['when_add'] = datetime.datetime.fromtimestamp(int(bundle.data['when_add'])).strftime('%Y-%m-%d %H:%M:%S')
        return bundle


class StatsResource(MyModelResource):
    class Meta:
        queryset = Accounts.objects.all()
        resource_name = 'stats'

    def dehydrate(self, bundle):
        bundle.data['letters_count'] = Accounts.get_letters_count(bundle.data['id'])
        bundle.data['filters_finds_count'] = Accounts.get_filters_finds_count(bundle.data['id'])
        bundle.data['attachments_count'] = Accounts.get_attachments_count(bundle.data['id'])
        bundle.data['errors_count'] = Accounts.get_accerrs_count(bundle.data['id'])
        bundle.data['letters_count_today'] = Accounts.get_letters_count(bundle.data['id'], True)
        bundle.data['filters_finds_count_today'] = Accounts.get_filters_finds_count(bundle.data['id'], True)
        bundle.data['attachments_count_today'] = Accounts.get_attachments_count(bundle.data['id'], True)
        bundle.data['errors_count_today'] = Accounts.get_accerrs_count(bundle.data['id'], True)
        return bundle

class FiltersResource(MyModelResource):
    class Meta:
        queryset = Filters.objects.all()
        resource_name = 'filters'
    def dehydrate(self, bundle):
        bundle.data['letters_count'] = FiltersFinds.objects.filter(filter_id__exact=bundle.data['id']).count()
        return bundle

class FoldersResource(MyModelResource):
    class Meta:
        filtering = {
            "account_id": ('exact',),
        }
        queryset = Folders.objects.all()
        resource_name = 'folders'
    def dehydrate(self, bundle):
        bundle.data['letters_count'] = Letters.objects.filter(folder_id__exact=bundle.data['id']).count()
        return bundle

class SubjectsResource(MyModelResource):
    class Meta:
        filtering = {
            "folder_id": ('exact',),
        }
        queryset = Letters.objects.all().order_by('-date')
        resource_name = 'subjects'
        authorization = Authorization()
        max_limit = None
        fields = ['id', 'subject', 'folder_id', 'date', 'has_attachments']

    def dehydrate(self, bundle):
        today_timestamp = datetime.date.today().strftime('%s')
        if len(bundle.data['subject']) == 0:
            bundle.data['subject'] = "= NO SUBJECT ="
        bundle.data['is_today'] = int(int(today_timestamp) <= int(bundle.data['date']))
        bundle.data['timestamp'] = datetime.datetime.fromtimestamp(int(bundle.data['date'])).strftime('%Y-%m-%d %H:%M:%S')
        return bundle

class LettersResource(MyModelResource):
    class Meta:
        filtering = {
            "folder_id": ('exact',),
        }
        queryset = Letters.objects.all()
        resource_name = 'letters'
        authorization = Authorization()
        max_limit = None

    def dehydrate(self, bundle):
        raw_body = open(settings.BODIES_PATH + bundle.data['hash'], encoding='utf8').read()
        bundle.data['body'] = html.escape(raw_body)

        body_clean = BeautifulSoup(raw_body).text
        body_clean.replace("\r\n", "\n")
        while body_clean.count("\n\n"):
            body_clean = body_clean.replace("\n\n", "\n")
        body_clean = body_clean.replace("\n", "<br/>")
        bundle.data['body_clean'] = body_clean

        bundle.data['timestamp'] = datetime.datetime.fromtimestamp(int(bundle.data['date'])).strftime('%Y-%m-%d %H:%M:%S')
        return bundle

class AttachmentsResource(MyModelResource):
    class Meta:
        filtering = {
            "letter_id": ('exact',),
        }
        queryset = Attachments.objects.all()
        resource_name = 'attachments'

class AttachmentsListResource(MyModelResource):
    class Meta:
        filtering = {
            "ext": ('exact',)
        }
        queryset = Attachments.objects.all()
        resource_name = 'attachments-list'

    def dehydrate(self, bundle):
        letter = Letters.objects.get(id=bundle.data['letter_id'])
        bundle.data['letter'] = {
            'id': letter.id,
            'subject': letter.subject if len(letter.subject) else "= NO SUBJECT =",
            'date': letter.date
        }
        return bundle


class FiltersFindsResource(MyModelResource):
    class Meta:
        filtering = {
            "letter_id": ('exact',),
            "filter_id": ('exact',),
        }
        fields = ['filter_id']
        queryset = FiltersFinds.get_filters_ids_only()
        resource_name = 'filters-finds'

class FiltersFindsLettersResource(MyModelResource):
    class Meta:
        #ordering = ['-letter_date']
        filtering = {
            "letter_id": ('exact',),
            "filter_id": ('exact',),
        }

        queryset = FiltersFinds.objects.all().order_by('-when_add')
        resource_name = 'filters-finds-letters'

    def dehydrate(self, bundle):
        today_timestamp = datetime.date.today().strftime('%s')
        letter = Letters.objects.get(id=bundle.data['letter_id'])
        bundle.data['letter_id'] = letter.id
        bundle.data['letter_subject'] = letter.subject
        bundle.data['letter_is_today'] = int(int(today_timestamp) <= int(letter.date))
        bundle.data['letter_date'] = letter.date
        bundle.data['letter_has_attachments'] = letter.has_attachments
        bundle.data['letter_timestamp'] = datetime.datetime.fromtimestamp(int(letter.date)).strftime('%Y-%m-%d %H:%M:%S')

        filter = Filters.objects.get(id=bundle.data['filter_id'])
        bundle.data['filter_target'] = filter.target
        bundle.data['filter_type'] = filter.type
        bundle.data['filter_content'] = filter.content

        return bundle
