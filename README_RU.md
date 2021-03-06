MailSnoopy
===================


Mail-snoopy (MS) - программа для сбора, хранения и фильтрации писем с нескольких IMAP-аккаунтов. В отличие от стандартных почтовых клиентов, MS не синхронизирует почту с сервером полностью. Синхронизируется только поступление писем. Их удаление и перемещение между директориями игнорируется. 
Таким образом, MS позволяет собрать, сохранить и в последствии обработать, всю входящую почту за определённый отрезок времени. В то время как на целевых аккаунтах (со стороны сервера и других клиентов) многие письма могут быть удалены, MS будет хранить всю корреспонденцию от начала своей работы. 
Столь специфичная работа объясняется тем, что создавался MS для использования во время тестов на проникновение. В некоторых ситуациях пен-тестеру требуется наблюдать за большим количеством почтовых ящиков, в ожидании приходящих паролей, информации о доступах и прочем. В то время как на них могут валиться тысячи писем из которых tve предстоит отсеять 0.001%.

MS делится на 2 части - cli и web. cli-часть написана на Python3 и предназначена для фоновой работы на стороне сервера. web-часть написана с использованием Python3+Django и отвечает за взаимодействие пользователя с MS (редактирование аккаунтов, фильтров, просмотр почты, отфильтрованных писем и пр.).

Распространяется по лицензии MIT.

Установка cli-части
----------------------------
Минимальных аппаратных требований нет. 
Требования к ПО:
- nix-like ОС
- MySQL 5+
- Пакеты python3: mysql.connector, imapclient. 
Распакуйте дистрибутив. Создайте директории для хранения аттачей и тел писем. Отредактируйте файл config.ini. 

Установка web-части
-----------------------------
Минимальных аппаратных требований нет. 
Требования к ПО:
- nix-like ОС
- MySQL 5+
- Пакеты python3: bs4, django, mysqlclient, django-cors-headers, django-tastypie, django-angular
- Apache2 или любой другой веб-сервер способный работать с Django. 

При желании, сразу после распаковки дистрибутива и установки необходимых пакетов, вы можете запустить отладочный веб-сервер Django (./manage.py runserver) и начать работать с приложением. 
Если необходимо настроить полноценную работу на веб-сервере смотрите пример ниже или обратитесь к официальной документации Django. 

Конфигурация mysql хранится в файле my.cnf. Директории аттачей и тел писем указываются в mailsnoopyweb/settings.py в переменных ATTACHMENTS_PATH и BODIES_PATH соответственно. 

После установки главная страница может быть найдена по URL http://HOST/msw/index/

Пример установки на "чистую" Ubuntu 16.04
----------------------------------------------------------------
    apt-get install mysql-server libmysqlclient-dev apache2 git python3-dev python3-pip python3-venv python3-django python3-django-uwsgi libapache2-mod-wsgi-py3 
Клонируем дистрибутив ms-web. Размещаем его в /var/www/msw/. Заходим в /var/www/msw, создаём виртуальное окружение:

    python3 -m venv myvenv

Активируем его командой:

        source myvenv/bin/activate

Устанавливаем необходимые пакеты:

        pip3 install wheel
        pip3 install mysqlclient bs4
        pip3 install django django-cors-headers django-tastypie django-angular

Открываем /etc/apache2/sites-available/000-default.conf и дописываем в конец:

    WSGIScriptAlias / /var/www/msw/mailsnoopyweb/wsgi.py
    WSGIPythonPath /var/www/msw/:/var/www/msw/myvenv/lib/python3.5/site-packages/
    WSGIDaemonProcess example.com python-home=/var/www/msw/myvenv python-path=/var/www/msw/
    WSGIProcessGroup example.com

	Alias /static/ /var/www/msw/static/
	<Directory /var/www/msw/static>
	Require all granted
	</Directory>

Открываем mailsnoopyweb/settings.py и в переменных ATTACHMENTS_PATH и BODIES_PATH указываем пути к директориям аттачей и тел писем. 
В список ALLOWED_HOSTS вносим имя хоста по которому вы будете обращаться к ms-web. 
Перезапускаем веб-сервер и обращаемся по URL http://HOST/msw/index/

Схема работы
--------------------
Раз в указанное пользователем время MS проверяет имеющиеся в базе аккаунты на актуальность. Если при попытке аутентификации происходит ошибка, MS записывает сообщение об этом, аккаунт деактивируется и больше никаких работ по нему не проводится. Пока пользователь не поменяет пароль аккаунта или не активирует его вручную. Если аутентификация успешна, MS обновляет список директорий аккаунта. Далее, для каждой директории получается свежая почта. Получение писем происходит по разнице списка UID-ов на сервере и на стороне MS. Т.о., если в процессе работы какие-то письма получить не удалось (к примеру, сбой связи), то они будут получены позже т.к. их UIDы будут отсутствовать в базе. 
При получении каждого письма оно будет проходить через цепочку имеющихся фильтров. Записи о совпадениях заносятся в БД и доступны для просмотра в веб-части. Тела (содержимое) писем и их прикреплённые файлы сохраняются отдельно на жёстком диске, вне БД. 
При создании нового фильтра cli-часть отдельно проводит по нему все имеющиеся в базе письма.

Фильтры 
-----------
Фильтры в MS делятся по типу и целям. Типов всего 2:

 - Поиск по фразе (подстрока) 
 - Поиск по регулярному выражению (PCRE)

Цели у фильтров могут быть следующими:

 - Subject/Тема 
 - Content/Текст 
 - From/От (почтовый адрес и имя) 
 - To/Адресат (почтовый адрес и имя) 
 - Attachment/Вложение (имя файла и его mime-тип)

Аттачи
---------
Все загруженные прикреплённые файлы сохраняются с уникальным именем в соответствующую директорию. Работать с ними необходимо через web-часть. В ней вы можете загрузить вложения как из отдельного письма, так и из списка вложений с конкретным расширением файла. 

Логи
----
Cli-часть MS пишет логи в директорию logs. Внутри неё создаются подпапки с датой к которой относятся логи. В них можно обнаружить несколько файлов:

 - ex.log — лог возникших и не обработанных исключительных ситуаций. Буду благодарен если вы сообщите о них в виде баг-репорта.  
 - err.log — лог ошибок. Например о том, что войти в аккаунт не удалось. 
 - info.log — лог простой информации. Например о том, что письмо с ящика Х загружено и сохранено. 
 - out.log — всё что основной рабочий скрипт cli-части выводил в stdout в процессе работы (предыдущие логи вместе взятые).

Ограничения и предупреждения
------------------------------------------------
MS создавался как pet-project и тренировочная площадка для знакомства с Django и AngularJS. Если вы являетесь специалистом по этим инструментам, копание в коде может нанести вред вашей психике. 

MS имеет проблемы с обработкой писем в редких кодировках типа koi8-r или cp866. Возможно в будущем они будут устранены. 

Автор/Ссылки
---------------------
Кузьмин Антон http://anton-kuzmin.ru (ru) http://anton-kuzmin.pro (en)
 

