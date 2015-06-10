# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import re
import operator
import subprocess

def vectorize(corpus_file):
  with open(corpus_file) as f:
    data = unicode(f.read(), "utf-8")
  data = re.findall(ur"(#[\d]+)([^#]*)(?#[\d]+)", data, re.DOTALL)
  sentences = []

  for item in data:
    notes = item[1].split(".")
    for note in notes:
      words_in_note = [word.lower() for word in re.findall(ur"[a-zA-ZżółćęśąźńŻÓŁĆĘŚĄŹŃ]+", note)]
      sentences = sentences + [words_in_note]
  return sentences

def filter_sentences(sentences, preposition):
  filtered_sentences = []
  for sentence in sentences:
    count = False
    new_sentence = []
    for word in sentence:
      if count:
        new_sentence.append(word)
      if word == preposition:
        count = True
    if len(new_sentence) > 0:
      filtered_sentences = filtered_sentences + [new_sentence]
  return filtered_sentences

def wordcount(words):
  dictionary = {}
  for word in words:
    if word not in dictionary:
      dictionary[word] = 1
    else:
      dictionary[word] += 1
  return dictionary

def call_morfologik(first_words):
  p = subprocess.Popen(['java', '-jar', 'morfologik-tools-1.9.0-standalone.jar', 'plstem'],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
  out, _ = p.communicate(u" ".join(first_words.keys()).encode("utf-8"))
  return out

def parse_output(morfologik_output, words_dictionary):
  parts_of_sentence = {}
  data = re.findall(ur"^([a-zA-ZżółćęśąźńŻÓŁĆĘŚĄŹŃ-]+)\s+([a-zA-ZżółćęśąźńŻÓŁĆĘŚĄŹŃ -]+)\s+([a-zA-ZżółćęśąźńŻÓŁĆĘŚĄŹŃ0-9:+-.]+)$", unicode(morfologik_output, "utf-8"), re.DOTALL|re.MULTILINE)
  for item in data:
    forms = item[2].split(":")
    part = forms[2] if len(forms) > 2 else "undefined"
    if item[0] in words_dictionary:
      if part not in parts_of_sentence:
        parts_of_sentence[part] = words_dictionary[item[0]]
      else:
        parts_of_sentence[part] += words_dictionary[item[0]]
  return parts_of_sentence

def take_nth_word_after_preposition(sentences, index=0):
  first_words = [words[index] for words in sentences if len(words) > index]
  return first_words


if __name__ == '__main__':
  if len(sys.argv) >= 3:
    corpus_file = sys.argv[1]
    preposition = sys.argv[2]
    index = int(sys.argv[3]) if len(sys.argv) > 3 else 0

  sentences = vectorize(corpus_file)
  sentences = filter_sentences(sentences, preposition)
  first_words = take_nth_word_after_preposition(sentences, index=index)
  words_dictionary = wordcount(first_words)
  output = call_morfologik(words_dictionary)

  parts_of_sentence = parse_output(output, words_dictionary)
  for item in sorted(parts_of_sentence.items(), key=operator.itemgetter(1), reverse=True):
    print item[0], " : ", item[1]


