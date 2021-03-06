#
#	Generate chord images, requires Pillow.
#
from PIL import Image,ImageDraw,ImageFont

def xPos(n):
	return int((n+0.5)/4*128)

def yPos(n):
	return int(n * 256 / 5)

def create(tgtFile,fretting):
	image = Image.new("RGBA",(128,256),color=(255,255,255,0))	
	d = ImageDraw.Draw(image)
	for s in range(0,4):
		x = xPos(s)
		d.rectangle((x-2,0,x+2,256),fill=(0,0,0,255))
	for s in range(0,6):
		y = yPos(s)
		h = 8 if s == 0 else 4
		if s == 5:
			y = y - h
		d.rectangle((xPos(0),y,xPos(3),y+h),fill=(0,0,0,255))
	for s in range(0,4):
		fret = int(fretting[s])
		if fret > 0:
			x = xPos(s)
			y = yPos(fret-0.3)
			w = 12
			d.ellipse((x-w,y-w,x+w,y+w),fill=(0,0,0,255))
	image.save(tgtFile)

if __name__ == '__main__':
	# add chords here, any old how will do as long as there's spacing.
	chords = """
		c:0003 c7:0002 c6:0001
		d:2220 d7:2223 dm:2210
		f:2010
		g:0232	g7:0212
		a:2100 am:2000 a7:0100
	"""

	chords = chords.replace("\t"," ").replace("\n"," ").split(" ")
	for c in chords:
		if c != "":
			c = c.split(":")
			create("target/images/"+c[0]+".png",c[1])
