class excluder(object):
    """exclude bbs sections, board or assigned page"""
    def __init__(self):
        super(excluder, self).__init__()
        self.exclude_section = ['0']
        self.exclude_board = ['Announce', 'BBSLOG', 'Bet', 'BYRStar',
            'ForumCommittee', 'Progress', 'Score', 'sysop', 'Recommend'
        ]

    def only_uid_see_exclude(self, _parsed_url):
        query = _parsed_url.query
        if 'au' in query.split('=', 1):
            return True
        return False

    def section_exclude(self, _parsed_url):
        path = (_parsed_url.path).split('/', 3)     
        if 'section' not in path:
            return False
        for ele in self.exclude_section:
            if ele in path:
                return True
        return False

    def board_exclude(self, _parsed_url):
        path = (_parsed_url.path).split('/', 3)
        if 'board' not in path:
            return False
        for ele in self.exclude_board:
            if ele in path:
                return True
        return False

    def fit(self, _parsed_url):
        return self.only_uid_see_exclude(_parsed_url) or \
            self.section_exclude(_parsed_url) or \
            self.board_exclude(_parsed_url)
        