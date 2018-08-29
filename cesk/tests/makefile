SRC = $(shell find ./ -name '*.c')
TAR = $(SRC:.c=.pkl)

.PHONY: all

all: $(TAR)

%.pkl : %.c
	python3 ../../main.py -t save $^

clean:
	rm -fr $(TAR)