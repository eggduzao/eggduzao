#!/bin/bash
# Create Alien Dictionaries given known answers
# to test algorithm solution

echo "✨ Running 3 word-dict 2-2 ambiguous ✨"
python challenge_15.py \
       './input/test1-input-symbols.txt' \
       --output-path './output/test1-3-2-2.txt'

echo "✨ Running 100K word-dict 10-100 unique ✨"
python challenge_15.py \
       './input/test1-100K-10-100.txt' \
       --output-path './output/test1-100K-10-100.txt'

echo "✨ Running 100K word-dict 10-100 unique ✨"
python challenge_15.py \
       './input/test1-100K-10-100.txt' \
       --output-path './output/test1-100K-10-100.txt'

echo "✨ Running 10K word-dict 3-100 unique ✨"
python challenge_15.py \
       './input/test1-10K-3-100.txt' \
       --output-path './output/test1-10K-3-100.txt'

echo "✨ Running 1K word-dict 3-100 unique ✨"
python challenge_15.py \
       './input/test1-1K-3-100.txt' \
       --output-path './output/test1-1K-3-100.txt'

echo "✨ Running 250 word-dict 3-50 unique ✨"
python challenge_15.py \
       './input/test1-250-3-50.txt' \
       --output-path './output/test1-250-3-50.txt'

echo "✨ Running 100 word-dict 3-50 unique ✨"
python challenge_15.py \
       './input/test1-100-3-50.txt' \
       --output-path './output/test1-100-3-50.txt'

echo "✨ Running 25 word-dict 1-10 unique ✨"
python challenge_15.py \
       './input/test1-25-1-10.txt' \
       --output-path './output/test1-25-1-10.txt'

echo "✨ Running 10 word-dict 1-10 unique ✨"
python challenge_15.py \
       './input/test1-10-1-10.txt' \
       --output-path './output/test1-10-1-10.txt'

echo "✨ Running 5 word-dict 5-5 unique ✨"
python challenge_15.py \
       './input/test1-5-5-5.txt' \
       --output-path './output/test1-5-5-5.txt'

echo "✨ Running 3 word-dict 2-2 ambiguous ✨"
python challenge_15.py \
       './input/test1-3-2-2.txt' \
       --output-path './output/test1-3-2-2.txt'

echo "✨ Running 1 word-dict 25-25 unique ✨"
python challenge_15.py \
       './input/test1-1-25-25.txt' \
       --output-path './output/test1-1-25-25.txt'

echo "✨ Running 1 word-dict 20-20 ambiguous ✨"
python challenge_15.py \
       './input/test1-1-20-20.txt' \
       --output-path './output/test1-1-20-20.txt'

echo "✨ Running 1 word-dict 10-10 ambiguous ✨"
python challenge_15.py \
       './input/test1-1-10-10.txt' \
       --output-path './output/test1-1-10-10.txt'

echo "✨ Running 1 word-dict 1-1 ambiguous ✨"
python challenge_15.py \
       './input/test1-1-1-1.txt' \
       --output-path './output/test1-1-1-1.txt'

echo "✨ Running 0 word-dict 0-0 ambiguous ✨"
python challenge_15.py \
       './input/test1-0-0-0.txt' \
       --output-path './output/test1-0-0-0.txt'

echo "✅ Everything Done Under the Sun."
