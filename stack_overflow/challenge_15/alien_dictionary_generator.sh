#!/bin/bash
# Create Alien Dictionaries given known answers
# to test algorithm solution

echo "✨ Creating 100K word-dict 10-100 unique ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-100K-10-100.txt' \
       --input-words 100000 \
       --min-word-size 10 \
       --max-word-size 100 \
       --seed 1987 \
       --mode unique

echo "✨ Creating 10K word-dict 3-100 unique ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-10K-3-100.txt' \
       --input-words 10000 \
       --min-word-size 3 \
       --max-word-size 100 \
       --seed 1987 \
       --mode unique

echo "✨ Creating 1K word-dict 3-100 unique ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-1K-3-100.txt' \
       --input-words 1000 \
       --min-word-size 3 \
       --max-word-size 100 \
       --seed 1987 \
       --mode unique

echo "✨ Creating 250 word-dict 3-50 unique ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-250-3-50.txt' \
       --input-words 250 \
       --min-word-size 3 \
       --max-word-size 50 \
       --seed 1987 \
       --mode unique

echo "✨ Creating 100 word-dict 3-50 ambiguous ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-100-3-50.txt' \
       --input-words 100 \
       --min-word-size 3 \
       --max-word-size 50 \
       --seed 1987 \
       --mode ambiguous \
       --enforce-prefix 10

echo "✨ Creating 25 word-dict 1-10 unique ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-25-1-10.txt' \
       --input-words 25 \
       --min-word-size 1 \
       --max-word-size 10 \
       --seed 1987 \
       --mode unique

echo "✨ Creating 10 word-dict 1-10 ambiguous ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-10-1-10.txt' \
       --input-words 10 \
       --min-word-size 1 \
       --max-word-size 10 \
       --seed 1987 \
       --mode ambiguous \
       --enforce-prefix 10

echo "✨ Creating 5 word-dict 5-5 unique ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-5-5-5.txt' \
       --input-words 5 \
       --min-word-size 5 \
       --max-word-size 5 \
       --seed 1987 \
       --mode unique

echo "✨ Creating 3 word-dict 2-2 ambiguous ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-3-2-2.txt' \
       --input-words 3 \
       --min-word-size 5 \
       --max-word-size 5 \
       --seed 1987 \
       --mode ambiguous \
       --enforce-prefix 10

echo "✨ Creating 1 word-dict 25-25 unique ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-1-25-25.txt' \
       --input-words 1 \
       --min-word-size 25 \
       --max-word-size 25 \
       --seed 1987 \
       --mode unique

echo "✨ Creating 1 word-dict 20-20 ambiguous ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-1-20-20.txt' \
       --input-words 1 \
       --min-word-size 20 \
       --max-word-size 20 \
       --seed 1987 \
       --mode ambiguous \
       --enforce-prefix 10

echo "✨ Creating 1 word-dict 10-10 ambiguous ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-1-10-10.txt' \
       --input-words 1 \
       --min-word-size 10 \
       --max-word-size 10 \
       --seed 1987 \
       --mode ambiguous \
       --enforce-prefix 5

echo "✨ Creating 1 word-dict 1-1 ambiguous ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-1-1-1.txt' \
       --input-words 1 \
       --min-word-size 1 \
       --max-word-size 1 \
       --seed 1987 \
       --mode ambiguous \
       --enforce-prefix 1

echo "✨ Creating 0 word-dict 0-0 ambiguous ✨"
python alien_dictionary_generator.py \
       --input-path './input/test1-input-symbols.txt' \
       --output-path './input/test1-0-0-0.txt' \
       --input-words 0 \
       --min-word-size 0 \
       --max-word-size 0 \
       --seed 1987 \
       --mode ambiguous \
       --enforce-prefix 0

echo "✅ Everything Done Under the Sun."
