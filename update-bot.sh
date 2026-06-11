#!/usr/bin/env bash

git pull
source ./venv/bin/activate

read -p "Render cards? (y: all, n: skip, c: custom)" ync
case $ync in
  [yY] )
    ./card_rendering.py all
    ;;
  [cC] )
    read "What would you like to render? " op
    ./card_rendering.py $op
    ;;
  [nN] ) echo "Skipping render.";;
  * ) echo "Invalid response";;
esac

sudo systemctl restart discord-bot.service
