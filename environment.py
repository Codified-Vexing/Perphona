class Enviro:

	def solve_widgets(self):
		#self.id = self.builder.get_object("id")
		self.seeker = self.builder.get_object("seeker")
		self.song_time = self.builder.get_object("time_show")
		self.status_mem = self.builder.get_object("mem_gauge")
		self.the_title = self.builder.get_object("title_now")
		self.the_author = self.builder.get_object("author_now")
		self.top = self.builder.get_object("top_panel")
		self.meta_butt = self.builder.get_object("butt_pic")
		self.meta_put = self.builder.get_object("meta_put")
		self.meta_pan = self.builder.get_object("metadata_panel")
		self.art = self.builder.get_object("art_pic")
		self.art_comb = self.builder.get_object("art_list")
		self.pool = self.builder.get_object("pool_cell")
		self.playbook = self.builder.get_object("playlist_book")
		self.extrabook = self.builder.get_object("extras_book")
		self.rewinder = self.builder.get_object("rewind_button")
		self.spect_butt = self.builder.get_object("spect_hide")
		self.lyric_butt = self.builder.get_object("lyric_hide")
		self.dirs_butt = self.builder.get_object("dirs_butt")
		self.col_show_butt = self.builder.get_object("col_show_butt")
		self.loopmenu = self.builder.get_object("loopMenu")
		
		
		
		#{"signal": (callback, arg1, arg2, etc) , }  <-- each arg is whatever the signal emits when triggered, according to the docs.
		#{"signal": (lambda widget: callback(widget, arg_a, arg_b, etc)) , }  <-- For custom callback arguments
		sigs = {
				"finish_it": (self.finish_it),
				"extra_hiding": (
								( lambda widget, n: self.panel_hide(widget, self.extrabook) ),
								( lambda widget, n: self.panels.setitem(0, not widget.get_active()) )
								),
				"playlist_hiding": (
									( lambda widget, n: self.ntbk_tabs_hide(widget, self.playbook) ),
									( lambda widget, n: self.panels.setitem(1, not widget.get_active()) )
									),
				"metadata_hiding": (
									( lambda widget, n: self.panel_hide(widget, self.meta_pan) ),
									( lambda widget, n: self.panels.setitem(2, not widget.get_active()) )
									),
				"play_state": (self.play_pause_song),
				"skip_forward": (lambda widget: self.skip_song(widget, 1)),
				"skip_backward":(lambda widget: self.skip_song(widget, -1)),
				"seek_set": (lambda widget, event: self.seek_set(widget.get_value())),
				"check_dirs": self.check_dirs,
				"show_hover_menu": self.show_menu,
				"hide_hover_menu": self.hide_menu,
				}
		return sigs
