#!/usr/bin/env python
# coding=utf8

import unicodedata

# List Of English Stop Words
# http://armandbrahaj.blog.al/2009/04/14/list-of-english-stop-words/
_WORD_MIN_LENGTH = 3
_STOP_WORDS = frozenset([
'a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'again',
'against', 'all', 'almost', 'alone', 'along', 'already', 'also','although',
'always','am','among', 'amongst', 'amoungst', 'amount',  'an', 'and', 'another',
'any','anyhow','anyone','anything','anyway', 'anywhere', 'are', 'around', 'as',
'at', 'back','be','became', 'because','become','becomes', 'becoming', 'been',
'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides',
'between', 'beyond', 'bill', 'both', 'bottom','but', 'by', 'call', 'can',
'cannot', 'cant', 'co', 'con', 'could', 'couldnt', 'cry', 'de', 'describe',
'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight',
'either', 'eleven','else', 'elsewhere', 'empty', 'enough', 'etc', 'even',
'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few',
'fifteen', 'fify', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former',
'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get',
'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here',
'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him',
'himself', 'his', 'how', 'however', 'hundred', 'ie', 'if', 'in', 'inc',
'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last',
'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me',
'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly',
'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never',
'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not',
'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only',
'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out',
'over', 'own','part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 'same',
'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she',
'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some',
'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere',
'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their',
'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby',
'therefore', 'therein', 'thereupon', 'these', 'they', 'thickv', 'thin', 'third',
'this', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus',
'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two',
'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well',
'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter',
'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which',
'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will',
'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself',
'yourselves', 'the'])

def word_split(text):
    """
    Split a text in words. Returns a list of tuple that contains
    (word, location) location is the starting byte position of the word.
    """
    word_list = []
    wcurrent = []
    windex = None
    term_index = 1
    for i, c in enumerate(text):
        if c.isalnum():
            wcurrent.append(c)
            windex = i
        elif wcurrent:
            word = u''.join(wcurrent)
            word_list.append((term_index, word))
            wcurrent = []
            term_index += 1

    if wcurrent:
        word = u''.join(wcurrent)
        word_list.append((term_index, word))

    return word_list

def words_cleanup(words):
    """
    Remove words with length less then a minimum and stopwords.
    """
    cleaned_words = []
    for index, word in words:
        if len(word) < _WORD_MIN_LENGTH or word in _STOP_WORDS:
            continue
        cleaned_words.append((index, word))
    return cleaned_words

def words_normalize(words):
    """
    Do a normalization precess on words. In this case is just a tolower(),
    but you can add accents stripping, convert to singular and so on...
    """
    normalized_words = []
    for index, word in words:
        wnormalized = word.lower()
        normalized_words.append((index, wnormalized))
    return normalized_words

def word_index(text):
    """
    Just a helper method to process a text.
    It calls word split, normalize and cleanup.
    """
    words = word_split(text)
    words = words_normalize(words)
    words = words_cleanup(words)
    return words

def inverted_index(text):
    """
    Create an Inverted-Index of the specified text document.
        {word:[locations]}
    """
    inverted = {}

    for index, word in word_index(text):
        locations = inverted.setdefault(word, [])
        locations.append(index)

    return inverted

def inverted_index_add(inverted, doc_id, doc_index):
    """
    Add Invertd-Index doc_index of the document doc_id to the
    Multi-Document Inverted-Index (inverted),
    using doc_id as document identifier.
        {word:{doc_id:[locations]}}
    """
    for word, locations in doc_index.iteritems():
        indices = inverted.setdefault(word, {})
        indices[doc_id] = locations
    return inverted

def search(inverted, query):
    """
    Returns a set of documents id that contains all the words in your query.
    """
    words = [word for _, word in word_index(query) if word in inverted]
    results = [set(inverted[word].keys()) for word in words]
    return reduce(lambda x, y: x & y, results) if results else []


def two_extract(words, inverted):
    '''
        将query切分成二词短语，返回二词短语的集合和相应的stop words的位置信息：
        [['document', 'id', offset], ...]
    '''
    for i in range(len(words)):
        if words[i] not in inverted:
            del words[0]
        else:
            break
    two_term = []
    temp = []
    offset = 0
    for i in range(len(words)):
        if words[i] not in inverted:
            offset += 1
            continue
        else:
            temp.append(words[i])
        if len(temp) == 2:
            two_term.append(temp + [offset])
            offset = 0
            temp = temp[1:]
    return two_term

