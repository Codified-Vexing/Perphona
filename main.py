#!/usr/bin/env python
"""
Module Docstring
"""
__author__ = "Diogo JC Duarte"
__version__ = "0.1.0"
__license__ = "MIT"

# TODO:
# Remember what module allowed to take command-line arguments. Built a parser of it into Vexwerk. Import Vexwerk here.
#from vexwerk import clix

from os import walk as fetch_dir
from os.path import splitext as get_ext
from os.path import split as get_name

from pympler.asizeof import basicsize as basicsize

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as g
from gi.repository import Gdk as gdk
from gi.repository import GObject as gob
from gi.repository import Pango

from configuration import Config
from environment import Enviro
from engine import *

# https://www.youtube.com/watch?v=9zDYCFWTbSw
# https://www.youtube.com/watch?v=vNxhi2a2SpI&list=PL6gx4Cwl9DGBBnHFDEANbv9q8T4CONGZE&index=13&t=0s
# https://lazka.github.io/pgi-docs/

# https://stackoverflow.com/questions/10759954/triggering-a-function-on-hover-event-for-button-in-pygtk/10774373#10774373
# https://developer.gnome.org/gdk3/stable/gdk3-Events.html#GdkEventMask

		
class WindowMain(Config, Enviro, Engine):
	
	def __init__(self):

		
		# Get GUI from Glade file
		self.builder = g.Builder()
		self.builder.add_from_file("perphona.glade")  # UI file specified here
		
		# Display main window
		self.mainwin = self.builder.get_object("mainwin")  # The top-level window's ID could be "mainwin"
		#print(*dir(self.windowMain), sep="\n")
		self.mainwin.show()
		g.Window.maximize(self.mainwin)
		
		self.mainwin.set_title("Perphona - Title/Filename")
		
		Config.__init__(self)
		Engine.__init__(self)

		# Make widget references and get signals
		sigs = self.solve_widgets()
		
		# Figure out all the playlits and songs in the directories.
		# Set the selected playlist as one of the found ones by default
		# Use a database instead of opening files.
		# fl.seek(1,0)
		with open("index.csv") as fl:
			for line in fl:
				if line[0] == "#" or line[0] == "|" or len(line) <= 2:
					pass
				else:
					line = line.split(",")
					self.dex[int(line[0])] = [int(x) for x in line[1:]]
		playlists_raw = list(self.dex.keys())
		playlists = dict()
		with open("database.csv") as fl:
			for each in playlists_raw:
				fl.seek(each,0)
				playlist_url = fl.readline().strip()			
				playlists[get_name(playlist_url)[1]] = playlist_url 
		
		if not "default.m3u" in playlists:
			playlists["default.m3u"] = list()
			
			
		self.solve_from_dirs()

		# Read last song and last playlists from a configuration file.
		# If a playlist was found, overwrite the automatically selected one and use it.
		# also build the song queue
		# Set the first song of the queue for the metadata panel.
		self.solve_playlist()
			
		self.solve_metadata()
		
		self.status_mem.set_text("The "+str(self.number_songs)+" songs listed take ~"+str(self.mem_taken)+" Bytes of RAM")
		
		# The thing that loops forever.
		self.looptime = gob.timeout_add(500, self.looper)
		
		# Get the signals. After doing initial stuff to the UI, so that it doesn't trigger the callbacks.
		#self.builder.connect_signals(self)
		self.builder.connect_signals(sigs)  # connects those set manually
		
		# Doffer
		self.mainwin.show_all()
		g.main()

	def bogus(*x):
		pass

	def looper(self):
		if self.play:
			dur, pos = self.queue[0].tell_time()
			self.seeker.set_value(pos)
			time = str(pos)+"/"+str(dur)
			self.song_time.set_text(time)
		return True  # Makes it loop again


	def solve_from_dirs(self):
		# fold_list = g.ListStore(str,str)
		# dir_list = g.ListStore(str,str)
		pool_list = g.ListStore(str, str,str,str,str,str,str,str)

		# Get files and folders
		for tgt in self.song_dirs:
			for url, fldr, rsrc in fetch_dir(tgt):
				for r in rsrc:
					i, ext = get_ext(r)
					
					place = url+"/"+r
					
					if ext[1:].upper() in formats:
							song = Song(place, self)
							self.mem_taken += basicsize(song)
							self.number_songs += 1
					
							pool_list.append([
												song.meta["title"], 
												song.meta["author"],
												song.meta["album"],
												song.meta["year"],
												song.meta["genre"],
												song.meta["duration"],
												"0",
												place,
												])			
					if ext[1:].upper() == "M3U":
						self.playlists[place] = g.ScrolledWindow()
						self.playlists[place].add(g.TreeView(g.ListStore(str,str,str,str,str,str,str,str)))
						tab_text = g.Label(i)
						tab_text.set_max_width_chars(8)
						self.playbook.prepend_page(self.playlists[place], tab_text)
						#self.playbook.set_tab_reorderable(tab_text, True)
						#self.playlists[place].get_children()[0].set_reorderable(True)
						self.playlists[place].get_children()[0].get_selection().set_mode(g.SelectionMode.MULTIPLE)
						self.playlists[place].get_children()[0].set_grid_lines(g.TreeViewGridLines.VERTICAL)
						
						self.playlists[place].get_children()[0].connect("cursor_changed", self.songSelect)
						self.playlists[place].get_children()[0].connect("row_activated", self.songSet)
						
						for i, col_title in enumerate(["Nr.", "Title", "Author", "Album", "Year", "Genre", "Length", "Kudos"]):
							rend = g.CellRendererText()
							col = g.TreeViewColumn(col_title, rend, text=i)
							#col.set_sort_column_id(i)
							col.set_reorderable(True)
							col.set_resizable(True)
							self.playlists[place].get_children()[0].append_column(col)
							
		
		pool_view = g.TreeView(pool_list)
		pool_view.set_enable_search(True)
		pool_view.set_grid_lines(g.TreeViewGridLines.VERTICAL)
		pool_view.get_selection().set_mode(g.SelectionMode.MULTIPLE)
		
		#pool_view.connect("clicked", self.on_close_clicked)
		pool_view.connect("button-press-event", self.onClick)
		
		
		for i, col_title in enumerate(["Title", "Author", "Album", "Year", "Genre", "Length", "Kudos", "Location",]):
			rend = g.CellRendererText()
			col = g.TreeViewColumn(col_title, rend, text=i)
			col.set_sort_column_id(i)
			col.set_reorderable(True)
			col.set_resizable(True)
			pool_view.append_column(col)
			
		self.pool.add(pool_view)
		
		
	def solve_playlist(self, url=None):
		if url == None:
			url = list(self.playlists.keys())[-1]
		
		with open(url) as file:
			for line in file:
				line = line.strip()
				if line[0] == "#":
					pass
				elif len(line) >= 1:
					drctr, flnm = get_name(url)
					# TODO: There needs to be a better way to deal with paths relative to the playlist file.
					#song_url = "/".join([drctr, line])
					# For now please only use absolute paths or it will assume a path relative to the Python script.
					song_url = line
					
					song = Song(song_url, self)
					self.mem_taken += basicsize(song)
					
					self.select_list.append(song)  # This one must correspond with the indexes of the Treeview ListStore model.
					self.queue.append(song)  # This one will be shuffled and looped as the user asks to.
					
					
					# ["Nr.", "Title", "Author", "Album", "Year", "Length", "Kudos"]
					self.playlists[url].get_children()[0].get_model().append([ 
																				song.meta["number"],
																				song.meta["title"], 
																				song.meta["author"],
																				song.meta["album"],
																				song.meta["year"],
																				song.meta["genre"],
																				song.meta["duration"],
																				"0"
																			])
	
	def solve_metadata(self, song=None):
		
		if song == None:
			song = self.queue[0]
		
		meta_text = "\n".join( song.raw_meta.info.pprint().split(",") + [song.raw_meta.tags.pprint(), ])
		self.meta_put.set_label(meta_text)
		
		self.art_comb.remove_all()
		
		song.show()  # Build the pictures
		
		# Thumbnail will only exist if there are pictures. Thus it can be used as a test for the availability of pictures.
		if song.meta["thumbnail"]:

			for n, kind in enumerate(song.meta["pics"].keys()):
				self.art_comb.append(str(n), kind)

			self.art_comb.set_active(0)
			curr_art = self.art_comb.get_active_text()

			# Make picture adjust size to the be completely contained in its panel cell.
			# Get the original picture size before changing it: print(pixpic.get_width(), "x", pixpic.get_height())
			#allocation = self.art.get_allocation() # The size available to occupy in this widget
			self.meta_butt.set_from_pixbuf(song.meta["thumbnail"])
			self.art.set_from_pixbuf(song.meta["pics"][curr_art].scale_simple(250, 250, gpix.InterpType.BILINEAR))
		else:
			print("No pictures available!")
			self.meta_butt.set_from_icon_name("gtk-orientation-portrait", 4)
			self.art.set_from_icon_name("gtk-missing-image", 6)

	def check_dirs(self, widget):
		self.solve_from_dirs()

	def onClick(self, widget, event):
		print(widget)
		if event.button == 1:
			print("pluck")
		elif event.button == 3:
			print("hit")
		else:
			print(event.button)		
			
	
	def onDrag(self, widget, context):
		print("dragging", context)
	
	def songSelect(self, tree):
		# «model» is the whole listStore object.
		# selected is a list of indices of selected rows.
		# Given one of the indices, «model[index]» is a list representing an row, each element a data column.
		# The ordering of data in the row object doesn't seem to be affected by the re-ordering of columns the user does.
		model, selected = tree.get_selection().get_selected_rows()
		if len(selected) == 0:
			print("We gotta fix this at some point.")
		else:
			row = selected[0].to_string()
			song = self.select_list[int(row)]
			self.solve_metadata(song)
			
	
	def songSet(self, tree, path, col):
		print("play this song in the selected playlist:",path)
	
	def play_pause_song(self, widget):
		icon = ["gtk-media-play", "gtk-media-pause"]
		if self.play:
			self.queue[0].pause()
		else:
			self.queue[0].play()
			if len(self.queue) == 0 and len(self.playlists) == 0:
				print("NOTICE: No music available")
			elif len(self.queue) >= 1:
				self.the_title.set_text( self.queue[0].meta["title"] )
				self.the_author.set_text("by "+self.queue[0].meta["author"] )
			elif len(self.playlists) >= 1:
				print("There's a playlist, but no songs")
			#	print("checking playlist: ", self.playlists[ list(self.playlists.keys())[0] ])
			#	self.play_song(None)
				
		if widget:  # was this the called by the play button in the UI?
			self.play = not self.play  # Change the state only if it was the button being pressed
			widget.get_children()[0].set_from_icon_name(icon[int(self.play)], 5)
	
	def seek_set(self, pos=0):
		pick = ("pause", "play")
		getattr(self.queue[0], pick[int(self.play)])(pos)
	
	def skip_song(self, widget, num=1):
		if self.play:
			self.queue[0].stop()
		self.queue.rotate(num)
		self.the_title.set_text( self.queue[0].meta["title"] )
		self.the_author.set_text("by "+self.queue[0].meta["author"] )
		if self.play:
			self.queue[0].play()

	def update_song_timestamp(self):
		self.seeker.set_sensitive(True)
		self.seeker.set_range(0, self.queue[0].meta["nanosecs"])

	def panel_hide(self, button, target):
		## TODO: attach this to self.panels
		stt = ("show", "hide")
		getattr(target, stt[int(button.get_active())])()
			
	def ntbk_tabs_hide(self, widget, target):
		target.set_show_tabs(not widget.get_active())

	def trick_reverse(self, widget):
		# https://gstreamer.freedesktop.org/documentation/tutorials/basic/playback-speed.html?gi-language=c
		pass

	def show_menu(self, widget, event):
		self.loopmenu.popup()
		#self.loopmenu.grab_focus()
		
	def hide_menu(self, widget, event):
		widget.popdown()
		
		

	def finish_it(self, widget, data=None):
		print("Quitting...")
		g.main_quit()
		# Do «self.windowMain.destroy()» to exit by other means than pressing the window cross.
	
	# Example signal handler:
	
	#def foo(self, widget, data=None):
	#	print("bar")


if __name__ == "__main__":
	print("Initiating the audio imagery landscape...")
	applic = WindowMain()
else:
	print("oopsies.")
