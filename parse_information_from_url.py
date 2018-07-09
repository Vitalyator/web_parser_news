import argparse
import os
import requests
import textwrap
from bs4 import BeautifulSoup

MAX_LENGTH_STRING = 80


class ProcessURL:
    def __init__(self, url, config, output_path):
        if not os.path.isdir(output_path):
            raise IOError('path %s is not exist' % output_path)
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        self.url = url
        self.output_path = output_path
        self.config = config
        self.processed_text = self._modificating_html(response.text, config)

    def _modificating_html(self, html, config):
        text = []
        soup = BeautifulSoup(html, 'html.parser')
        # title = soup.title.string
        parent_with_h1 = soup.find('h1').parent.parent
        print(parent_with_h1)
        for tags in parent_with_h1:
            print(parent_with_h1.contents)
            if tags.name != 'div':
                continue
            for content in tags.contents:
                if content.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'p']:
                    continue
                extracted_text = content.text
                if len(extracted_text) > MAX_LENGTH_STRING:
                    extracted_text = textwrap.fill(extracted_text, MAX_LENGTH_STRING)
                text.append(extracted_text)
        # print(text) принт отладки
        return text

    def save_text(self):
        #https://lenta.ru/news/2018/07/06/naftogaz_nadoel/
        url = self.url
        if url[-1] == '/':
            url = url[:-1]
        generating_directories = url.split('/')[2:]
        complete_output_path = os.path.join(self.output_path, *generating_directories[:-1])
        os.makedirs(complete_output_path, exist_ok=True)
        path_to_file = os.path.join(complete_output_path, generating_directories[-1] + '.txt')
        with open(path_to_file, 'w') as stream:
            for string in self.processed_text:
                stream.write(string)
                stream.write('\n\n')


def argument_parse():
    argument_parser = argparse.ArgumentParser(description='parse relevant information from URL site with filtering '
                                                          'commercial and navigates texts')
    argument_parser.add_argument('-u', '--url', type=str, help='URL from which information will be extracted')
    argument_parser.add_argument('-c', '--config', choices=['default', 'custom'], default='default',
                                 help='configurator filter information')
    argument_parser.add_argument('-o', '--output_path', type=str, help='path to save file .txt with filtered '
                                                                       'information from site')
    args = argument_parser.parse_args()
    return args


def main():
    args = argument_parse()
    filtered_information = ProcessURL(args.url, args.config, args.output_path)
    filtered_information.save_text()


if __name__ == '__main__':
    main()
