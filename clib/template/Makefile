FILE = template
CC = gcc
CFLAGS = -O0 -std=gnu99 -nostdlib -nostdinc -fno-builtin -fno-asynchronous-unwind-tables -static
START = ../start
SLIB = ../libktpg.a
BASE_DIR = ..

all: start.o
	${CC} ${CFLAGS} ${START}/start.o ${SLIB} ${FILE}.c -I${BASE_DIR}/include -L${BASE_DIR} -lktpg -o ${FILE}.elf
	objdump -xsD ${FILE}.elf > ${FILE}.map
			
start.o:
	${MAKE} -C ${START}
	
.PHONY:clean
clean:
	rm -f *.o *.elf *.map