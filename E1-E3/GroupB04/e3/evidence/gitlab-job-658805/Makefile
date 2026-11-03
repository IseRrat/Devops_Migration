CC ?= cc
CFLAGS ?= -O2

.PHONY: all clean

all: hello

hello: main.o
	$(CC) $(CFLAGS) main.o -o hello

main.o: main.c
	$(CC) $(CFLAGS) -c main.c -o main.o

clean:
	rm -f hello main.o
