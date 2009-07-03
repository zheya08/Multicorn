# -*- coding: utf-8 -*-
# This file is part of Dyko
# Copyright © 2008-2009 Kozea
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kalamar.  If not, see <http://www.gnu.org/licenses/>.

"""
Ogg/Vorbis parser.

This parser is read-only.

"""

from werkzeug import MultiDict
from tempfile import NamedTemporaryFile
from mutagen.oggvorbis import Open

from kalamar.item import AtomItem

class VorbisItem(AtomItem):
    """Ogg/Vorbis parser.
    
    The vorbis format allows a lot of things for tagging. It is possible to
    add any label you want and, for each label, to put several values.
    Because of that, this module cannot guarantee a set of properties. Despite
    this, here are some common tags you can use:
    - time_length : duration in seconds
    - _content : raw ogg/vorbis data
    - artist
    - genre
    - track
    
    TODO write test

    """
    format = 'audio_vorbis'
    
    def _custom_parse_data(self):
        """Set Vorbis metadata and time_length as properties."""
        
        properties = MultiDict()
        properties['_content'] = self._stream.read()
        
        # Create a real file descriptor, as VorbisFile does not accept a stream
        self._stream.seek(0)
        temporary_file = NamedTemporaryFile()
        temporary_file.write(self._stream.read())
        temporary_file.seek(0)
        vorbis_tags = Open(temporary_file.name)
        
        for key in vorbis_tags:
            properties.setlist(key, vorbis_tags[key])
        
        temporary_file.close()
        
        return properties
    
    def _custom_serialize(self, properties):
        """Return the whole file into a bytes string."""
        
        temporary_file = NamedTemporaryFile()
        temporary_file.file.write(self.properties['_content'])
        
        vorbis_tags = Open(temporary_file.name)
        keys = self.properties.parser_keys()
        keys.remove('_content')
        for key in keys:
            vorbis_tags[key] = self.properties.getlist(key)
        vorbis_tags.save()
        
        temporary_file.file.flush()
        temporary_file.seek(0)
        self.properties['_content'] = temporary_file.read()
        
        return self.properties['_content']
    
del AtomItem
