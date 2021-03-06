
#
# PyGoWave Server - The Python Google Wave Server
# Copyright 2009 Patrick Schneider <patrick.p2k.schneider@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson

from pygowave_server.models import Wave, Wavelet, Blip

from lxml import etree
import urllib2, time

class Event:
	"""
	An event captures changes made to a Wavelet, Blip, or Document in the Wave
	system. In this form, it can be sent to a (robot) client.
	
	"""

	# Event types
	WAVELET_BLIP_CREATED = 'WAVELET_BLIP_CREATED'
	WAVELET_BLIP_REMOVED = 'WAVELET_BLIP_REMOVED'
	WAVELET_PARTICIPANTS_CHANGED = 'WAVELET_PARTICIPANTS_CHANGED'
	WAVELET_TIMESTAMP_CHANGED = 'WAVELET_TIMESTAMP_CHANGED'
	WAVELET_TITLE_CHANGED = 'WAVELET_TITLE_CHANGED'
	WAVELET_VERSION_CHANGED = 'WAVELET_VERSION_CHANGED'
	BLIP_CONTRIBUTORS_CHANGED = 'BLIP_CONTRIBUTORS_CHANGED'
	BLIP_DELETED = 'BLIP_DELETED'
	BLIP_SUBMITTED = 'BLIP_SUBMITTED'
	BLIP_TIMESTAMP_CHANGED = 'BLIP_TIMESTAMP_CHANGED'
	BLIP_VERSION_CHANGED = 'BLIP_VERSION_CHANGED'
	DOCUMENT_CHANGED = 'DOCUMENT_CHANGED'
	FORM_BUTTON_CLICKED = 'FORM_BUTTON_CLICKED'

	def __init__(self, evt_type, wave, modified_by, properties = {}):
		self.wave = wave
		self.evt_type = evt_type
		self.modified_by = modified_by
		self.properties = properties
		self.timestamp = int(time.time()*1000)
	
	def serialize(self):
		"""
		Serialize the event into a format that is compatible with robots.
		
		"""
		return {
			"timestamp": self.timestamp,
			"type": self.evt_type,
			"modifiedBy": self.modified_by,
			"properties": self.properties,
		}

class GadgetLoader:
	
	SUPPORTED_FEATURES = ("rpc", "wave", "wave-preview", "setprefs", "dynamic-height")
	
	def __init__(self, url):
		"""
		Parses a Gadget's XML data after downloading it.
		Throws urllib2.HTTPError if download failed.
		Throws lxml.etree.XMLSyntaxError if not well-formatted.
		Throws ValueError if it is not a valid (Wave-) Gadget.
		
		"""
		
		opener = urllib2.build_opener(urllib2.HTTPRedirectHandler())
		
		# Download
		reader = opener.open(url)
		root = etree.XML(reader.read())
		reader.close()
		
		if root.tag != "Module":
			raise ValueError(_(u'Invalid Gadget XML format (Module tag missing)'))
		
		# Title
		title = root.xpath("//ModulePrefs/attribute::title")
		if len(title) != 1:
			raise ValueError(_(u'Invalid Gadget XML format (ModulePrefs/title missing)'))
		self.title = title[0]
		
		# Optional attributes
		self.description, self.height, self.author, self.author_email = self.__getAttrsOrNone(root, "//ModulePrefs", ("description", "height", "author", "author_email"))
		
		# Requires/Features
		self.features = {}
		for req in root.xpath("//ModulePrefs/Require"):
			feat = req.get("feature")
			if feat == None: continue
			feat = feat.lower()
			if feat in GadgetLoader.SUPPORTED_FEATURES:
				self.features[feat.replace("-", "_")] = True
			else:
				raise ValueError(_(u'Required feature "%s" is unsupported') % (feat))
		
		# Userprefs
		self.prefs = {}
		for pref in root.xpath("//UserPref"):
			if pref.get("name"):
				prefmap = dict(pref.attrib)
				del prefmap["name"]
				if prefmap.has_key("datatype"):
					prefmap["datatype"] = prefmap["datatype"].lower()
					if prefmap["datatype"] == "list":
						if prefmap.has_key("default_value"):
							prefmap["default_value"] = prefmap["default_value"].split("|")
					elif prefmap["datatype"] == "bool":
						if prefmap.has_key("default_value"):
							if prefmap["default_value"] == "" \
								or prefmap["default_value"].lower() == "false" \
								or prefmap["default_value"] == "0":
								prefmap["default_value"] = False
							else:
								prefmap["default_value"] = True
				else:
					prefmap["datatype"] = "string"
				self.prefs[pref.get("name")] = prefmap
		
		# Content
		content = root.xpath("//Content/text()")
		if len(content) != 1:
			raise ValueError(_(u'Invalid Gadget XML format (Content tag missing)'))
		
		self.content = content[0]
	
	def update_prefs(self, data):
		"""
		Update the UserPrefs with a name:value map.
		
		"""
		for key, value in data.iteritems():
			if self.prefs.has_key(key):
				self.prefs[key]["value"] = value
			else:
				self.prefs[key] = {
					"datatype": "string",
					"value": unicode(value)
				}
	
	def prefs_json(self):
		return simplejson.dumps(self.prefs)
	
	def __getAttrOrNone(self, root, path, attr):
		v = root.xpath("%s/attribute::%s" % (path, attr))
		if len(v) > 0:
			return v[0]
		else:
			return None
	
	def __getAttrsOrNone(self, root, path, attrs):
		return [self.__getAttrOrNone(root, path, attr) for attr in attrs]
