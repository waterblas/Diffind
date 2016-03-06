# -*- coding: utf-8-*-
import re
from HTMLParser import HTMLParser

class TagParser:

    ##替换常用HTML字符实体.
    #使用正常的字符替换HTML中特殊的字符实体.
    #你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
    #@param htmlstr HTML字符串.
    def __replaceCharEntity(self, s):
        CHAR_ENTITIES={'nbsp':' ','160':' ',
                    'lt':'<','60':'<',
                    'gt':'>','62':'>',
                    'amp':'&','38':'&',
                    'quot':'"','34':'"',}
        
        re_charEntity=re.compile(r'&#?(?P<name>\w+);')
        sz=re_charEntity.search(s)
        while sz:
            entity=sz.group()#entity全称，如&gt;
            key=sz.group('name')#去除&;后entity,如&gt;为gt
            try:
                s=re_charEntity.sub(CHAR_ENTITIES[key],s,1)
                sz=re_charEntity.search(s)
            except KeyError:
                #以空串代替
                s=re_charEntity.sub('',s,1)
                sz=re_charEntity.search(s)
        return s   

    ##过滤HTML中的特殊标签
    #<?xml ...> <script/> <style />
    def filter_tags(self, htmlstr):
        #先过滤CDATA
        re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        re_br=re.compile('<br\s*?/?>')#处理换行
        # re_h=re.compile('</?\w+[^>]*>')#HTML标签
        re_comment=re.compile('<!--[^>]*-->')#HTML注释
        s=re_cdata.sub('',htmlstr)#去掉CDATA
        s=re_script.sub('',s) #去掉SCRIPT
        s=re_style.sub('',s)#去掉style
        s=re_br.sub('\n',s)#将br转换为换行
        # s=re_h.sub('',s) #去掉HTML 标签
        s=re_comment.sub('',s)#去掉HTML注释
        #去掉多余的空行
        blank_line=re.compile('\n+')
        s=blank_line.sub('\n',s)
        s=self.__replaceCharEntity(s)#替换实体
        return s

    def strip_tags(self, html):
        """
        Python中过滤HTML标签的函数
        >>> str_text=strip_tags("<font color=red>hello</font>")
        >>> print str_text
        hello
        """
        html = html.strip()
        html = html.strip("\n")
        result = []
        parser = HTMLParser()
        parser.handle_data = result.append
        parser.feed(html)
        parser.close()
        return ''.join(result)

    def extract(self, htmlstr):
        s = self.filter_tags(htmlstr)
        return self.strip_tags(s).replace('\n', ' ')
