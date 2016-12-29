#DIRS = std start string
#OBJS = std/stdio.o string/string.o threads/threads.o
DIRS = threads
OBJS = threads/ktpg_threads.o
all:  
	@for i in ${DIRS};\
	do cd $${i} && make && cd ..; \
	done
	ar -rcvs libktpg.a ${OBJS}
 	
.PHONY:clean
clean:
	@for i in ${DIRS};\
	do cd $${i} && make clean && cd ..; \
	done
	rm -f libktpg.a
	