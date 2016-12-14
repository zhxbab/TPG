DIR = std start
all:  
	@for i in ${DIR};\
	do cd $${i} && make && cd ..; \
	done
 
.PHONY:clean
clean:
	@for i in ${DIR};\
	do cd $${i} && make clean && cd ..; \
	done
	