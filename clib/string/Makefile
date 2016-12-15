FILE = string
CC = gcc
CFLAGS = -O0 -std=gnu99 -nostdlib -nostdinc -fno-builtin -fno-asynchronous-unwind-tables

all:
	${CC} -c ${CFLAGS} ${FILE}.c -o ${FILE}.o
	
.PHONY:clean
clean:
	rm -f *.o