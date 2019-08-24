#!/usr/bin/env python

#https://gstreamer.freedesktop.org/documentation/playback/playbin.html?gi-language=python

import os

#import sounddevice as sd  # PortAudio: interface between hardware and Numpy  https://python-sounddevice.readthedocs.io/en/0.3.12/
import soundfile as sf  # libsndfile: interface between audio files and Numpy  https://pysoundfile.readthedocs.io/en/0.9.0/#module-soundfile
import mutagen as mt

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk as g
from gi.repository import Gst as gst
from gi.repository import GdkPixbuf as gpix
gst.init(None)

class Engine:

	def __init__(self):
	
		#gst-inspect in commandline for available codecs
		#NOTE: use playbin as a playlist, rather than creating multiple bins?
	
	
		filepath = os.path.realpath("example.mp3")
		if not os.path.isfile(filepath):
			print("File doesn't exist")
	
		self.gsbin = gst.ElementFactory.make("playbin",None)
		gsnul = gst.ElementFactory.make("fakesink","nulsnk")
		self.gsbin.set_property("video_sink", gsnul)
		self.gsbin.set_property("uri", "file://" + filepath)
		self.gsbus = self.gsbin.get_bus()
		
		self.gsbus.connect("message", self.gstreamer_message)
		self.gsbin.connect("about-to-finish", self.song_end)
		self.gsbus.add_signal_watch()

		self.gsbin.volume = 0.5
		self.gsbin.set_state(gst.State.PLAYING)
		# States: VOID_PENDING, NULL, READY, PAUSED, PLAYING
	
		#if gsbin.seek_simple(gst.Format.PERCENT, gst.SeekFlags.FLUSH, 10):
		if self.gsbin.seek_simple(gst.Format.TIME, gst.SeekFlags.FLUSH, gst.SECOND * 120):
			print(self.gsbin.query_position(gst.Format.TIME), " of ", self.gsbin.query_duration(gst.Format.TIME))
		else:
			print("Seeking failed")

	
	def gstreamer_message(self, bus, message):
		t = message.type
		
		if t == gst.MessageType.TAG:
			print("A metadata variable was found")
		else:
			err, debug = message.parse_error()
			print("Error: %s" % err, debug)
				
			self.gsbin.set_state(Gst.State.NULL)
	
	def song_end(self, gsbin):
		print("The song is ended!")
		

class Song:

	def __init__(self, url):
		self.data = None
		self.pics = dict()
		self.miniature = None
		
		self.url = os.path.realpath(url)
		if not os.path.isfile(self.url):
			print("File doesn't exist!")
		
		self.meta = mt.File(self.url)

		self.length = str(round(self.meta.info.length, 2)) + "sec"
		
		self.title = self.meta.tags["title"][0]
		if self.title == None:
			drctr, flnm = get_name(url)
			bsnm, ext = get_ext(flnm)
			self.title = bsnm
			
		auth_set = False
		self.author = "undefined artist"
		for each in (self.meta.tags.get("artist", False), self.meta.tags.get("albumartist", False)):
			if each:
				each = each[0]
				if auth_set:
					break
				else:
					self.author = each
					auth_set = True

	def show(self):
		# Only load the pictures if it hasn't already. Ie.: the number of pics in metadata is different from those loaded.
		if len(self.meta.pictures) != len(self.pics):
			art_type = ["Other", "File Icon", "Alternate File Icon", "Front Cover", "Back Cover", "Leaflet Page", "Media Label", "Lead Author", "Author", "Conductor", "Band", "Composer", "Lyrics Writer", "Recording Location", "During Perfomance", "Screen Capture", "Fish", "Band Logo", "Publisher Logo"]
			
			if len(self.meta.pictures) >= 1:
				for each in self.meta.pictures:
					pixloader = gpix.PixbufLoader()
					pixloader.write(each.data)
					pixloader.close()
					self.pics[art_type[each.type]] = pixloader.get_pixbuf()
					if each.type in (3,2,1) or icon == None:
						self.miniature = pixloader.get_pixbuf().scale_simple(30, 30, gpix.InterpType.BILINEAR)
		
	def load(self):
		pass
		
	def play(self):
		pass




if __name__ == "__main__":
	print("oopsie!")
	appl = Engine()
else:
	print("Engine Loaded")

