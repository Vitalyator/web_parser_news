import argparse
import os
import re
import requests
import textwrap
from bs4 import BeautifulSoup, element
from collections import Counter

MAX_LENGTH_STRING = 80


class ProcessURL:
    def __init__(self, url, output_path):
        if not os.path.isdir(output_path):
            raise IOError('path %s is not exist' % output_path)
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        self.html = response.text
        self.url = url
        self.output_path = output_path
        content_tag, title_text = self.search_tag_with_content()
        contents = self.parser_tag(content_tag)
        contents.insert(0, title_text)
        self.processed_text = contents

    @staticmethod
    def text_wrapping(text):
        if len(text) > MAX_LENGTH_STRING:
            text = textwrap.fill(text, MAX_LENGTH_STRING)
        return text

    def parser_tag(self, tag):
        buffer = ''
        text = []
        for content in tag.contents:
            text_content = content.string
            if content.name in ['div', 'img', 'figcaption', 'table'] or isinstance(content, element.Comment):
                continue
            if content.string is None:
                text.extend(self.parser_tag(content))
                continue

            extracted_text = str(text_content).replace(u'\xa0', u' ')

            if content.name == 'a':
                link = content.get('href')
                if link is not None and link.split("/")[0] != 'http:':
                    link = '/'.join(self.url.split('/')[0:3]) + link
                    extracted_text += '[' + link + ']'

            if content.name == 'p':
                text.append(self.text_wrapping(extracted_text))
                continue

            if '\n' in extracted_text:
                if len(buffer) != 0:
                    buffer = self.text_wrapping(buffer)
                    text.append(buffer)
                    buffer = ''
                if len(extracted_text) > 1:
                    extracted_text = extracted_text.strip('\r')
                    separated_extracted_text = extracted_text.split('\n')
                    for i, sub_text in enumerate(separated_extracted_text):
                        separated_extracted_text[i] = self.text_wrapping(sub_text)
                    while '' in separated_extracted_text:
                        separated_extracted_text.remove('')
                    text.extend(separated_extracted_text[:-1])
                    buffer = separated_extracted_text[-1]
            else:
                extracted_text = extracted_text.strip()
                if len(buffer) == 0 or len(extracted_text) == 1:
                    buffer += extracted_text
                    continue
                buffer = ' '.join([buffer, extracted_text])
        text.append(self.text_wrapping(buffer))
        while '' in text:
            text.remove('')
        return text

    def search_tag_with_content(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        h1_tag = soup.find('h1')
        title_text = self.text_wrapping(h1_tag.text.strip('\n\t '))

        for sibling_tag in h1_tag.next_siblings:
            if 'p' == sibling_tag.name:
                return sibling_tag, title_text

        p_tags = soup.find_all('p')
        for p in p_tags[:]:
            actual_content = []
            for title_words in title_text[0].split():
                actual_content += p.find_all(string=re.compile(title_words))
            if len(actual_content) == 0:
                p_tags.remove(p)
                
        if len(p_tags) == 0:
            for title_words in title_text[0].split():
                p_tags += soup.find_all(string=re.compile(title_words))
        counter = Counter()
        for tag in p_tags:
                counter[tag.parent] += 1
            
        content_tag, _ = counter.most_common(1)[0]
        return content_tag, title_text

    def save_text(self):
        url = self.url
        if url[-1] == '/':
            url = url[:-1]
        generating_directories = url.split('/')[2:]
        complete_output_path = os.path.join(self.output_path, *generating_directories[:-1])
        os.makedirs(complete_output_path, exist_ok=True)
        path_to_file = os.path.join(complete_output_path, generating_directories[-1] + '.txt')
        with open(path_to_file, 'w', encoding='utf-8') as stream:
            for string in self.processed_text:
                stream.write(string + '\n\n')


def argument_parse():
    argument_parser = argparse.ArgumentParser(description='parse relevant information from URL site with filtering '
                                                          'commercial and navigates texts')
    argument_parser.add_argument('-u', '--url', type=str, help='URL from which information will be extracted')
    argument_parser.add_argument('-o', '--output_path', type=str, help='path to save file .txt with filtered '
                                                                       'information from site')
    args = argument_parser.parse_args()
    return args


def main():
    args = argument_parse()
    filtered_information = ProcessURL(args.url, args.output_path)
    filtered_information.save_text()


if __name__ == '__main__':
    main()
