

# Copyright 2011 Florian Ledermann <ledermann@ims.tuwien.ac.at>
# 
# This file is part of OpenResources
# https://bitbucket.org/floledermann/openresources/
# 
# OpenResources is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# OpenResources is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with OpenResources. If not, see <http://www.gnu.org/licenses/>.


from django.conf import settings

TAG_HELP_LINKS = getattr(settings, 'OPENRESOURCES_TAG_HELP_LINKS', None)

MAP_ATTRIBUTION = getattr(settings, 'OPENRESOURCES_MAP_ATTRIBUTION', 'Resource Data collected with <a href="http://bitbucket.org/floledermann/openresources/">OpenResources</a>')

