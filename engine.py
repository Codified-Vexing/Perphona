#!/usr/bin/env python

#https://gstreamer.freedesktop.org/documentation/playback/playbin.html?gi-language=python
#http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.html


import os  # Gst.filename_to_uri(filename)
from os import walk as fetch_dir
from os.path import splitext as get_ext
from os.path import split as get_name

#import sounddevice as sd  # PortAudio: interface between hardware and Numpy  https://python-sounddevice.readthedocs.io/en/0.3.12/
import soundfile as sf  # libsndfile: interface between audio files and Numpy  https://pysoundfile.readthedocs.io/en/0.9.0/#module-soundfile
import mutagen as mt

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk as g
from gi.repository import GdkPixbuf as gpix
from gi.repository import Gst as gst
gst.init(None)


def time_convert(nanosec):
	pass


## Finding what file extensions/formats we can read. This is the only part using soundfile until someone figures out a way to parse the available GStreamer plugins.
formats = list(sf.available_formats().keys()) # + ["MP3", ] This will make it take a long time to load.

# from https://github.com/GStreamer/gstreamer/blob/master/tools/gst-inspect.c
# features = gst_registry_get_feature_list_by_plugin (gst_registry_get (),
# feature = GST_PLUGIN_FEATURE (features->data);
# factory = GST_ELEMENT_FACTORY (feature);
# factory = GST_TYPE_FIND_FACTORY (feature);
# extensions = gst_type_find_factory_get_extensions (factory);

# https://lazka.github.io/pgi-docs/#Gst-1.0/classes/Registry.html#Gst.Registry
#plugin_reg = gst.Registry().get()
#for each in plugin_reg.get_plugin_list():
#	each.get_description()
#	gst.TypeFindFactory
#	each.list_free()

#####

class Engine:

	def __init__(self):
	
		#gst-inspect in commandline for available codecs
		pass
		

