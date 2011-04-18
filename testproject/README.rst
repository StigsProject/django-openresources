
==============================
Test Project for OpenResources
==============================

To run an OpenResources test server, type::

  manage.py syncdb

(only the first time, creates database and superuser), then::

  manage.py runserver

to run a pre-configured server. Point your browser to http://localhost:8000/ - et voilà!

You can also create a Python virtual environment containing your dependencies (e.g. South, TransMeta) here.

===================
Creating Migrations
===================

If you have South installed, you can run::

  manage.py schemamigration openresources --auto

to create a schemamigration if you changed the models. After that you can run::

  manage.py migrate

to apply that migration to the database.

=====================
Creating Translations
=====================

To create or update a translation, go to ``../openresources`` and run::

  django-admin.py makemessages -l <language_code>

Edit the created/updated translation file, and run::

  django-admin.py compilemessages

Make sure to check in / commit bot the ``.po`` and the ``.mo`` (binary) file in ``locale/<language_code>/LC_MESSAGES/``, since not everyone will have gettext installed!


