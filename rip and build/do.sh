rm music christmas-songs fetchpages.sh fetchpdf.sh songbook.pdf
rm pages/* pdf/*
wget http://www.wymondhamukulelegroup.com/music
wget http://www.wymondhamukulelegroup.com/christmas-songs
cat christmas-songs >>music
grep 'href=\"http' music|grep '<li>'| sed -r 's/.*(http.*)\/".*/wget -P pages \1/' >fetchpages.sh
sh fetchpages.sh
grep pdf pages/* | grep "gde-text"|sed -r 's/.*(http.*pdf).*/ wget -P pdf \1/'|uniq >fetchpdf.sh
sh fetchpdf.sh
pdfunite pdf/*.pdf songbook.pdf