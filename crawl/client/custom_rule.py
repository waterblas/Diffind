class excluder(object):
    """exclude bbs sections, board or assigned page"""
    def __init__(self):
        super(excluder, self).__init__()
        self.parsed_url = None
        self.url_path = None
        self.exclude_section = ['0']
        self.exclude_board = ['Announce', 'BBSLOG', 'Bet', 'BYRStar',
            'ForumCommittee', 'Progress', 'Score', 'sysop', 'Recommend'
        ]

    def only_uid_see_exclude(self):
        query = self.parsed_url.query
        if 'au' in query.split('=', 1):
            return True
        return False

    def section_exclude(self):
        if 'section' not in self.url_path:
            return False
        for ele in self.exclude_section:
            if ele in self.url_path:
                return True
        return False

    def board_exclude(self):
        if 'board' not in self.url_path:
            return False
        if len(self.url_path) == 4 and self.url_path[-1] in ['1', '3']:
            return True
        for ele in self.exclude_board:
            if ele in self.url_path:
                return True
        return False

    def single_article_exclude(self):
        if 'article' in self.url_path and 'single' in self.url_path:
            return True
        return False

    def fit(self, _parsed_url):
        self.parsed_url = _parsed_url
        self.url_path = (_parsed_url.path).split('/', 4)
        return self.only_uid_see_exclude() or self.section_exclude() or \
            self.board_exclude() or self.single_article_exclude()


class limiter(object):
    """only crawl page that has following feature"""
    def __init__(self, arg):
        super(debooster, self).__init__()
        self.parsed_url = None
        self.url_path = None

    def fit(self, url):
        return True


        