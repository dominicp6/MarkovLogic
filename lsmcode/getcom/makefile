INLINE_LIMIT=-finline-limit=100000

PROGRAM = getcom
HEADERS = 
SOURCES = main.cpp gndnode.cpp clustnode.cpp clustedge.cpp path.cpp
OBJECTS = main.o gndnode.o clustnode.o clustedge.o path.o

# some useful others that you may need to edit
CC = g++
NO_DEPREC=-Wno-deprecated
INCLUDE=-I../util -I../pfind
#CFLAGS = -Wall -ansi -g $(NO_DEPREC) $(INCLUDE) $(INLINE_LIMIT)
#CFLAGS = -O3 $(NO_DEPREC) $(INCLUDE) $(INLINE_LIMIT)
CFLAGS = -O3 $(NO_DEPREC) -DNDEBUG $(INCLUDE) $(INLINE_LIMIT)
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
# dependencies generated on:  Tue May 11 12:03:56 BST 2021
#
main.o: main.cpp graph.h uuutil.h win.h ../util/array.h ../util/random.h \
 ../util/util.h ../util/array.h gndnode.h ../util/hashint.h \
 ../util/hasharray.h gndedge.h ../util/hashstring.h ../util/hashint.h \
 clustnode.h clustedge.h nodeids.h comcreator.h ../util/timer.h path.h \
 ../pfind/atom.h comgnder.h

gndnode.o: gndnode.cpp gndnode.h ../util/util.h ../util/array.h \
 ../util/random.h ../util/hashint.h ../util/hasharray.h ../util/array.h

clustnode.o: clustnode.cpp clustnode.h ../util/array.h ../util/random.h \
 gndnode.h ../util/util.h ../util/array.h ../util/hashint.h \
 ../util/hasharray.h clustedge.h win.h gndedge.h ../util/hashstring.h \
 ../util/hashint.h

clustedge.o: clustedge.cpp clustedge.h win.h ../util/util.h \
 ../util/array.h ../util/random.h gndedge.h ../util/hashstring.h \
 ../util/hasharray.h ../util/hashint.h ../util/array.h gndnode.h \
 ../util/hashint.h clustnode.h

path.o: path.cpp path.h ../util/hashstring.h ../util/hasharray.h \
 ../util/random.h ../util/hashint.h ../util/array.h ../pfind/atom.h \
 ../util/util.h

