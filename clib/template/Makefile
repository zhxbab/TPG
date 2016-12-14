FILE = template
CC = gcc
CFLAGS = -O0 -std=gnu99 -nostdlib -nostdinc -fno-builtin -fno-asynchronous-unwind-tables
START = ../start

all: start.o
	${CC} ${CFLAGS} ${START}/start.o ${FILE}.c -o ${FILE}.elf
	objdump -xsD ${FILE}.elf > ${FILE}.map
			
start.o:
	${MAKE} -C ${START}

	
.PHONY:clean
clean:
	rm -f *.o *.elf *.map