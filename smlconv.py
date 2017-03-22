#
#	SML to HTML Conversion
#
import re,sys

#
#	Represents a single line consisting of a title, and chord and text that goes with it.
#	there may be multiple chord/text items, all on the same line.
#
class Line:
	def __init__(self):
		self.title = ""
		self.chords = []
		self.lyrics = []

	def add(self,title,chords,lyrics):
		if title != "":
			self.title = title 
		self.chords.append(chords)
		self.lyrics.append(lyrics)

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

	def chordProcess(self,chord):
		chord = chord.replace("/"," / ").replace("."," . ")
		while chord.find("  ") >= 0:
			chord = chord.replace("  "," ")
		return chord.strip()
#
#	Represents a collection of lines
#
class SongBlock:
	#
	#	Create a new block
	#
	def __init__(self):
		# Linesin this block.
		self.lines = [Line()]
		self.count = 0
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
			handle.write('</table><br />\n')
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
		self.chords = {"A":"","B":"","C":"","D":"","E":"","F":"","G":"","Bb":"" }
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
					m = re.match("^\\[(.*?)\\]\\s*(.*?)(\\[.*)$",src)
					if m is None:
						m = re.match("^\\[(.*?)\\]\\s*(.*)(.*)$",src)
					assert m is not None,"Error "+src
					self.blocks[-1].add(pendingTitle,m.group(1).strip(),m.group(2).strip())
					pendingTitle = ""
					src = m.group(3).strip()
			self.blocks[-1].endLine()

	def renderChords(self,handle):
		chords = [x for x in self.chords.keys()]
		chords.sort()
		handle.write("<table><tr>\n")
		for c in chords:
			handle.write("<td class = 'chordlabel'>{0}</td>".format(c))
		handle.write("</tr><tr>\n")
		for c in chords:
			c = "chord"
			handle.write("<td class='chordtable'><img class = 'chordimage' src='{0}.png'></td>".format(c))
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


if __name__ == '__main__':

	cv = SMLConvert()
	cv.read("8days.sml")
	cv.process()
	handle = open("test.html","w")
	handle.write('<link rel="stylesheet" href="sml.css">\n')
	cv.renderSheet(handle)
	handle.close()

# rip chord names from song 
# generate chord images

