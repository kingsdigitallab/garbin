import argparse
import re
import sys
import enchant
from tqdm import tqdm
import chardet
from pathlib import Path
import pandas as pd
import utils

VERSION = '0.2'


class Garbin:
    '''Data validation toolbox.
    To assess the quality of input material.'''

    def process_command_line(self):
        self.nltk_words = None

        self.parse_command_line()

        action_method = getattr(self, f'action_{self.action}', None)
        if action_method:
            res = action_method()
            if res:
                res_df = pd.DataFrame(res)
                res_format = self.args.format
                res_fmt = res_df
                if res_format == 'csv':
                    res_fmt = res_df.to_csv(index=False)
                if res_format == 'json':
                    res_fmt = res_df.to_json(orient='table', index=False)
                self.log(res_fmt, True)
        else:
            print('ERROR: Unrecognised action.\n')
            self.action_help()

    def action_test(self):
        '''Dummy action for testing purpose.'''
        self.log('test')
        return [{'k1': 'v1', 'k2': 'v2'}]

    def log(self, message, is_output=False):
        '''Log a unicode message to stderr (for info only).
        Or stdout (for results) if is_output is True.'''
        std_x = sys.stdout if is_output else sys.stderr
        print(message, file=std_x)

    def parse_command_line(self):
        self.parser = argparse.ArgumentParser(
            description=f'Data validator toolbox ({VERSION})',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self.get_actions_help()
        )
        self.parser.add_argument(
            'action',
            nargs=1,
            help=self.get_actions_help(True)
        )
        self.parser.add_argument(
            '-f', '--format', nargs='?',
            default='table',
            choices=['table', 'json', 'csv'],
            help='output format'
        )
        self.parser.add_argument(
            '-s', '--save',
            action='store_true',
            help='save intermediary outputs into data/out/ folder'
        )
        self.args = self.parser.parse_args()

        self.action = self.args.action[0]

    def action_help(self):
        '''Show help'''
        self.parser.print_help()

    def has_save(self):
        '''return True if intermediary outputs should be saved in data/out.
        Only if the user has specified --save flag.'''
        return self.args.save

    def get_actions_help(self, compact=False):
        ret = []
        for member in dir(Garbin):
            action = member.replace('action_', '')
            if action != member:
                action_desc = f'{action}'
                if not compact:
                    action_desc += ': ' + getattr(self, member).__doc__
                ret.append(action_desc)

        if compact:
            return ', '.join(ret)

        return '\nActions:\n  ' + '\n  '.join(ret)

    def action_legible(self):
        '''Check English legibility of documents in input folder.
        Returns a list of dictionary. One entry per file.
        Keys:
            file (PosixPath),
            legibility (from 0 to 1),
            extraction (e.g. tesseract)
        '''
        ret = []

        children = list(Path('data/in').iterdir())
        children = sorted(children, key=lambda c: c.name)

        for child in tqdm(children):
            if child.is_file():
                method_name = f'extract_' + child.suffix[1:]
                method = getattr(self, method_name, None)
                if method:
                    file_info = {
                        'file': child,
                    }
                    method(file_info)
                    self.compute_legibility(file_info)
                    # remove potentially long text from memory
                    if 'text' in file_info: del file_info['text']
                    ret.append(file_info)

        return ret

    def extract_txt(self, file_info):
        content = file_info['file'].read_bytes()
        encoding = chardet.detect(content)['encoding']
        file_info['extraction'] = encoding
        file_info['text'] = content.decode(encoding)

    def extract_pdf(self, file_info):
        file_info['extraction'] = 'tesseract'
        file_info['text'] = utils.extract_text_from_pdf(
            file_info['file'], True
        )
        if self.has_save():
            utils.write_file(
                f'data/out/{file_info["file"].name}.txt',
                file_info['text']
            )

    def compute_legibility(self, file_info):
        ret = 0.0

        correct, found = [0, 0]
        text = file_info.get('text', None)
        if text is not None:
            tokens = re.findall(r'[\w]+', text)
            for token in tokens:
                if len(token) > 1:
                    found += 1
                    token = token.lower()

                    if re.match(r'\d+', token):
                        # number
                        correct += 1
                    elif re.match(r'[A-Za-z][a-z]+', token):
                        correct += self.is_word(token)

        if found > 0:
            ret = correct / found

        file_info['legibility'] = int(ret*1000)/1000

    def is_word(self, token):
        if not hasattr(self, 'enchant_dict'):
            self.enchant_dict = enchant.Dict('en_US')

        edict = self.enchant_dict

        ret = edict.check(token.title())

        if not ret:
            # try f->s
            token = token.lower().replace('f', 's')
            ret = edict.check(token.title())

        # if not ret:
        #     print(token, edict.suggest(token))

        return ret

    def normalise_token(self, token):
        # f->s: Because Pennfyvlania, eftablifh
        return token.lower().replace('z', 's').replace('f', 's')


if __name__ == '__main__':
    garbin = Garbin()
    garbin.process_command_line()
