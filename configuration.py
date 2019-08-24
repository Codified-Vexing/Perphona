from collections import deque  # Like lists but faster for queueing operations.

class Config:

	def __init__(self):
		self.song_dirs = ["./some_media/", ]  # "/home/vex/Music"
		self.panels = [True, True, True]  # Whether panels are visible. (Extras, Playlists, Metadata)
		
		self.dex = dict()
		self.playlists = dict()
		self.select_list = list()
		self.queue = deque()  # use self.queue.rotate(1) for efficient travel
		self.play = False
		self.mem_taken = 0  # RAM taken by the Song objects.
		self.number_songs = 0
		self.song_time = [0,0]
