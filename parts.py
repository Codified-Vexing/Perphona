
from os import walk as fetch_dir
from os.path import splitext as get_ext
import random as rd

import sounddevice as sd # https://python-sounddevice.readthedocs.io/en/0.3.12/
import soundfile as sf
import mutagen as mt
#FFmpeg + GStreamer


import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

song_pool = ["/home/vex/Music", "."]
curr_list = ["example.flac",]
playlists = ["My First Playlist", "Awesome Mixtape", "Chill Ambience Tracks"]

# Get files and folders
for tgt in song_pool:
	print("In", tgt)
	for url, fldr, rsrc in fetch_dir(tgt):
		for r in rsrc:
			i, ext = get_ext(r)
			if ext[1:].upper() in sf.available_formats():
				print("\t",url,"/",r)

# Get Metadata
mtdt = mt.File(curr_list[0])
print(mtdt.info.pprint())
print(mtdt.tags.pprint())
print(mtdt.pictures)

# Play Audio
data, srate = sf.read(curr_list[0], dtype='float32')
comfirm = input("Play song? ")
sd.play(data, srate)

"""
# Draw Spectrum

f = Figure(figsize=(5, 5), dpi=150)
a = f.add_subplot(111)
		
curv = {"x":[0,], "y":[0,]}

a.axhline(linewidth=0.4, color='black')  # origin line
a.plot(curv["x"], curv["y"], color='blue'

a.set_xlabel("Frequency"))
canvas = FigureCanvas(f)  # a Gtk.DrawingArea
canvas.set_size_request(100,100)
cell.add_with_viewport(canvas)
"""
