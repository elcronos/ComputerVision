#!/usr/bin/env python

import cv2, numpy as np
import sys
import time
from player  import Player, PlayerState, PlayerCmd

def PrintUsage():
    print \
      "\npython main.py filename\n" \
      "Click the video window, and control by:\n" \
      "  | key   | action        |\n" \
      "  | p     | Play          |\n" \
      "  | f     | Freeze(pause) |\n" \
      "  | m     | Next frame    |\n" \
      "  | n     | Prev frame    |\n" \
      "  | s     | Screenshot    |\n" \
      "  | Esc   | Exit          |\n"

def main():
    player = Player(sys.argv[1])
    player.Start()

    while True:
        try:
            cmd = 'none'
            cmd = {ord('f'): 'freeze',
                   ord('p'): 'play',
                   ord('n'): 'prev_frame',
                   ord('m'): 'next_frame',
                   ord('s'): 'screenshot',
                   -1      : cmd,
                   27      : 'exit'}[cv2.waitKey(10)]
            if cmd == 'play':
                player.Play()
            if cmd == 'freeze':
                player.Pause()
            if cmd == 'exit':
                player.Stop()
                break
            if cmd == 'prev_frame':
                player.SeekTo(player.GetCurPos() - 1)
                player.Pause()
            if cmd == 'next_frame':
                player.SeekTo(player.GetCurPos() + 1)
                player.Pause()
            if cmd == 'screenshot':
                player.SaveCurFrame()
                player.Pause()
        except KeyError:
            print "Invalid Key was pressed"
        except (KeyboardInterrupt):
            print "KeyboardInterrupt in main()"
            player.Stop()
            sys.exit()

if __name__ == "__main__":
    PrintUsage()
    if len(sys.argv) < 2 :
        print "Error input params"
        sys.exit(-1)
    main()
