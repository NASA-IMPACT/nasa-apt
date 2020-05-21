#!/usr/bin/env bash

# copied from prototype script @ https://github.com/developmentseed/nasa-apt/blob/eb0b6bc897efa29284dd11b4e46b085f388d9743/ecs/pdf/entrypoint.sh
# - removed s3 commands
# - removed extra bibtex command
# - removed invalid echo status messages, e.g. 'Successfully wrote TeX file'

# TODO: check exit codes of each command (pdflatex and bibtex) and figure out error handling strategy. https://github.com/developmentseed/nasa-apt/issues/177
# TODO: there are errors but pdf is still produced by this script. (for example  bash `set -e` will cause script to fail)
# TODO: try pdflatex -halt-on-error option
# TODO: try --draftmode to prevent duplicate pdf generation https://github.com/developmentseed/nasa-apt/issues/253

basename=$(basename $1 .tex)

# 3 passes is correct
# https://tex.stackexchange.com/questions/53235/why-does-latex-bibtex-need-three-passes-to-clear-up-all-warnings#53236

pdflatex --shell-escape "\def\convertType{PDF}\input{$1}"
bibtex $basename
pdflatex --shell-escape "\def\convertType{PDF}\input{$1}"
pdflatex --shell-escape "\def\convertType{PDF}\input{$1}"
