CC ?= cc

app: main.o
	$(CC) main.o -o app

main.o: main.c config.h missing.h
	$(CC) -c main.c -o main.o

clean:
	rm -f main.o app app.exe