class Song:

	def __init__(self, url, controller):
	
		"""
		«controller» is the object instance that controls the songs. Might be some "song_manager" class, but usually is the main GTK class.
		"""
	
		self.ui = controller	
		
		self.url = os.path.realpath(url)
		if not os.path.isfile(self.url):
			print("File doesn't exist!")

		self.gsbin = gst.ElementFactory.make("playbin",None)
		gsnul = gst.ElementFactory.make("fakesink","nulsnk")
		self.gsbin.set_property("video_sink", gsnul)
		self.gsbus = self.gsbin.get_bus()

		self.gsbus.connect("message", self.gstreamer_message)
		self.gsbus.add_signal_watch()
	
		self.gsbin.set_property("uri", "file://" + self.url)
		self.gsbin.set_state(gst.State.READY)
	
		#self.gsbin.volume = 0.5
				
		self.raw_meta = mt.File(self.url)
		drctr, flnm = get_name(url)
		bsnm, ext = get_ext(flnm)

		secs = round(self.raw_meta.info.length, 2)
		mins = secs/60
		secs = int((mins%1)*60)
		mins = int(mins)
		hrs = mins/60
		mins = int((hrs%1)*60)
		hrs = int(hrs)
		duration = ":".join((str(hrs).zfill(2), str(mins).zfill(2), str(secs).zfill(2)))

		self.meta = {
					"nanosecs": None,  # Duration in nanosecs, to interface with GStreamer
					"duration": duration,  # Duration, but in a human readable form.
					"number": "NaN",
					"title": bsnm,
					"author": "UNDEFINED",
					"album": "UNDEFINED",
					"year": "????",
					"genre": "UNDEFINED",
					"pics": dict(),
					"thumbnail": None,
					}


		for kind, each in {
		"number": ("tracknumber", "TRCK"),
		"title": ("title", "TIT2"),
		"author": ("artist", "albumartist", "album-artist", "TPE1", "performer", "composer"),
		"album": ("album", "TALB"),
		"year": ("date", "TDRC"),
		"genre": ("genre", "TCON"),
		}.items():
			for variant in each:
				result = self.raw_meta.tags.get(variant, False)
				if result:
					if kind == "year":
						self.meta[kind] = str(result[0])[:4]
					elif kind == "number":
						self.meta[kind] = str(result[0]).zfill(3)
					else:
						self.meta[kind] = str(result[0])
					break  # Stop looking for it once a result was found. Thus the order of the options to try has a priority.

	
	def gstreamer_message(self, bus, message):
		# https://gstreamer.freedesktop.org/documentation/gstreamer/gstmessage.html?gi-language=c#GstMessageType
		# https://gstreamer.freedesktop.org/documentation/gstreamer/gsttaglist.html?gi-language=c
		
		# Look for GST_DEBUG: https://gstreamer.freedesktop.org/documentation/gstreamer/running.html?gi-language=c
		
		msg_kind = [
					gst.MessageType.EOS,
					#gst.MessageType.TAG,
					gst.MessageType.ERROR,
					gst.MessageType.WARNING,
					gst.MessageType.INFO,
					]
		"""
		def extract(raw_meta,kind):
			count = raw_meta.get_tag_size(kind)
			for i in range(count):
				value = raw_meta.get_value_index(kind, i)
				print(kind, i, "::", value)
		"""			
		t = message.type
		m = gst.message_type_get_name(t)		
		
		if t == gst.MessageType.EOS:
			self.gsbin.set_state(gst.State.NULL)
			print("The song is ended!")
			"""
		# Get the metadata using GStreamer
		# It will keep updating the data as the music plays because it's updating bitrate value.
		elif t == gst.MessageType.TAG:
			raw_meta = message.parse_tag()
			raw_meta.foreach(extract)
			"""
		elif t == gst.MessageType.ERROR:
			self.gsbin.set_state(gst.State.NULL)
			err, debug = message.parse_error()
			print(err,debug)
		elif t == gst.MessageType.WARNING:
			err, debug = message.parse_warning()
			print(err,debug)
		elif t == gst.MessageType.INFO:
			err, debug = message.parse_info()
			print(err,debug)
		elif t == gst.MessageType.STATE_CHANGED:
			old, new, pending = message.parse_state_changed()
			if old == gst.State.READY and pending == gst.State.PLAYING:
				self.meta["nanosecs"] = self.gsbin.query_duration(gst.Format.TIME)[1]
				self.ui.update_song_timestamp()
			
		
		if t in msg_kind:
			print("")  # just an empty space to be more readable
	
	def tell_time(self):
		return self.meta["nanosecs"], self.gsbin.query_position(gst.Format.TIME)[1]

	def show(self):
		# Only load the pictures if it hasn't already. Ie.: the number of pics in metadata is different from those loaded.
		
		if not hasattr(self.raw_meta, 'pictures'):
			return False
		
		if len(self.raw_meta.pictures) != len(self.meta["pics"]):
			art_type = ["Other", "File Icon", "Alternate File Icon", "Front Cover", "Back Cover", "Leaflet Page", "Media Label", "Lead Author", "Author", "Conductor", "Band", "Composer", "Lyrics Writer", "Recording Location", "During Perfomance", "Screen Capture", "Fish", "Band Logo", "Publisher Logo"]
			
			if len(self.raw_meta.pictures) >= 1:
				for each in self.raw_meta.pictures:
					pixloader = gpix.PixbufLoader()
					pixloader.write(each.data)
					pixloader.close()
					self.meta["pics"][art_type[each.type]] = pixloader.get_pixbuf()
					if each.type in (3,2,1) or self.meta["thumbnail"] == None:
						self.meta["thumbnail"] = pixloader.get_pixbuf().scale_simple(30, 30, gpix.InterpType.BILINEAR)

	def play(self, pos=None):
		# States: VOID_PENDING, NULL, READY, PAUSED, PLAYING
		self.gsbin.set_state(gst.State.PLAYING)
		if pos:
			self.gsbin.seek_simple(gst.Format.TIME, gst.SeekFlags.FLUSH, pos)
			
	def pause(self, pos=None):
		self.gsbin.set_state(gst.State.PAUSED)
		if pos:
			self.gsbin.seek_simple(gst.Format.TIME, gst.SeekFlags.FLUSH, pos)

	def stop(self):
		self.gsbin.set_state(gst.State.NULL)



if __name__ == "__main__":
	print("oopsie!")
else:
	print("Engine Loaded")

