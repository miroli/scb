# -*- coding: utf-8 -*-
import requests
import json
import pprint
import textwrap
from colorama import Fore, init

init(autoreset=True)


class SCB:
    BASE_URL = 'http://api.scb.se/OV0104/v1/doris/sv/ssd/'
    pwd = BASE_URL

    def get_overview(self):
        r = requests.get(self.BASE_URL)
        subjects = json.loads(r.text)

        self.print_contents(subjects)

    def select(self, id):
        new_pwd = self.pwd + id
        self.request_page(new_pwd)

    def select_table(self, id):
        new_pwd = self.pwd + id
        r = requests.get(new_pwd)

        table = json.loads(r.text)

        print table['title']

        for variable in table['variables']:
            print variable['code'] + ' (' + variable['text'] + ')'
            print str(len(variable['values'])) + ' värden att välja mellan\n'

        headers = {'content-type': 'text/csv', 'accept': 'text/csv'}
        data = {'query': []}

        # Ask the user for filters
        for variable in table['variables']:
            print variable['code'] + ': '
            for value in variable['values']:
                print value,
            answer = raw_input('\nValj ' + variable['code'] + ': ')

            # Construct the query
            data['query'].append({'code': variable['code'], 'selection': {'filter': 'item', 'values': [answer]}})

        data['response'] = {'format': 'csv'}

        r = requests.post(new_pwd, data=json.dumps(data), headers=headers)
        print r.text


    def back(self):
        new_pwd = self.pwd.rstrip('/').rsplit('/', 1)[0]
        self.request_page(new_pwd)

    def request_page(self, url):
        r = requests.get(url)
        self.pwd = url + '/'
        subjects = json.loads(r.text)

        response_type = subjects[0]['type']

        # Have we reached the tables yet?
        if response_type == 'l':
            self.print_contents(subjects)
        elif response_type == 't':
            self.print_tables(subjects)

    def print_contents(self, seq):
        '''
        Prints out a list of categories above table level
        '''
        id_len = len(seq[0]['id'])
        indent = ' ' * (id_len + 2)

        print ''
        print Fore.GREEN + 'ID' + indent + 'Titel'
        print Fore.GREEN + '--' + indent + '------'

        for subject in seq:
            id = subject['id']
            text = subject['text']
            print Fore.RED + id + textwrap.fill(text, initial_indent=' '*4, subsequent_indent=' '*len(id + ' '*4))
        print ''

    def print_tables(self, seq):
        '''
        Prints out a list of tables within a category
        '''
        print Fore.GREEN + '\nTABELLER'
        for table in seq:
            indent = ' '*len('Uppdaterad:') + ' '*4
            tabell_indent = ' ' * (len(indent) - len('Tabell:'))
            uppdaterad_indent = ' ' * 4
            id_indent = ' ' * (len(indent) - len('ID:'))

            print 'Tabell:' + textwrap.fill(table['text'], initial_indent=tabell_indent, subsequent_indent=indent)
            print 'Uppdaterad:' + textwrap.fill(table['updated'], initial_indent=uppdaterad_indent)
            print 'ID:' + textwrap.fill(table['id'], initial_indent=id_indent, subsequent_indent=id_indent)
            print ''

if __name__ == '__main__':
    print 'working'
