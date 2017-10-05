from django.db import models
import time
import datetime
from django.db import connection


class Accounts(models.Model):
    class Meta:
        db_table = "accounts"
        unique_together = ["host", "login"]
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    host = models.CharField(max_length=100)
    ssl = models.BooleanField()
    active = models.BooleanField(default=1)
    in_work = models.BooleanField(default=0)
    last_checked = models.IntegerField(default=0)
    check_interval = models.IntegerField(default=3600)

    @staticmethod
    def get_letters_count(id, today=False):
        today_timestamp = datetime.date.today().strftime('%s')
        sql = ("SELECT COUNT(l.id) FROM `accounts` a " 
                  "JOIN `folders` f ON f.account_id = a.id " 
                  "JOIN `letters` l ON l.folder_id = f.id " 
                  "WHERE a.id = " + str(id))
        if today:
            sql += " AND l.when_add > " + str(today_timestamp)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
        return row[0]

    @staticmethod
    def get_filters_finds_count(id, today=False):
        today_timestamp = datetime.date.today().strftime('%s')
        sql = ("SELECT COUNT(l.id) "
               "FROM `accounts` a "
               "JOIN `folders` f ON f.account_id = a.id "
               "JOIN `letters` l ON l.folder_id = f.id "
               "JOIN `filters_finds` ff ON ff.letter_id = l.id "
               "WHERE a.id = " + str(id))
        if today:
            sql += " AND l.when_add > " + str(today_timestamp)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
        return row[0]

    @staticmethod
    def get_attachments_count(id, today=False):
        today_timestamp = datetime.date.today().strftime('%s')
        sql = ("SELECT COUNT(l.id) "
               "FROM `accounts` a "
               "JOIN `folders` f ON f.account_id = a.id "
               "JOIN `letters` l ON l.folder_id = f.id "
               "JOIN `attachments` at ON at.letter_id = l.id "
               "WHERE a.id = " + str(id))
        if today:
            sql += " AND l.when_add > " + str(today_timestamp)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
        return row[0]

    @staticmethod
    def get_accerrs_count(id, today=False):
        today_timestamp = datetime.date.today().strftime('%s')
        sql = ("SELECT COUNT(id) FROM `accounts_errors` WHERE account_id = " + str(id))
        if today:
            sql += " AND when_add > " + str(today_timestamp)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
        return row[0]

class AccountsErrors(models.Model):
    class Meta:
        db_table = "accounts_errors"
        verbose_name = "AccountError"
        verbose_name_plural = "AccountsErrors"

    id = models.IntegerField(primary_key=True)
    account_id = models.IntegerField()
    when_add = models.IntegerField()
    error = models.CharField(max_length=200)

class Folders(models.Model):
    class Meta:
        db_table = "folders"
        verbose_name = "Folder"
        verbose_name_plural = "Folders"

    id = models.IntegerField(primary_key=True)
    account_id = models.IntegerField()
    parent_id = models.IntegerField()
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    server_name = models.CharField(max_length=200)
    last_updated = models.IntegerField()
    last_checked = models.IntegerField()
    removed = models.BooleanField()


class Filters(models.Model):
    class Meta:
        db_table = "filters"
        verbose_name = "Filter"
        verbose_name_plural = "Filters"

    TARGET_CHOICES = (
        ('subject', 'subject'),
        ('content', 'content'),
        ('from', 'from'),
        ('to', 'to'),
        ('attachment', 'attachment')
    )

    TYPE_CHOICES = (
        ('regex', 'regex'),
        ('str', 'str'),
    )

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    target = models.CharField(max_length=50, choices=TARGET_CHOICES)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    content = models.CharField(max_length=255)
    new = models.BooleanField(default=1)
    when_add = models.IntegerField(default=int(time.time()))

class Letters(models.Model):
    class Meta:
        db_table = "letters"
        verbose_name = "Letter"
        verbose_name_plural = "Letters"

    id = models.IntegerField(primary_key=True)
    uid = models.IntegerField()
    hash = models.CharField(max_length=32)
    folder_id = models.IntegerField(db_index=True)
    subject = models.CharField(max_length=100)
    from_name = models.CharField(max_length=100)
    from_mail = models.CharField(max_length=100)
    to_name = models.CharField(max_length=100)
    to_mail = models.CharField(max_length=100)
    has_attachments = models.BooleanField()
    when_add = models.IntegerField()
    date = models.IntegerField()

class Attachments(models.Model):
    class Meta:
        db_table = "attachments"
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    id = models.IntegerField(primary_key=True)
    letter_id = models.IntegerField(db_index=True)
    hash = models.CharField(max_length=32)
    ext = models.CharField(max_length=10)
    file_name = models.CharField(max_length=100)
    mime_type = models.CharField(max_length=50)
    size = models.IntegerField()

class FiltersFinds(models.Model):
    class Meta:
        unique_together = ["filter_id", "letter_id"]
        db_table = "filters_finds"
        verbose_name = "FilterFind"
        verbose_name_plural = "FiltersFinds"

    filter_id = models.IntegerField(primary_key=True)
    letter_id = models.IntegerField(primary_key=True)
    when_add = models.IntegerField()

    @staticmethod
    def get_filters_ids_only():
        query = FiltersFinds.objects.all().query
        query.group_by = ['filter_id']
        return models.QuerySet(query=query, model=FiltersFinds)