#!/bin/sh
OUTPUT=circuit_markup/antlr
rm -rf $OUTPUT/*
antlr4 -Dlanguage=Python3 -no-listener -visitor CircuitMarkup.g4 -o $OUTPUT
