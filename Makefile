CC      = gcc
CFLAGS  = -Wall -Wextra -O2 -std=c11 -D_POSIX_C_SOURCE=199309L

# rpi-rgb-led-matrix install root (override with: make MATRIX_ROOT=~/rpi-rgb-led-matrix)
MATRIX_ROOT ?= /usr/local
MATRIX_CFLAGS = -I$(MATRIX_ROOT)/include
MATRIX_LIBS   = -L$(MATRIX_ROOT)/lib -lrgbmatrix -lstdc++ -lrt -lm -lpthread

SRCS = main.c tetris_pieces.c tetris_anim.c tetris_clock.c tetris_render.c
HDRS = tetris_data.h tetris_pieces.h tetris_anim.h tetris_clock.h tetris_render.h

.PHONY: all test clean

all: tetris-clock

tetris-clock: $(SRCS) $(HDRS)
	$(CC) $(CFLAGS) $(MATRIX_CFLAGS) -o $@ $(SRCS) $(MATRIX_LIBS)

test: tetris-clock-test

tetris-clock-test: $(SRCS) $(HDRS) stb_image_write.h
	$(CC) $(CFLAGS) -DTEST_MODE -o $@ $(SRCS) -lm

clean:
	rm -f tetris-clock tetris-clock-test
