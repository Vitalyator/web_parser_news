import argparse
import os
import re
import requests
import textwrap
from bs4 import BeautifulSoup
from collections import Counter

MAX_LENGTH_STRING = 80


class ProcessURL:
    def __init__(self, url, output_path):
        if not os.path.isdir(output_path):
            raise IOError('path %s is not exist' % output_path)
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        self.url = url
        self.output_path = output_path
        self.processed_text = self._modificating_html(response.text)

    def _modificating_html(self, html):

        def text_wrapping(text):
            if len(text) > MAX_LENGTH_STRING:
                text = textwrap.fill(text, MAX_LENGTH_STRING)
            return text

        def scan_tag(tag_):
            text_ = []
            for child in tag_.children:
                if child.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'lo']:
                    continue
                content_text_ = child.text
                if content_text_ == '':
                    continue
                content_text_ = content_text_.strip()
                text_.append(text_wrapping(content_text_))
            return text_

        def text_editor(content_tag):
            buffer = ''
            text = []
            for content in content_tag.contents:
                text_content = content.string
                if content.string is None:
                    if content.text is not None:
                        text_content = content.text
                    else:
                        continue
                extracted_text = str(text_content).replace(u'\xa0', u' ')
                if '\n' in extracted_text:
                    if len(buffer) != 0:
                        buffer = text_wrapping(buffer)
                        text.append(buffer)
                        buffer = ''
                    if len(extracted_text) > 1:
                        extracted_text = extracted_text.strip('\r')
                        separated_extracted_text = extracted_text.split('\n')
                        for i, sub_text in enumerate(separated_extracted_text):
                            separated_extracted_text[i] = text_wrapping(sub_text)
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
            return text

        text = []
        soup = BeautifulSoup(html, 'html.parser')
        h1_tag = soup.find('h1')
        text.append(text_wrapping(h1_tag.text.strip('\n\t ')))
        for sibling_tag in h1_tag.next_siblings:
            if 'p' == sibling_tag.name:
                text = (scan_tag(h1_tag.parent))
                return text
        parent_content = soup.find_all('p')
        if len(parent_content) != 0:
            counter = Counter()
            for tag in parent_content:
                counter[tag.parent] += 1
            content_tag, _ = counter.most_common(1)[0]
            text.extend(scan_tag(content_tag))
        else:
            for title_words in text[0].split():
                parent_content += soup.find_all(string=re.compile(title_words))
            counter = Counter()
            for tag in parent_content:
                counter[tag.parent] += 1
            content_tag, count = counter.most_common(1)[0]
            text.extend(text_editor(content_tag))
        print(text)
        return text

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
