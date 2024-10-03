# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 14:01:11 2023

@author: dnelson
"""

import re
from datetime import datetime
from edtf_validate.valid_edtf import is_valid
import csv
import pandas as pd
import numpy as np
import os
import validators


# silence warnings about writing to a copy
pd.options.mode.chained_assignment = None



def clean_up_commas(cell):
    '''
    Take delimiter commas and replace them with pipes.
    Take escaped commas and replace them with regular commas.
    '''
    cell = re.sub(r'([^\\]),', r'\1|', cell)
    cell = cell.replace('\,', ',')
    return cell


def add_relators(relator, cell):
    new_cell = []
    if cell != '':
        cells = cell.split('|')
        for i in cells:
            new_data = f'{relator}:{i}'
            new_cell.append(new_data)
    return '|'.join(new_cell)
    

def add_two_relators(relators, cell):
    new_cell = []
    if cell != '':
        cells = cell.split('|')
        for i in relators:
            for j in cells:
                new_data = add_relators(i, j)
                new_cell.append(new_data)
    return '|'.join(new_cell)


def add_subjects(subject, cell):
    new_cell = []
    if cell != '':
        cells = cell.split('|')
        for i in cells:
            new_data = f'{subject}:{i}'
            new_cell.append(new_data)
    return '|'.join(new_cell)

def replace_curly_quotes(cell):
    cell = cell.replace('“', '"')
    cell = cell.replace('”', '"')
    return cell
    
def process_lang_abbr(cell):
   new_cell = []
   if cell != '':
       cells = cell.split('|')
       for i in cells:
           new_data = f'({i})'
           new_cell.append(new_data)
   return '|'.join(new_cell)


def process_dates(cell):
    # variables
    mdy = re.compile('(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2},\s+\d{4}')
    ymd = re.compile('\d{4}\s(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}')
    ymd_comma = re.compile('\d{4},\s(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}')
    ym = re.compile('\d{4}\s(January|February|March|April|May|June|July|August|September|October|November|December)')
    ym_comma = re.compile('\d{4},\s(January|February|March|April|May|June|July|August|September|October|November|December)')
    my = re.compile('(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}')
    # fix year ranges
    if re.match('([0-9][0-9][0-9][0-9])-([0-9][0-9][0-9][0-9])', cell):
        cell = re.sub(r'([0-9][0-9][0-9][0-9])-([0-9][0-9][0-9][0-9])', r'\1/\2', cell)
        return cell
    # fix months and days without leading zeros
    elif re.match('([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9])$', cell):
        cell = re.sub('([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9])', r'\1-\2-0\3', cell)
        return cell
    elif re.match('([0-9][0-9][0-9][0-9])-([0-9])-([0-9])([0-9])', cell):
        cell = re.sub('([0-9][0-9][0-9][0-9])-([0-9])-([0-9][0-9])', r'\1-0\2-\3', cell)
        return cell
    # fix items with written months
    elif re.match(mdy, cell):
        try:
            date = datetime.strptime(cell, '%B %d, %Y')
            return date.strftime('%Y-%m-%d')
        except ValueError:
            return cell
    elif re.match(ymd, cell):
        try:
            date = datetime.strptime(cell, '%Y %B %d')
            return date.strftime('%Y-%m-%d')
        except ValueError:
            return cell
    elif re.match(ymd_comma, cell):
        date = datetime.strptime(cell, '%Y, %B %d')
        return date.strftime('%Y-%m-%d')
    elif re.match(ym, cell):
        try:
            date = datetime.strptime(cell, '%Y %B')
            return date.strftime('%Y-%m')
        except ValueError:
            return cell
    elif re.match(ym_comma, cell):
        try:
            date = datetime.strptime(cell, '%Y, %B')
            return date.strftime('%Y-%m')
        except ValueError:
            return cell
    elif re.match(my, cell):
        date = datetime.strptime(cell, '%B %Y')
        return date.strftime('%Y-%m')
    elif re.match('\[\d{4}\]', cell):
        date = cell.replace('[', '')
        return date.replace(']', '?')
    elif re.match('\d{4}-\[\d{2}\]', cell):
        date = cell.replace('[', '?')
        return date.replace(']', '')
    elif re.match('\d{4}-\d{2}-\[\d{2}\]', cell):
        date = cell.replace('[', '?')
        return date.replace(']', '')
    else:
        return cell


def validate_date(cell):
    valid = is_valid(cell)
    return valid


def validate_url(cell):
    valid = validators.url(cell)
    if valid is True:
        return cell
    else:
        return f'@{cell}'


relators = {
    'mods_name_corporate_printer_namePart_ms': 'relators:prt:corporate_body',
    'mods_name_collector_namePart_ms': 'relators:col:person',
    'mods_name_corporate_participant_namePart_ms': 'local:par:corporate_body',
    'mods_name_personal_interviewer_namePart_ms': 'relators:ivr:person',
    'mods_name_personal_c_namePart_ms': 'relators:cre:person',
    'mods_name_consultant_namePart_ms': 'relators:csl:person',
    'mods_name_personal_grantee_namePart_ms': 'local:grn:person',
    'mods_name_personal_singer_namePart_ms': 'relators:sng:person',
    'mods_name_corporate_creator_namePart_ms': 'relators:cre:corporate_body',
    'mods_name_personal_speaker_namePart_ms': 'relators:spk:person',
    'mods_name_corporate_depositor_namePart_ms': 'relators:dpt:corporate_body',
    'mods_name_personal_researcher_namePart_ms': 'relators:res:person',
    'mods_name_personal_uploader_namePart_ms': 'local:upl:person',
    'mods_name_corporate_transcriber_namePart_ms': 'relators:trc:corporate_body',
    'mods_name_personal_illustrator_namePart_ms': 'relators:ill:person',
    'mods_name_corporate_interpreter_namePart_ms': 'local:ipt:corporate_body',
    'mods_name_corporate_moderator_namePart_ms': 'relators:mod:corporate_body',
    'mods_name_personal_correspondent_namePart_ms': 'relators:crp:person',
    'mods_name_personal_compiler_namePart_ms': 'relators:com:person',
    'mods_name_personal_grantor_namePart_ms': 'local:gro:person',
    'mods_name_author_namePart_ms': 'relators:aut:person',
    'mods_name_corporate_researcher_namePart_ms': 'relators:res:corporate_body',
    'mods_name_personal_artist_namePart_ms': 'relators:art:person',
    'mods_name_corporate_singer_namePart_ms': 'relators:sng:corporate_body',
    'mods_name_corporate_interviewer_namePart_ms': 'relators:ivr:corporate_body',
    'mods_name_corporate_recipient_namePart_ms': 'relators:rcp:corporate_body',
    'mods_name_corporate_performer_namePart_ms': 'relators:prf:corporate_body',
    'mods_name_corporate_recorder_namePart_ms': 'relators:rcd:corporate_body',
    'mods_name_personal_consultnat_namePart_ms': 'relators:csl:corporate_body',
    'mods_name_personal_composer_namePart_ms': 'relators:cmp:person',
    'mods_name_personal_collector_namePart_ms': 'relators:col:person',
    'mods_name_corporate_developer_namePart_ms': 'local:dev:corporate_body',
    'mods_name_personal_depicted_namePart_ms': 'relators:dpc:person',
    'mods_name_personal_printmaker_namePart_ms': 'relators:prm:person',
    'mods_name_personal_printer_namePart_ms': 'relators:prt:person',
    'mods_name_personal_participant_namePart_ms': 'local:par:person',
    'mods_name_family_creator_namePart_ms': 'relators:cre:family',
    'mods_name_personal_annotator_namePart_ms': 'relators:ann:person',
    'mods_name_corporate_author_namePart_ms': 'relators:aut:corporate_body',
    'mods_name_contributor_namePart_ms': 'relators:ctb:person',
    'mods_name_personal_recipient_namePart_ms': 'relators:rcp:person',
    'mods_name_personal_performer_namePart_ms': 'relators:prf:person',
    'mods_name__cartographer_namePart_ms': 'relators:ctg:person',
    'mods_name_personal_consultant_namePart_ms': 'relators:csl:person',
    'mods_name_corporate_publisher_namePart_ms': 'relators:pbl:corporate_body',
    'mods_name_recorder_namePart_ms': 'relators:rcd:person',
    'mods_name_personal_creator_namePart_ms': 'relators:cre:person',
    'mods_name_personal_seller_namePart_ms': 'relators:sll:person',
    'mods_name_personal_buyer_namePart_ms': 'local:buy:person',
    'mods_name_personal_contributor_namePart_ms': 'relators:ctb:person',
    'mods_name_personal_publisher_namePart_ms': 'relators:pbl:person',
    'mods_name_personal_producer_namePart_ms': 'relators:rpc:person',
    'mods_name_personal_originator_namePart_ms': 'relators:org:person',
    'mods_name_personal_surveyor_namePart_ms': 'relators:srv:person',
    'mods_name_personal_data_contributor_namePart_ms': 'relators:dtc:person',
    'mods_name_corporate_consultant_namePart_ms': 'relators:csl:corporate_body',
    'mods_name_personal_source_namePart_ms': 'local:src:person',
    'mods_name_personal_photographer_namePart_ms': 'relators:pht:person',
    'mods_name_corporate_translator_namePart_ms': 'relators:trl:corporate_body',
    'mods_name_creator_namePart_ms': 'relators:cre:person',
    'mods_name_personal_cartographer_namePart_ms': 'relators:ctg:person',
    'mods_name_personal_translator_namePart_ms': 'relators:trl:person',
    'mods_name_personal_spaker_namePart_ms': 'relators:spk:person',
    'mods_name_personal_depositor_namePart_ms': 'relators:dpt:person',
    'mods_name_corporate_responder_namePart_ms': 'relators:rsp:corporate_body',
    'mods_name_corporate_contributor_namePart_ms': 'relators:ctb:corporate_body',
    'mods_name_corporate_speaker_namePart_ms': 'relators:spk:person',
    'mods_name_personal_contributer_namePart_ms': 'relators:ctb:person',
    'mods_name_corporate_collector_namePart_ms': 'relators:col:corporate_body',
    'mods_name_corporate_speaker_affiliation_ms': 'local:aff:corporate_body',
    'mods_name_personal_interpreter_namePart_ms': 'local:ipt:person',
    'mods_name_personal_author_namePart_ms': 'relators:aut:person',
    'mods_name_personal_engraver_namePart_ms': 'relators:egr:person',
    'mods_name_personal_creater_namePart_ms': 'relators:cre:person',
    'mods_name_personal_recorder_namePart_ms': 'relators:rcd:person',
    'mods_name_researcher_namePart_ms': 'relators:res:person',
    'mods_name_personal_transcriber_namePart_ms': 'relators:trc:person'            
    }

two_relators = {
    'mods_name_personal_researcher_role_ms': ('relators:col:person',
                                              'relators:res:person'),
    'mods_name_personal_contributor_compiler_namePart_ms': ('relators:com:person',
                                                            'relators:ctb:person'),
    'mods_name_corporate_stationer_and_printer_namePart_ms': ('relators:prt:corporate_body',
                                                              'local:sta:corporate_body')
    }

subjects = {
    'mods_subject_name_family_namePart_ms': 'family',
    'mods_subject_name_corporate_namePart_ms': 'corporate_body',
    'mods_subject_name_personal_namePart_ms': 'person'}

subject_headers = [s for s in subjects.keys()]

all_linked_agents = [a for a in relators.keys()] + [r for r in two_relators.keys()]

models = {
    'bookCModel': 'Paged Content',
    'collectionCModel': 'Collection',
    'pageCModel': 'Page',
    'sp_large_image_cmodel': 'Image',
    'compoundCModel': 'Compound Object',
    'sp_videoCModel': 'Video',
    'sp_pdf': 'Digital Document',
    'sp_strict_pdf': 'Digital Document', # double check with Bayard and Sabrina
    'manuscriptCModel': 'Manuscript', # what to do
    'manuscriptPageCModel': 'Page', # what to do
    'sp-audioCModel': 'Audio',
    'binaryObjectCModel': 'Binary'
    }

resource_types = {
    'Paged Content': 'Collection',
    'Collection': 'Collection',
    'Page': 'Text',
    'Image': 'Still Image',
    'Compound Object': 'Collection',
    'Video': 'Moving Image',
    'Digital Document': 'Text',
    'Manuscript': 'Collection',
    'Manuscript Page': 'Text',
    'Audio': 'Sound',
    'Binary': 'Text'}

display_hint = {
    'Image': 'Open Seadragon',
    'Page': 'Open Seadragon',
    'Digital Document': 'PDFjs'}

bad_batches = ['batch-8.csv',
               'batch-9.csv',
               'batch-10.csv',
               'batch-11.csv',
               'batch-12.csv',
               'batch-14.csv']

base_path = 'P:/Center for Digital Scholarship/diglib-migration-scripts/data/batches'
out_path = 'P:/Center for Digital Scholarship/diglib-migration-scripts/data/output.csv'
multiples_path = 'P:/Center for Digital Scholarship/diglib-migration-scripts/data/parents'
output_dir = 'P:/Center for Digital Scholarship/diglib-migration-scripts/data/cleaned'

raw_csvs = os.listdir(base_path)

# get dict of parent pids and titles in batches 7 and 13
parent_pids = {}
with open('P:/Center for Digital Scholarship/diglib-migration-scripts/data/parent-pids.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        parent_pids.update({row[0]: row[1]})

parent_pid_titles = {}
with open('P:/Center for Digital Scholarship/diglib-migration-scripts/data/parent-pids-titles.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        parent_pid_titles.update({row[0]: row[1]})
        
for file in raw_csvs:
    full_path = os.path.join(base_path, file)

    with open(full_path, 'r', newline='', encoding='utf-8') as in_file, open(out_path, 'w', newline='', encoding='utf-8') as out_file:
        reader = csv.DictReader(in_file)
        header = reader.fieldnames
        writer = csv.writer(out_file)
        writer.writerow(header)
    
        for row in reader:
            output = []
            for key, value in row.items():
                # clean commas for all cells
                cell = clean_up_commas(value)
                # clean description/abstract
                if key == 'mods_abstract_ms':
                    cell = replace_curly_quotes(cell)
                    output.append(cell)
                # language abbreviations
                elif key == 'mods_language_languageTerm_code_ms':
                    cell = process_lang_abbr(cell)
                    output.append(cell)
                # basic EDTF date conversion
                elif key == 'mods_originInfo_dateIssued_ss' or key == 'mods_originInfo_dateCreated_ss':
                    cell = process_dates(value)
                    output.append(cell)
                elif key in relators.keys():
                    cell = add_relators(relators[key], cell)
                    output.append(cell)
                elif key in two_relators.keys():
                    cell = add_two_relators(two_relators[key], cell)
                    output.append(cell)
                elif key in subjects.keys():
                    cell = add_subjects(subjects[key], cell)
                    output.append(cell)
                else:
                    output.append(cell)
            writer.writerow(output)

    print(f'Stage one of cleaning completed for {file}.')

    # now we read to pandas to combine and reorder columns
    df = pd.read_csv(out_path,
                     dtype={'RELS_EXT_isSequenceNumber_literal_ms': str,
                            'program_number': str,
                            'recording_number': str,
                            'mods_originInfo_dateModified_ss': str,
                            'mods_originInfo_dateCaptured_ss': str,
                            'mods_originInfo_dateCreated_ss': str,
                            'mods_language_languageTerm_text_ms': str,
                            'mods_language_languageTerm_code_ms': str},
                     low_memory=False)
    # populate ID field
    df['id'] = df['PID']
    # populate weight field
    df['weight'] = df['RELS_EXT_isSequenceNumber_literal_ms']
    # populate linked agent field
    relator_cols = df[all_linked_agents]
    relator_cols.dropna(how='all', axis=1, inplace=True)
    df['people'] = relator_cols.apply(lambda x: '|'.join(x.dropna()), axis=1)
    # handle subjects
    subject_cols = df[subject_headers]
    subject_cols.dropna(how='all', axis=1, inplace=True)
    df['mods_subject_name_personal_namePart_ms'] = subject_cols.apply(lambda x: '|'.join(x.dropna()), axis=1)

    # handle parents
    parents = df[['RELS_EXT_isMemberOfCollection_uri_ms',
                  'RELS_EXT_isConstituentOf_uri_ms',
                  'RELS_EXT_isPageOf_uri_ms']]
    df['parent'] = parents.apply(lambda x: '|'.join(x.dropna()), axis=1)
    # delete extraneous url string to just get PID
    df['parent'] = df['parent'].str.replace('info:fedora/', '')
    # now, just take the first parent for multiples and pipe the rest to a
    # separate CSV
    parents_list = df['parent'].to_list()
    pids = df['PID'].to_list()

    parents_keep = []
    member_of = []
    parents_path = os.path.join(multiples_path, file)
    with open(parents_path, 'w', newline='', encoding='utf-8') as parent_file:
        parent_writer = csv.writer(parent_file)
        parent_writer.writerow(['pid', 'parents'])
        for i, j in zip(parents_list, pids):
            if file in bad_batches:
                if '|' in i:
                    all_parents = i.split('|')
                    if any(e in all_parents for e in parent_pids.keys()) is True:
                        common = set(parent_pids.keys()).intersection(all_parents)
                        try:
                            len(common) == 1
                        except Exception:
                            print('More than one common pid')
                            raise
                        all_parents.remove(list(common)[0])
                        member_of.append(list(common)[0])
                        parents_keep.append(all_parents[0])
                        if len(all_parents) > 1:
                            parent_writer.writerow([j, '|'.join(all_parents[1:])])
                    else:
                        parents_keep.append(all_parents[0])
                        parent_writer.writerow([j, '|'.join(all_parents[1:])])
                        member_of.append('')
                else:
                    if i in parent_pids.keys():
                        member_of.append(i)
                        parents_keep.append('')
                    else:
                        parents_keep.append(i)
                        member_of.append('')
            else:
                if '|' in i:
                    all_parents = i.split('|')
                    parents_keep.append(all_parents[0])
                    parent_writer.writerow([j, '|'.join(all_parents[1:])])
                else:
                    parents_keep.append(i)

    df['parent'] = parents_keep
    df['parent'] = df['parent'].str.replace('islandora:text_collection', '')
    if file in bad_batches:
        try:
            df['member_of'].isnull().all() is True    
            df['member_of'] = member_of
        except Exception:
            print('Member Of Exception triggered')
            raise

    # Recording numbers
    rec_numbers = df['dc.identifier'].str.contains('Recording Number', na=False)
    numbers = df[rec_numbers]['dc.identifier'].to_list()
    rec = []
    for n in numbers:
        items = n.split('|')
        for i in items:
            if 'Recording Number' in i:
                rec_number = i.replace('Recording Number: ', '')
                rec.append(rec_number)
    df.loc[rec_numbers, ['recording_number']] = rec
    # Program numbers
    program_numbers = df['dc.identifier'].str.contains('Program Number', na=False)
    numbers = df[program_numbers]['dc.identifier'].to_list()
    program = []
    for n in numbers:
        items = n.split('|')
        for i in items:
            if 'Program Number' in i:
                program_number = i.replace('Program Number: ', '')
                program.append(program_number)
    df.loc[program_numbers, ['program_number']] = program

    # now, legacy ids

    df['dc.identifier'] = df['dc.identifier'].fillna('')
    numbers = df['dc.identifier'].to_list()
    pid_reg = re.compile('(graphics|audio|text|video|compound|revcity|apsrevcity|hsprevcity|lcprevcity|pdf|flatPaperReports|flatPaperImages|conservation|bookTreatmentReports|islandora):.+')
    legacy_ids = []
    for n in numbers:
        items = n.split('|')
        local_ids = []
        for i in items:
            if 'Recording Number' not in i:
                if 'Program Number' not in i:
                    if re.match(pid_reg, i) is None:
                        local_ids.append(i.replace('local: ', ''))
        if len(local_ids) == 0:
            local_ids.append('')
        legacy_ids.append('|'.join(local_ids))

    df['dummy_legacy'] = legacy_ids
    df['mods_identifier_local_ms'] = df[['mods_identifier_local_ms', 'dummy_legacy']].apply(lambda x: '|'.join(x.dropna()), axis=1)
    df.drop(['dummy_legacy'], axis=1, inplace=True)

    legacy_cleaning = df['mods_identifier_local_ms'].to_list()

    final_legacy = []
    for i in legacy_cleaning:
        local_ids = set(i.split('|'))
        local_ids = list(filter(None, local_ids))
        final_legacy.append('|'.join(local_ids))

    df['mods_identifier_local_ms'] = final_legacy
    
    # create titles for columns without them
    # select all empty rows
    if file in bad_batches:
        title = df[df['mods_titleInfo_title_ms'].isna()]
        title['parents_to_use'] = title['parent']
        title['parents_to_use'].replace('', np.nan, inplace=True)
        title['parents_to_use'] = title['parents_to_use'].fillna(title['member_of'])
        title['mods_titleInfo_title_ms'] = title['parents_to_use'].map(parent_pid_titles)
        title.drop(['parents_to_use'], axis=1, inplace=True)
        title['mods_titleInfo_title_ms'] = title[['mods_titleInfo_title_ms', 'weight']].apply(lambda x: ' , Page '.join(x.dropna()), axis=1)
        # reintegrate data
        df.update(title)
        # compare related materials, fill empty data
        # fill na because NaN != NaN
        df[['mods_relatedItem_titleInfo_title_ms', 'mods_relatedItem_displayLabel_parentCollection_ms']] = df[['mods_relatedItem_titleInfo_title_ms', 'mods_relatedItem_displayLabel_parentCollection_ms']].fillna('')
        df['compare'] = (df['mods_relatedItem_titleInfo_title_ms'] == df['mods_relatedItem_displayLabel_parentCollection_ms'])
        related_mat = df.loc[df['compare'] == False]
        # first, blank collections get populated
        subset_related = related_mat.loc[related_mat['mods_relatedItem_displayLabel_parentCollection_ms'] == '']
        subset_related['mods_relatedItem_displayLabel_parentCollection_ms'] = subset_related['mods_relatedItem_titleInfo_title_ms']
        # reintegrate data
        related_mat.update(subset_related)
        df.update(related_mat)
    else:
        title = df[df['mods_titleInfo_title_ms'].isna()]
        # get just parents
        title_parents = set(title['parent'].to_list())
        # look up PIDs, write PIDs and titles to dict for quick lookup
        titles_to_use = df[df['PID'].isin(title_parents)]
        titles_to_use.dropna(subset=['mods_titleInfo_title_ms'], inplace=True)
        titles_dict = pd.Series(titles_to_use['mods_titleInfo_title_ms'].values, index=titles_to_use['PID']).to_dict()
        title['mods_titleInfo_title_ms'] = title['parent'].map(titles_dict)
        title['mods_titleInfo_title_ms'] = title[['mods_titleInfo_title_ms', 'weight']].apply(lambda x: ' , Page '.join(x.dropna()), axis=1)
        # reintegrate data
        df.update(title)
        # compare related materials, fill empty data
        # fill na because NaN != NaN
        df[['mods_relatedItem_titleInfo_title_ms', 'mods_relatedItem_displayLabel_parentCollection_ms']] = df[['mods_relatedItem_titleInfo_title_ms', 'mods_relatedItem_displayLabel_parentCollection_ms']].fillna('')
        df['compare'] = (df['mods_relatedItem_titleInfo_title_ms'] == df['mods_relatedItem_displayLabel_parentCollection_ms'])
        related_mat = df.loc[df['compare'] == False]
        # first, blank collections get populated
        subset_related = related_mat.loc[related_mat['mods_relatedItem_displayLabel_parentCollection_ms'] == '']
        subset_related['mods_relatedItem_displayLabel_parentCollection_ms'] = subset_related['mods_relatedItem_titleInfo_title_ms']
        # reintegrate data
        related_mat.update(subset_related)
        df.update(related_mat)

    # drop things that now match
    df['compare'] = (df['mods_relatedItem_titleInfo_title_ms'] == df['mods_relatedItem_displayLabel_parentCollection_ms'])
    related_mat = df.loc[df['compare'] == False]
    # write to related materials column
    related_mat['related_materials'] = related_mat['mods_relatedItem_titleInfo_title_ms']
    df.update(related_mat)

    #delete comparison column
    df.drop(['compare'], axis=1, inplace=True)

    # now handle genres
    olac = df.dropna(subset=['mods_genre_displayLabel_ms'])
    olac_field = olac['mods_genre_displayLabel_ms'].to_list()
    olac['mods_genre_ms'] = olac['mods_genre_ms'].fillna('')
    olac_content = olac['mods_genre_ms'].to_list()

    discourse_type = []
    linguistic_type = []
    for f, c in zip(olac_field, olac_content):
        write_to_discourse = []
        write_to_linguistic = []
        fields = f.split('|')
        olac_types = c.split('|')
        if len(fields) == len(olac_types):
            for i, j in zip(fields, olac_types):
                if i =='OLAC Discourse Type':
                    write_to_discourse.append(j)
                elif i == 'OLAC Linguistic Type':
                    write_to_linguistic.append(j)
                else:
                    write_to_discourse.append('@Bad data in OLAC column. Manual review.')
            discourse_type.append('|'.join(write_to_discourse))
            linguistic_type.append('|'.join(write_to_linguistic))
        else:
            discourse_type.append('@Data does not match. Manual review')
            linguistic_type.append('')

    olac['olac_discourse_type'] = discourse_type
    olac['olac_linguistic_type'] = linguistic_type

    df.update(olac)

    genres = df[df['mods_genre_displayLabel_ms'].isna()]

    genres['genre'] = genres['mods_genre_ms']
    df.update(genres)

    # handle empty call numbers
    df['mods_relatedItem_displayLabel_parentCollectionIdentifier_ms'].fillna(df['mods_relatedItem_identifier_ms'], inplace=True)

    # handle language data
    # first, expand both into lists
    df['mods_language_languageTerm_text_ms'] = df['mods_language_languageTerm_text_ms'].str.split('|', expand=False)
    df['mods_language_languageTerm_code_ms'] = df['mods_language_languageTerm_code_ms'].str.split('|', expand=False)

    lang = df['mods_language_languageTerm_text_ms'].to_list()
    lang_co = df['mods_language_languageTerm_code_ms'].to_list()

    lang_list = []
    for lg, code in zip(lang, lang_co):
        if pd.isna(lg) is True and pd.isna(code) is True:
            lang_list.append('')
        else:
            try:
                new_lang = '|'.join([a + ' ' + b for a, b in zip(lg, code)])
                lang_list.append(new_lang)
            except TypeError:
                if pd.isna(lg) is True:
                    lang_list.append(f'@{code}')
                elif pd.isna(code) is True:
                    lang_list.append(f'@{lg}')
                else:
                    lang_list.append('Bad data. See original sheet.')
                    print('Bad language data detected.')

    df['mods_language_languageTerm_text_ms'] = lang_list

    # handle file URLs
    # first, add file URLs for files that habe OBJ
    obj_url = df.dropna(subset=['fedora_datastream_info_OBJ_ID_ms'])
    obj_url['file'] = obj_url.apply(lambda x: '/mnt/legacy-data/media/batch' + file.replace('batch-', '').replace('.csv', '') + '/' + x['PID'].replace(':', '_') +'_OBJ.tiff', axis=1)
    df.update(obj_url)

    # now add URLs for files with JP2 but no OBJ
    jp2_url = df.dropna(subset=['fedora_datastream_info_JP2_ID_ms'])
    jp2_url = jp2_url[jp2_url['fedora_datastream_info_OBJ_ID_ms'].isna()]
    if jp2_url.empty is False:
        jp2_url['file'] = jp2_url.apply(lambda x: '/mnt/legacy-data/media/batch' + file.replace('batch-', '').replace('.csv', '') + '/' + x['PID'].replace(':', '_') + '_JP2.jp2', axis=1)
        df.update(jp2_url)

    # now add TEI - untested code, but should be the same as other datastreams
    tei_url = df.dropna(subset=['fedora_datastream_info_TEI_ID_ms'])
    if tei_url.empty is False:
        tei_url['tei'] = tei_url.apply(lambda x: '/mnt/legacy-data/media/batch' + file.replace('batch-', '').replace('.csv', '') + '/' + x['PID'].replace(':', '_') + '_TEI.xml', axis=1)
        df.update(tei_url)
    
    # populate file alias column
    df['alias'] = df.apply(lambda x: '/islandora/object/' + x['PID'], axis=1)

    # now work on models
    df['legacy_model'] = df['RELS_EXT_hasModel_uri_s'].str.replace('info:fedora/islandora:', '')
    df['model'] = df['legacy_model'].map(models)
    df.drop(['legacy_model'], axis=1, inplace=True)

    # now map resource types
    df['resource_type'] = df['model'].map(resource_types)

    # access control
    restricted = df.dropna(subset=['RELS_INT_isViewableByUser_literal_ms'])
    restricted['access_control'] = 'Restricted Audio'
    df.update(restricted)

    # doing the same thing twice, but we aren't sure if all restricted items
    # will have data in both categories
    restricted = df.dropna(subset=['RELS_INT_isViewableByRole_literal_ms'])
    restricted['access_control'] = 'Restricted Audio'
    df.update(restricted)


    # add display hints
    df['display_hint'] = df['model'].map(display_hint)

    # dates - whoo, boy...

    # first, date issued
    # validate, pipe bad results to another cell
    date_status = []
    df['mods_originInfo_dateIssued_ss'] = df['mods_originInfo_dateIssued_ss'].fillna('')
    date_issued = df['mods_originInfo_dateIssued_ss'].to_list()
    for d in date_issued:
        valid = validate_date(d)
        date_status.append(valid)

    df['valid'] = date_status
    bad_dates = df.loc[~df['valid']]
    bad_dates['date_created_text'] = bad_dates['mods_originInfo_dateIssued_ss']
    df.update(bad_dates)

    # now delete non-valid EDTF dates from EDTF column
    df.loc[df['valid'].eq(False), 'mods_originInfo_dateIssued_ss'] = ''
    df.drop(['valid'], axis=1, inplace=True)

    # now we do date digitized column:
    # columns imported as string to prevent type error, but need to convert nulls
    # to NaN

    df[['mods_originInfo_dateModified_ss', 'mods_originInfo_dateCaptured_ss', 'mods_originInfo_dateCreated_ss']].replace('', np.nan, inplace=True)
    df['mods_originInfo_dateCaptured_ss'] = df[['mods_originInfo_dateModified_ss', 'mods_originInfo_dateCaptured_ss', 'mods_originInfo_dateCreated_ss']].apply(lambda x: '|'.join(x.dropna()), axis=1)
    df['mods_originInfo_dateCaptured_ss'] = df['mods_originInfo_dateCaptured_ss'].fillna('')
    date_digitized = df['mods_originInfo_dateCaptured_ss'].to_list()
    valid_dates = []
    for d in date_digitized:
        if d != '':
            valid = validate_date(d)
            if valid is False:
                valid_dates.append(f'@{d}')
                print('Bad date!')
            else:
                valid_dates.append(d)
        else:
            valid_dates.append('')

    df['mods_originInfo_dateCaptured_ss'] = valid_dates

    # combine places
    df['mods_place_placeTerm_text_ms'] = df[['mods_place_placeTerm_text_ms', 'mods_originInfo_place_placeTerm_text_ms', 'mods_originInfo_place_ms']].apply(lambda x: '|'.join(x.dropna()), axis=1)

    # combine conference data
    df['mods_name_personal_conference_namePart_ms'] = df[['mods_name_personal_conference_namePart_ms', 'mods_name_conference_namePart_ms', 'mods_name_corporate_conference_namePart_ms']].apply(lambda x: '|'.join(x.dropna()), axis=1)

    # combine note data
    df['mods_note_ms'] = df[['mods_note_ms', 'mods_note_i_ms']].apply(lambda x: '|'.join(x.dropna()), axis=1)

    # clean legacy model
    df['RELS_EXT_hasModel_uri_s'] = df['RELS_EXT_hasModel_uri_s'].str.replace('info:fedora/', '')
    
    # validate collection URLs
    df['mods_relatedItem_location_url_ms'] = df['mods_relatedItem_location_url_ms'].fillna('')
    collection_urls = df['mods_relatedItem_location_url_ms'].to_list()
    urls_to_keep = []
    for url in collection_urls:
        if url != '':
            valid_url = validate_url(url)
            urls_to_keep.append(valid_url)
        else:
            urls_to_keep.append('')
    
    df['mods_relatedItem_location_url_ms'] = urls_to_keep        

    columns_to_keep = ['notes',
                       'id',
                       'PID',
                       'parent',
                       'weight',
                       'people',
                       'mods_identifier_local_ms',
                       'recording_number',
                       'program_number',
                       'mods_titleInfo_subTitle_ms',
                       'mods_subject_authority_olac_topic_ms',
                       'mods_titleInfo_title_ms',
                       'fgs_label_ms',
                       'title',
                       'mods_accessCondition_restriction_on_access_ms',
                       'related_materials',
                       'mods_classification_ms',
                       'mods_place_placeTerm_text_ms',
                       'mods_subject_name_personal_namePart_ms',
                       'mods_physicalDescription_extent_ms',
                       'mods_originInfo_publisher_ms',
                       'mods_name_personal_speaker_affiliation_ms',
                       'mods_name_personal_conference_namePart_ms',
                       'olac_discourse_type',
                       'olac_linguistic_type',
                       'genre',
                       'mods_subject_authority_lcsh_topic_ms',
                       'mods_abstract_ms',
                       'mods_relatedItem_displayLabel_parentCollectionIdentifier_ms',
                       'mods_language_languageTerm_text_ms',
                       'mods_physicalDescription_form_authority_marcsmd_ms',
                       'mods_originInfo_dateCaptured_ss',
                       'mods_physicalDescription_note_ms',
                       'mods_name_family_namePart_ms',
                       'mods_subject_authority_local_cnair_topic_ms',
                       'mods_physicalDescription_digitalOrigin_ms',
                       'mods_relatedItem_note_ms',
                       'mods_note_ms',
                       'mods_physicalDescription_reformattingQuality_ms',
                       'mods_typeOfResource_ms',
                       'resource_type',
                       'mods_subject_geographic_ms',
                       'mods_tableOfContents_ms',
                       'mods_note_bioghist_ms',
                       'mods_subject_displayLabel_ms',
                       'mods_relatedItem_displayLabel_parentCollection_ms',
                       'mods_titleInfo_alternative_title_ms',
                       'mods_subject_temporal_ms',
                       'mods_accessCondition_use_and_reproduction_displayLabel_ms',
                       'mods_originInfo_dateIssued_ss',
                       'date_created_text',
                       'mods_subject_cartographics_coordinates_ms',
                       'mods_subject_authority_local_topic_ms',
                       'mods_relatedItem_identifier_uri_ms',
                       'mods_relatedItem_location_url_ms',
                       'date_modified',
                       'mods_physicalDescription_form_authority_marcform_ms',
                       'fedora_datastream_info_OBJ_ID_ms',
                       'fedora_datastream_info_TEI_ID_ms',
                       'fedora_datastream_info_JP2_ID_ms',
                       'RELS_EXT_hasModel_uri_s',
                       'model',
                       'RELS_EXT_isMemberOfCollection_uri_ms',
                       'RELS_EXT_isConstituentOf_uri_ms',
                       'RELS_EXT_isPageOf_uri_ms',
                       'RELS_EXT_isSequenceNumber_literal_ms',
                       'RELS_INT_isViewableByUser_literal_ms',
                       'RELS_INT_isViewableByRole_literal_ms',
                       'access_control',
                       'member_of',
                       'file',
                       'tei',
                       'display_hint',
                       'alias']

    df = df[columns_to_keep]
    df.rename(columns={"notes": "nötes"}, inplace=True)
    destination_path = os.path.join(output_dir, file)
    df.to_csv(destination_path, index=False, encoding="utf-8")
    print(f'Cleaning completed for {file}')
