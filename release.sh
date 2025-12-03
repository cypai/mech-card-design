#!/usr/bin/env bash
rm -rf ./steelvanguard
mkdir -p ./steelvanguard
cp -r ./outputs ./steelvanguard/pngs
cp ./*.pdf ./steelvanguard
cp ./changelog/changelog.txt ./steelvanguard
zip -r steelvanguard.zip ./steelvanguard
