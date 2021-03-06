"""
This module defines several functions for use with PyLautLang, both
internally and externally in the form of user-callable library functions.
"""

from pylaut.change import change, change_functions
from pylaut.language.phonology.phone import Phone
from typing import Any


def make_predicate(parser_entity):
    """
    This function creates a predicate on a Phone to use with
    Change.to. It switches on types to determine how best to construct
    such a predicate.
    """

    def default(_: Any) -> bool:
        return True

    predicate = default

    # We have a feature expression
    if isinstance(parser_entity, dict):
        predicates = []
        for k, v in parser_entity.items():
            predicates.append(lambda p, k=k, v=v: p.feature_is(k, v))

        def feature_predicate(p, predicates=predicates):
            for f in predicates:
                if not f(p):
                    return False
            return True

        predicate = feature_predicate
    # A phoneme
    elif isinstance(parser_entity, Phone):

        def phone_predicate(p, t=parser_entity):
            return p.is_symbol(t.symbol)

        predicate = phone_predicate
    # An improper phoneme
    elif isinstance(parser_entity, str):

        def symbol_predicate(p, t=parser_entity):
            return p.is_symbol(t)

        predicate = symbol_predicate
    # A phoneme list
    elif isinstance(parser_entity, tuple):
        predicates = []
        for t in parser_entity:
            predicates.append(lambda p, t=t: p.is_symbol(t.symbol))

        def list_predicate(p, t=predicates):
            return all(f(p) for f in t)

        predicate = list_predicate
    elif isinstance(parser_entity, list):
        return make_predicate(parser_entity[0])

    return predicate


def metathesis(left, right):
    pl = make_predicate(left)
    pr = make_predicate(right)

    def exchange(this):
        current = this.phonemes.index(this.phoneme)
        sylidx = this.syllable.phonemes.index(this.phoneme)
        try:
            next = this.phonemes[current + 1]
        except IndexError:
            return
        this.phonemes[current] = next
        this.phonemes[current + 1] = this.phoneme
        this.syllable.phonemes[sylidx] = next
        try:
            this.syllable.phonemes[sylidx + 1] = this.phoneme
        except IndexError:
            cursyl = this.syllables.index(this.syllable)
            this.syllables[cursyl + 1].phonemes[0] = this.phoneme
        this.advance()
        return next

    def defer(this):
        return exchange(this)

    return change.Change().do(defer).to(change.This.forall(Phone)(pl)).when(
        change.This.at(Phone, 1, pr))


def lengthen(phone):
    return change.Change().do(
        lambda this: change_functions.change_feature(
            this.phoneme, "long", True)
    ).to(change.This.forall(Phone)(make_predicate(phone)))


def intervocal_voicing(this):
    return change.Change().do(
        lambda this: change_functions.change_feature(
            this.phoneme, "voice", True)).to(
            change.This.forall(Phone)(make_predicate(this))).when(
                change.This.at(Phone, -1, lambda p: p.is_vowel())).when(
                    change.This.at(Phone, 1, lambda p: p.is_vowel()))


def merge(phonemes, target):
    target = target[0]
    phonemes = [p[0] for p in phonemes]
    return change.Change().do(lambda _: target).to(
        change.This.forall(Phone)(
            lambda p: any(p.is_symbol(b.symbol) for b in phonemes)))


def epenthesis(this, phoneme):
    p = make_predicate(this)

    if len(phoneme) == 1:
        phoneme = phoneme[0]

    def epenthesize(td, p=p, t=phoneme):
        if p(td.phoneme):
            cur_idx = td.phonemes.index(td.phoneme)
            syl_idx = td.syllable.phonemes.index(td.phoneme)
            td.phonemes.insert(cur_idx + 1, t)
            td.syllable.phonemes.insert(syl_idx + 1, t)
            td.advance()
            return td.phoneme
        return td.phoneme

    return change.Change().do(epenthesize).to(change.This.forall(Phone)(p))


def resyllabify(*args):
    return change_functions.Resyllabify()


def get_library():
    library = {
        "__name__": "libpylautlang",
        "__version__": "0.1.0",
        "__file__": __file__,
        "__module_name__": __name__,
        "Metathesis": metathesis,
        "Lengthen": lengthen,
        "IntervocalVoicing": intervocal_voicing,
        "Merge": merge,
        "Epenthesis": epenthesis,
        "Resyllabify": resyllabify
    }

    return library
