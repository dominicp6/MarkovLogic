INLINE_LIMIT=-finline-limit=100000

PROGRAM = rwl
HEADERS = 
SOURCES = main.cpp constant.cpp
OBJECTS = main.o constant.o

# some useful others that you may need to edit
CC = g++
NO_DEPREC=-Wno-deprecated
INCLUDE=-I../util
#CFLAGS = -Wall -ansi -g $(NO_DEPREC) $(INCLUDE) $(INLINE_LIMIT)
#CFLAGS = -O3 $(NO_DEPREC) $(INCLUDE) $(INLINE_LIMIT)
CFLAGS = -O3 -g $(NO_DEPREC) -DNDEBUG $(INCLUDE) $(INLINE_LIMIT)
LIBS = 

# name of this file
MF = makefile

.SUFFIXES: .o .h .cpp

# ------------- Stuff you shouldn't have to change ------------------

.cpp.o:
	$(CC) $(CFLAGS) -c -o $*.o $<

$(PROGRAM): $(OBJECTS)
	$(CC) -o $(PROGRAM) $(CFLAGS) $(OBJECTS) $(LIBS)

all:
	make $(PROGRAM)

clean: 
	@rm -f *.o $(PROGRAM)

cleant: 
	@rm -f *~

depend:
	@echo 'updating the dependencies for:'
	@echo '    ' $(SOURCES)
	@{ \
	< $(MF) sed -n '1,/^###.*DO NOT CHANGE ANYTHING BELOW HERE/p'; \
		echo '#' ; \
		echo '# dependencies generated on: ' `date` ; \
		echo '#' ; \
		for i in $(SOURCES); do \
			$(CC) -MM $(CFLAGS) $$i ; \
			echo; \
		done \
	} > $(MF).new
	@mv $(MF) $(MF).last
	@mv $(MF).new $(MF)

############ DO NOT CHANGE ANYTHING BELOW HERE #####
#
# dependencies generated on:  Thu Jun 3 17:59:16 BST 2021
#
main.o: main.cpp rwlearner.h ../util/hashint.h ../util/hasharray.h \
 ../util/random.h ../util/array.h ../util/timer.h node.h ../util/util.h \
 uutil.h win.h ../util/array.h constant.h predicate.h outlink.h \
 samplepath.h parser.h ../util/hashstring.h ../util/hashint.h \
 ../util/rbtree.h graph.h nodecluster.h community.h type.h

constant.o: constant.cpp constant.h type.h ../util/array.h \
 ../util/random.h

