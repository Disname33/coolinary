'use strict';

const COLS = 10;
const ROWS = 20;
const BLOCK_SIZE = (window.innerWidth < 390) ? (window.innerWidth - 90) / 10 : 30;
const BLOCK_SIZE_NEXT = 15;
const LINES_PER_LEVEL = 10;
const COLORS = [
  'none',
  'cyan',
  'blue',
  'orange',
  'yellow',
  'green',
  'purple',
  'red'
];

const COLORS_RGBA = {};

COLORS_RGBA['none'] = 'rgba(0, 0, 0, 0)';
COLORS_RGBA['cyan'] = 'rgba(0, 255, 255, 0.2)';
COLORS_RGBA['blue'] = 'rgba(0, 0, 255, 0.2)';
COLORS_RGBA['orange'] = 'rgba(255, 165, 0, 0.2)';
COLORS_RGBA['yellow'] = 'rgba(255, 255, 0, 0.2)';
COLORS_RGBA['green'] = 'rgba(0, 128, 0, 0.2)';
COLORS_RGBA['purple'] = 'rgba(128, 0, 128, 0.2)';
COLORS_RGBA['red'] = 'rgba(255, 0, 0, 0.2)';

Object.freeze(COLORS);

const SHAPES = [
  [],
  [
    [0, 0, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ],
  [
    [2, 0, 0],
    [2, 2, 2],
    [0, 0, 0]
  ],
  [
    [0, 0, 3],
    [3, 3, 3],
    [0, 0, 0]
  ],
  [
    [4, 4],
    [4, 4]
  ],
  [
    [0, 5, 5],
    [5, 5, 0],
    [0, 0, 0]
  ],
  [
    [0, 6, 0],
    [6, 6, 6],
    [0, 0, 0]
  ],
  [
    [7, 7, 0],
    [0, 7, 7],
    [0, 0, 0]
  ]
];
Object.freeze(SHAPES);

const POINTS = {
  SINGLE: 100,
  DOUBLE: 300,
  TRIPLE: 500,
  TETRIS: 800,
  SOFT_DROP: 1,
  HARD_DROP: 2,
}
Object.freeze(POINTS);

const LEVEL = {
  0: 800,
  1: 720,
  2: 630,
  3: 550,
  4: 470,
  5: 380,
  6: 300,
  7: 220,
  8: 130,
  9: 100,
  10: 80,
  11: 80,
  12: 80,
  13: 70,
  14: 70,
  15: 70,
  16: 50,
  17: 50,
  18: 50,
  19: 30,
  20: 30,
  // 29+ is 20ms
}
Object.freeze(LEVEL);