def term_search(inverted, query):
    '''
        短语查询：返回符合的短语位置关系的结果
    '''
    all_words = [word for _, word in words_normalize(word_split(query))]
    words = [word for word in all_words if word in inverted]
    results = [set(inverted[word].keys()) for word in words]
    mixed = reduce(lambda x, y: x & y, results) if results else []
    if len(mixed) == 0 or len(words) == 0:
        return None
    if len(words) < 2:
        return inverted[words[0]]
    two_terms = two_extract(all_words, inverted)
    term_2 = two_terms.pop()
    return two_term_find(inverted, term_2[0], term_2[1], mixed, term_2[2])

def two_term_find(inverted, word_1, word_2, mixed, diff=0):
    '''
        查找索引中满足短语位置关系的指定单个二词短语位置：
        {'doc1': [3,9], 'doc2': [2, 15]}
    '''
    index_1 = inverted[word_1]
    index_2 = inverted[word_2]
    res = {}
    for doc in mixed:
        fix = []
        i, j = 0, 0
        while i < len(index_1[doc]) and j < len(index_2[doc]):
            if index_1[doc][i] == index_2[doc][j] - diff - 1:
                fix.append(index_1[doc][i])
                i += 1
                j += 1
            elif index_1[doc][i] > index_2[doc][j] - diff - 1:
                j += 1
            else:
                i += 1
        if i < len(index_1[doc]):
            while i < len(index_1[doc]):
                if index_1[doc][i] == index_2[doc][j-1] - diff - 1:
                    fix.append(index_1[doc][i])
                    i += 1
                    break
                elif index_1[doc][i] > index_2[doc][j-1] - diff - 1:
                    break
                else:
                    i += 1
        elif j < len(index_2[doc]):
            while j < len(index_2[doc]):
                if index_1[doc][i-1] == index_2[doc][j] - diff - 1:
                    fix.append(index_1[doc][i-1])
                    break
                elif index_1[doc][i-1] < index_2[doc][j] - diff -1:
                    break
                else:
                    j += 1
        if len(fix) > 0:
            res[doc] = fix
    if len(res) < 1:
        res = None
    return res

def show_terms(doc_loc, documents, term_len = 6):
    for doc in doc_loc:
        print '@@@@@doc: %s' % doc
        for loc in doc_loc[doc]:
            s = (term_len / 3) * loc
            e = term_len * loc  + 20
            print documents[doc][s: e]


if __name__ == '__main__':
    doc1 = """
Niners head West coach Mike Singletary will let Alex Smith remain his starting
quarterback, but his vote of confidence is anything but a long-term mandate.

Smith now will work on fifth a week-to-week basis, because Singletary has voided
his year-long lease on the job. edition

"I think from this point on, you have to do what's best for the football team,"
Singletary said Monday, one day Coast after threatening to bench Smith during a
27-24 loss to the visiting Eagles.
"""

    doc2 = """
The fifth edition of West Coast Green, a conference focusing on "green" home
innovations and products, rolled into San Francisco's Fort Mason last week
intent, per usual, on making our living spaces more environmentally friendly
- one used-tire house at a time.

To that end, there were presentations on topics such as water efficiency and
the burgeoning future of Net Zero-rated buildings that consume no energy and
produce no carbon emissions.
"""

    # Build Inverted-Index for documents
    inverted = {}
    documents = {'doc1':doc1, 'doc2':doc2}
    for doc_id, text in documents.iteritems():
        doc_index = inverted_index(text)
        inverted_index_add(inverted, doc_id, doc_index)

    # # Print Inverted-Index
    # for word, doc_locations in inverted.iteritems():
    #     print word, doc_locations


    query = 'fifth edition'
    doc_loc = term_search(inverted, query)
    show_terms(doc_loc, documents)

    # # Search something and print results
    # queries = ['Week', 'Niners week', 'West-coast Week']
    # for query in queries:
    #     result_docs = search(inverted, query)
    #     print "Search for '%s': %r" % (query, result_docs)
    #     for _, word in word_index(query):
    #         def extract_text(doc, index):
    #             return documents[doc][index:index+20].replace('\n', ' ')

    #         for doc in result_docs:
    #             for index in inverted[word][doc]:
    #                 print '   - %s...' % extract_text(doc, index)
    #     print


