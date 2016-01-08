'''
Simple ahocorasick implementation entirely written in python.
Supports unicode.

Slightly optimized.

TODO: optimize moar!

Created on Jan 5, 2016

@author: frederik
'''


class KeywordTree:

    def __init__(self):
        self._zero_state = {'id': 0, 'success': False, 'transitions': {}}
        self._state_count = 1
        self._finalized = False
        self._states = [self._zero_state]

    def add(self, keyword):
        if self._finalized:
            raise ValueError('KeywordTree has been finalized.' +
                             ' No more keyword additions allowed')
        if len(keyword) <= 0:
            return
        current_state = self._zero_state
        idx = 0
        next_state = None
        symbol = keyword[idx:idx + 1]
        if symbol in current_state['transitions']:
            next_state = self._states[current_state['transitions'][symbol]]
        while next_state is not None:
            current_state = next_state
            idx += 1
            next_state = None
            symbol = keyword[idx:idx + 1]
            if symbol in current_state['transitions']:
                next_state = self._states[current_state['transitions'][symbol]]
        while idx < len(keyword):
            new_state = {
                'id': self._state_count, 'success': False, 'transitions': {},
                'parent': current_state['id']}
            self._states.append(new_state)
            current_state['transitions'][
                keyword[idx:idx + 1]] = self._state_count
            current_state = new_state
            self._state_count += 1
            idx += 1
        current_state['success'] = True
        current_state['matched_keyword'] = keyword

    def search(self, text):
        if not self._finalized:
            raise ValueError('KeywordTree has not been finalized.' +
                             ' No search allowed. Call finalize() first.')
        current_state = self._zero_state
        for idx, symbol in enumerate(text):
            next_state = None
            if symbol in current_state['transitions']:
                next_state = self._states[current_state['transitions'][symbol]]
            else:
                traversing = current_state
                while traversing['longest_strict_suffix'] is not None:
                    if symbol in traversing['transitions']:
                        next_state = self._states[
                            traversing['transitions'][symbol]]
                        break
                    traversing = self._states[
                        traversing['longest_strict_suffix']]
                if next_state is None:
                    next_state = self._zero_state
            current_state = next_state
            if current_state['success']:
                keyword = current_state['matched_keyword']
                return (keyword, idx + 1 - len(keyword))

    def finalize(self):
        if self._finalized:
            raise ValueError('KeywordTree has already been finalized.')
        finalizer = Finalizer(self)
        finalizer.finalize()
        self._finalized = True

    def __str__(self):
        return "ahocorapy KeywordTree with %i states." % self._state_count


class Finalizer:

    def __init__(self, keyword_tree):
        self._keyword_tree = keyword_tree
        self._states = keyword_tree._states

    def finalize(self):
        zero_state = self._keyword_tree._zero_state
        zero_state['longest_strict_suffix'] = None
        self.search_longest_strict_suffixes_for_children(zero_state)

    def search_longest_strict_suffixes_for_children(self, state):
        for symbol, childid in state['transitions'].iteritems():
            child = self._states[childid]
            self.search_longest_strict_suffix(child, symbol)
            self.search_longest_strict_suffixes_for_children(child)

    def search_longest_strict_suffix(self, state, symbol):
        if 'longest_strict_suffix' not in state:
            parent = self._states[state['parent']]
            if parent['id'] == 0:
                state['longest_strict_suffix'] = 0
            else:
                found_suffix = False
                if 'longest_strict_suffix' not in parent:
                    # Has not been done yet. Do early
                    self.search_longest_strict_suffix(parent, symbol)
                traversed = self._states[parent['longest_strict_suffix']]
                while not found_suffix:
                    if symbol in traversed['transitions']:
                        state['longest_strict_suffix'] = traversed[
                            'transitions'][symbol]
                        found_suffix = True
                    elif traversed['id'] == 0:
                        state['longest_strict_suffix'] = 0
                        found_suffix = True
                    else:
                        if 'longest_strict_suffix' not in traversed:
                            # Has not been done yet. Do early
                            self.search_longest_strict_suffix(
                                traversed, symbol)
                        traversed = self._states[
                            traversed['longest_strict_suffix']]
