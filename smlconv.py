# ****************************************************************************************
#
#									SML to HTML Conversion
#
# ****************************************************************************************

import re,sys,time

#
#	Represents a single line consisting of a title, and chord and text that goes with it.
#	there may be multiple chord/text items, all on the same line.
#
class Line:
	def __init__(self):
		self.title = ""
		self.chords = []
		self.lyrics = []
	#
	#	Add a new chord/lyric and possibly title to this line.
	#
	def add(self,title,chords,lyrics):
		if title != "":
			self.title = title 
		self.chords.append(chords)
		self.lyrics.append(lyrics)
	#
	#	Render the line in HTML
	#
	def render(self,handle):
		if len(self.chords) > 0:
			handle.write('<table>\n')
			handle.write("<tr><td  class='title' width='100px'>{0}</td>\n".format(self.title))
			handle.write("".join(["<td class='chords'>{0}</td>".format(self.chordProcess(x)) for x in self.chords]))
			handle.write("</tr>\n")
			handle.write("<tr><td></td>\n")
			handle.write("".join(["<td class='lyrics'>{0}</td>".format(x) for x in self.lyrics]))
			handle.write("</tr>\n")
			handle.write("</table>\n")
	#
	#	Pad out chord defs with spaces e.g G/C/ become "G / C /"
	#
	def chordProcess(self,chord):
		chord = chord.replace("/"," / ").replace("."," . ")
		while chord.find("  ") >= 0:
			chord = chord.replace("  "," ")
		return chord.strip()
#
#	Represents a collection of lines which should all be on the same page
#	issues in wkhtmltopdf?
#
class SongBlock:
	#
	#	Create a new block
	#
	def __init__(self):
		# Linesin this block.
		self.lines = [Line()]
		self.count = 0
		self.pageBreak = False
	#
	#	Page break after t his
	#
	def setPageBreak(self):
		self.pageBreak = True
	#
	#	Add a line part to the songblock current line
	#
	def add(self,title,chords,lyrics):
		self.lines[-1].add(title,chords,lyrics)	
		self.count += 1
	#
	#	Mark end of line.
	#
	def endLine(self):
		self.lines.append(Line())
	#
	#	Render song block.
	#
	def render(self,handle):
		if self.count != 0:
			handle.write('<table>\n')
			for line in self.lines:
				line.render(handle)
			handle.write('</table>\n')
		if self.pageBreak:
			handle.write('<div class="break"></div>\n')
		else:
			handle.write("<br />\n")
#
#	Main conversion class
#
class SMLConvert:
	def __init__(self):
		self.reset()
	#
	#	Reset the conversion process
	#
	def reset(self):
		# Headers with odds and sods that go in.
		self.header = { "title":"untitled","author":"unknown author" }
		# Block list, with first writing block
		self.blocks = [SongBlock()]
		# Known chords displayed
		self.chords = {}
	#
	#	Read and preprocess the source file
	#
	def read(self,sourceFile):
		# Read strip comments
		src = [x if x.find("#") < 0 else x[:x.find("#")] for x in open(sourceFile).readlines()]
		# Strip tabs , spaces
		src = [x.strip().replace("\t"," ") for x in src]
		# Get header stuff
		for assign in [x for x in src if x.find(":=") >= 0]:
			parts = [x.strip() for x in assign.split(":=")]
			self.header[parts[0].lower()] = parts[1]
		# Remove blank lines and assigns.
		self.source = [x for x in src if x != "" and x.find(":=") < 0]
	#
	#	Process the whole source file.
	#
	def process(self):
		pendingTitle = ""
		# For each line
		for src in self.source:
			if src.lower() == "[break]":
				self.blocks[-1].setPageBreak()
				src = ""
			# Check for {} header markers
			m = re.match("\\{(.*)\\}\\s*(.*)$",src)
			if m is not None:
				pendingTitle = m.group(1).strip()
				src = m.group(2).strip()
				if pendingTitle != "":
					self.blocks.append(SongBlock())
			# Keep processing the line till done.
			while src != "":

				# text before a chord grouping
				if src[0] != "[":
					# work out text to end or next chord grouping
					text = src if src.find("[") < 0 else src[:src.find("[")]
					# remove it.
					src = src[len(text):].strip()
					# add as lyric w/o chords
					self.blocks[-1].add(pendingTitle,"",text.strip())
					pendingTitle = ""

				# chord group.
				if (src+" ")[0] == '[':
					# when followed by another group
					m = re.match("^\\[(.*?)\\]\\s*(.*?)(\\[.*)$",src)
					if m is None:
						# when not followed by another group
						m = re.match("^\\[(.*?)\\]\\s*(.*)(.*)$",src)
					assert m is not None,"Error "+src
					# find chords in chord definition
					self.findChords(m.group(1))
					# add it to current block
					self.blocks[-1].add(pendingTitle,m.group(1).strip(),m.group(2).strip())
					pendingTitle = ""
					# discard
					src = m.group(3).strip()
			# mark end of line
			self.blocks[-1].endLine()
	#
	#	Extract actual chords fom the chord text (can have other things)
	#
	def findChords(self,chords):
		for c in chords.lower().replace("."," ").replace("/"," ").split(" "):
			if re.match("^[a-g][579\\#\\bdim]*$",c):
				self.chords[c] = True


	#
	#	Render the chord display
	#
	def renderChords(self,handle):
		# get and sort known chords
		chords = [x for x in self.chords.keys()]
		chords.sort()
		# render in HTML
		handle.write("<table><tr>\n")
		for c in chords:
			cf = c[0].upper()+c[1:].lower()
			handle.write("<td class = 'chordlabel'>{0}</td>".format(cf))
		handle.write("</tr><tr>\n")
		for c in chords:
			cn = c.lower().replace("#","sharp")
			handle.write("<td class='chordtable'><img class = 'chordimage' src='images/{0}.png'></td>".format(c))
		handle.write("</tr></table><br />\n")

	#
	#	Render all blocks
	#
	def renderSheet(self,handle):
		handle.write("<table width='100%'><tr><td>\n")
		handle.write("<p><h1>{0}</h1></p>\n".format(self.header["title"]))
		handle.write("<p><h2>{0}</h2></p>\n".format(self.header["author"]))
		handle.write("</td><td style='float:right;'>")
		self.renderChords(handle)
		handle.write("</td></tr></table>\n")
		for block in self.blocks:
			block.render(handle)
		date = time.strftime("%d-%m-%Y")
		handle.write("<p style='float:right'>Wymondham Ukulele Group {0}</p>".format(date))

if __name__ == '__main__':

	cv = SMLConvert()
	cv.read("8days.sml")
	cv.process()
	handle = open("target/test.html","w")
	handle.write('<link rel="stylesheet" href="sml.css">\n')
	cv.renderSheet(handle)
	handle.close()


