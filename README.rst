
=============
OpenResources
=============

OpenResources is a flexible, tag-based database application for Django_. It follows a similar approach to OpenStreetMap_ for creating a collaborative schema-less database based on tags (key-value pairs). OpenResources has been originally developed for `Vivir Bien`_, a mapping platform for solidarity economy resources.

OpenResources comes with "batteries included", which means that you don't only get a Django app but also a set of templates and static files that should give you a starting point and are designed with easy customization in mind.

OpenResources is released under the `GNU Affero General Public License (AGPL)`_, which means you can use it for free if you make all (modified) source code available under the AGPL through a link on your site. For details see the file LICENSE.txt .


Dependencies
------------

All dependencies on other (non-standard) Django applications are optional. At the moment OpenResources is prepared to work with the following 3rd party Djago applications:

* `Python Imaging Library`_ for the Icon.image field
* South_ for schema migrations
* Transmeta_ for multilingual installations
* django-threadedcomments_ for comments inside resources and views


Running OpenResources
---------------------

The enclosed test project allows you to run OpenResources in a local test setup without further installation. Inside the ``testproject`` directory, run::

  manage.py syncdb

(only the first time, creates database and superuser), then::

  manage.py runserver

to run a pre-configured server. Point your browser to http://localhost:8000/ - et voilà!


Installing OpenResources
------------------------

Adding OpenResources to a Django setup should be pretty straightforward. The only setting that is required is currently::

  AUTH_PROFILE_MODULE = 'openresources.UserProfile'

(We are working on removing this need).

The included templates are expecting the OpenResources media files to be served at ``{{MEDIA_URL}}openresources/`` , so if you want to use (or customize) these you should copy or symlink them accordingly.


Internationalization
--------------------

OpenResources uses Transifex_ for translating user interface elements. If you want to contribute a translation, you are more than welcome!

.. image:: https://www.transifex.net/projects/p/openresources/resource/django/chart/image_png
   :target: https://www.transifex.net/projects/p/openresources/

For translating model fields, Transmeta_ is used. While in the medium term, this should be replaced with something that does not interfer with the database schema of the application (see `Issue #1`_), for now we provide an alternative set of migrations to be used when South_ is used in combination with Transmeta. To use these migrations, add the following to your ``settings.py`` file::

  SOUTH_MIGRATION_MODULES = {
      'openresources': 'openresources.migrations_transmeta',
  }


Credits / Contributors
----------------------

The source code of OpenResources is released under the `GNU Affero General Public License (AGPL)`_, copyright by the following contributors:

* `Florian Ledermann`_ (ledermann@ims.tuwien.ac.at)

OpenResources incorporates parts of other open source projects:

* Icons used in the user interface CC-by_ `Yusuke Kamiyamane`_
* urlify.js based on Django_'s urlify.js


.. _`Vivir Bien`: http://vivirbien.mediavirus.org/
.. _OpenStreetMap: http://www.openstreetmap.org/
.. _Transmeta: http://code.google.com/p/django-transmeta/
.. _South: http://south.aeracode.org/
.. _django-threadedcomments: https://github.com/HonzaKral/django-threadedcomments
.. _`GNU Affero General Public License (AGPL)`: http://www.gnu.org/licenses/agpl.html
.. _`Florian Ledermann`: http://floledermann.com/
.. _CC-by: http://creativecommons.org/licenses/by/3.0/
.. _`Yusuke Kamiyamane`: http://p.yusukekamiyamane.com/
.. _Django: http://www.djangoproject.com/
.. _Transifex: https://www.transifex.net/projects/p/openresources/
.. _`Python Imaging Library`: http://www.pythonware.com/products/pil/
.. _`Issue #1`: https://bitbucket.org/floledermann/openresources/issue/1/more-loosely-coupled-model-translations

