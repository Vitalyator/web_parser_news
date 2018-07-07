import argparse
import os
import requests
from bs4 import BeautifulSoup

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
        self.processed_text = self.modificating_html(response.text, config)

    def modificating_html(self, html, config):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string
        print(title)
        return html


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


if __name__ == '__main__':
    main()
