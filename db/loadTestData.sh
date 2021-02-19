#!/bin/bash
psql 'postgres://masteruser:password@localhost:5432/nasadb?options=--search_path%3dapt' -f ./testData.sql
#psql 'postgres://masteruser:password@localhost:5432/nasadb?options=--search_path%3dapt' -f ./testDataFullAtbd.sql
