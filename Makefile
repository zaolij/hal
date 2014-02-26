VERSION = `git rev-parse HEAD`
MODEL=uno

.PHONY: upload build clean

all: upload
build: arduino/.build/uno/firmware.hex

arduino/.build/uno/firmware.hex: arduino/src/sketch.ino
	cd arduino && ino build -m=$(MODEL)

arduino/src/sketch.ino: arduino/src/sketch.ino.tpl .git
	sed -e "s/{{version}}/${VERSION}/" < $< > $@

upload: arduino/.build/uno/firmware.hex
	cd arduino && ino upload -m=$(MODEL)

clean:
	rm -f arduino/src/sketch.ino
	cd arduino && ino clean
