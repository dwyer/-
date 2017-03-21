#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import random

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from texts.models import Phrase

from django.db.models import Avg


def get_input(limit):
    min = 1
    while True:
        n = raw_input('[%d-%d] ' % (min, limit))
        if n == 's':
            return n
        try:
            n = int(n)
            if n >= min and n <= limit:
                return n - 1
        except ValueError:
            pass


def get_data():
    answer = Phrase.objects.order_by('?').first()

    # choose the fields
    fields = ['phrase', 'romanization', 'translation']
    random.shuffle(fields)
    question_field = fields.pop()
    answer_field = fields.pop()

    answer_phrase = answer.phrase
    question = getattr(answer, question_field)
    answer = getattr(answer, answer_field)

    choices = Phrase.objects.order_by('?')
    choices = choices.exclude(**{answer_field: ''})
    choices = choices.exclude(**{question_field: ''})
    choices = choices.exclude(**{answer_field: answer})
    choices = choices.exclude(**{question_field: question})
    if 'translation' not in [answer_field, question_field]:
        choices = choices.extra(where=['length(phrase) = %d' % len(answer_phrase)])
    choices = choices[:2 if answer_field == 'romanization' else 5]
    choices = list(choices)
    choices = [getattr(choice, answer_field) for choice in choices]
    choices.append(answer)

    random.shuffle(choices)

    return {
        'question': question,
        'answer': answer,
        'choices': choices,
        'question_field': question_field,
        'answer_field': answer_field,
    }


total = 0
correct = 0
while 1:
    data = get_data()
    question = data['question']
    answer = data['answer']
    choices = data['choices']
    answer_field = data['answer_field']
    question_field = data['question_field']
    # print '%s -> %s' % (question_field, answer_field)
    print '%s:' % question_field
    print question
    print
    print '%s:' % answer_field
    for i, choice in enumerate(choices):
        print '[%d] %s' % (i+1, choice)
    choice = get_input(len(choices))
    if choice == 's':
        print 'skipping'
        print
        continue
    total += 1
    choice = choices[choice]
    if answer == choice:
        correct += 1
        print 'Correct!'
    else:
        print 'Answer: %s' % answer
    print '%d/%d (%0.1f%%)' % (correct, total, correct / float(total) * 100)
    print
exit()


funcs = [translation_to_original, original_to_translation]
while 1:
    try:
        data = random.choice(funcs)()
        print 'Q: %s' % data['question']
        for i, choice in enumerate(data['choices']):
            print '[%d] %s' % (i+1, choice)
        if get_input(len(data['choices'])) == data['answer'] + 1:
            print 'correct!'
        else:
            print 'A: %s' % data['choices'][data['answer']]
        print
    except EOFError:
        print '再見！'
        break
