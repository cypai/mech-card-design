#!/usr/bin/env bash

git pull
source ./venv/bin/activate

read -p "Render cards? (y: all, n: skip, c: custom) " ync
case $ync in
  [yY] )
    ./card_rendering.py all
    ;;
  [cC] )
    read -p "What would you like to render? " op
    read -p "Filters? " filters
    case $filters in
      [nN] )
        ./card_rendering.py $op -f $filters
        ;;
      * )
        ./card_rendering.py $op
        ;;
    esac
    ;;
  [nN] ) echo "Skipping render.";;
  * ) echo "Invalid response";;
esac

sudo systemctl restart discord-bot.service
