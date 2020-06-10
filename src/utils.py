import numpy as np
import pandas as pd
from collections import Counter
from math import log2
import matplotlib.colors as mcolors
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
font = {# 'family' : 'serif', # Times (source: https://matplotlib.org/tutorials/introductory/customizing.html)
        'family': 'sans-serif', # Helvetica
#         'family': 'monospace',
#         'weight' : 'bold',
        'size'   : 12}
matplotlib.rc('font', **font) 
text = {'usetex': False}
matplotlib.rc('text', **text)
monospace_font = {'fontname':'monospace'}
CSS4_COLORS = mcolors.CSS4_COLORS

def read_fasta(filename):
    seq_list = []
    seq = ''
    with open(filename) as f:
        for line in f:
            if line[0] == '>':
                if len(seq) > 0:
                    seq_list.append((header, seq.upper()))
                    seq = ''
                    header = line[1:].strip('\n')
                else:
                    seq = ''
                    header = line[1:].strip('\n')
            else:
                seq += line.strip('\n').replace(' ', '').replace('-', 'N')
        if len(seq) > 0:
            seq_list.append((header, seq.upper()))
    return seq_list

def read_alignment(filename):
    seq_list = []
    seq = ''
    with open(filename) as f:
        for line in f:
            if line[0] == '>':
                if len(seq) > 0:
                    seq_list.append((header, seq.upper()))
                    seq = ''
                    header = line[1:].strip('\n')
                else:
                    seq = ''
                    header = line[1:].strip('\n')
            else:
                seq += line.strip('\n')
        if len(seq) > 0:
            seq_list.append((header, seq.upper()))
    return seq_list

def write_fasta(filename, seq_dict):
    with open(filename, 'w+') as f:
        for header in seq_dict:
            f.write('>{}\n'.format(header))
            f.write('{}\n'.format(seq_dict[header]))

def load_data(gisaid_filename = '../mafft_20200405.output'):
    seq_list = read_alignment(gisaid_filename)
    seq_dict = {'gisaid_epi_isl': [], 'sequence': []}
    for header, seq in seq_list:
        header = header.split('|')[1]
        if header == 'NC_045512.2':
            REFERENCE = (header, seq)
            continue
        seq_dict['gisaid_epi_isl'].append(header)
        seq_dict['sequence'].append(seq)

    seq_df = pd.DataFrame.from_dict(seq_dict)
    return seq_df, REFERENCE

def load_data_nextstrain(gisaid_filename = '../mafft_20200405.output'):
    seq_list = read_alignment(gisaid_filename)
    seq_dict = {'strain': [], 'sequence': []}
    for header, seq in seq_list:
        header = header.strip('\n')
        if len(header.split('|')) >= 2 and header.split('|')[1] == 'NC_045512.2':
            REFERENCE = ('NC_045512.2', seq)
            continue
        seq_dict['strain'].append(header)
        seq_dict['sequence'].append(seq)

    seq_df = pd.DataFrame.from_dict(seq_dict)
    return seq_df, REFERENCE

def preprocessing_nextstrain(seq_df, meta_df):
    # join sequence with metadate
    data_df = seq_df.join(meta_df.set_index(['strain']), on = ['strain'],how = 'left')
    # filter by Human, valid date time and convert date column to 'datetime' dtype
    data_df = data_df[data_df.apply(lambda x: (x['host'] == 'Human') and ('X' not in x['date']) and len(x['date'].split('-')) == 3, axis=1)]
    data_df = data_df[data_df.apply(lambda x: (x['host'] == 'Human') and ('X' not in x['date']) and len(x['date'].split('-')) == 3, axis=1)]
    data_df['country/region'] = data_df.apply(lambda x: 'Mainland China' if x['country'] == 'China' else x['country'], axis=1)
    data_df['country/region_exposure'] = data_df.apply(lambda x: 'Mainland China' if x['country_exposure'] == 'China' else x['country_exposure'], axis=1)

    data_df['date'] = pd.to_datetime(data_df['date'])
    data_df = data_df.rename(columns={'region': 'continent', 'region_exposure': 'continent_exposure'})
    data_df = data_df.drop(['virus', 'strain', 'genbank_accession', 'country', 'title', 'country_exposure'], axis = 1)
    return data_df

def preprocessing(seq_df, meta_df):
    # join sequence with metadate
    data_df = seq_df.join(meta_df.set_index(['gisaid_epi_isl']), on = ['gisaid_epi_isl'],how = 'left')
    # filter by Human, valid date time and convert date column to 'datetime' dtype
    data_df = data_df[data_df.apply(lambda x: (x['host'] == 'Human') and ('X' not in x['date']) and len(x['date'].split('-')) == 3, axis=1)]
    data_df = data_df[data_df.apply(lambda x: (x['host'] == 'Human') and ('X' not in x['date']) and len(x['date'].split('-')) == 3, axis=1)]
    data_df['country/region'] = data_df.apply(lambda x: 'Mainland China' if x['country'] == 'China' else x['country'], axis=1)
    data_df['country/region_exposure'] = data_df.apply(lambda x: 'Mainland China' if x['country_exposure'] == 'China' else x['country_exposure'], axis=1)

    data_df['date'] = pd.to_datetime(data_df['date'])
    data_df = data_df.rename(columns={'region': 'continent', 'region_exposure': 'continent_exposure'})
    data_df = data_df.drop(['virus', 'strain', 'genbank_accession', 'country', 'title', 'country_exposure'], axis = 1)
    return data_df

def get_color_names(CSS4_COLORS, num_colors):
    # bad_colors = set(['seashell', 'linen', 'ivory', 'oldlace',
    #                   'floralwhite', 'lightyellow', 'lightgoldenrodyellow', 'honeydew', 'mintcream', 'azure', 'lightcyan',
    #                   'aliceblue', 'ghostwhite', 'lavenderblush'
    #                  ])
    bad_colors = set([])
    by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(color))),
                             name)
                            for name, color in CSS4_COLORS.items())
    names = [name for hsv, name in by_hsv][14:]
    prime_names = ['red', 'orange', 'green', 'blue', 'gold', 
                 'lightskyblue', 'brown', 'black', 'pink',
                 'yellow']
    OTHER = 'gray'
    name_list = [name for name in names if name not in prime_names and name != OTHER and name not in bad_colors]   
    if num_colors > len(name_list) - 10:
        print('No enough distinctive colors!!!')
        name_list = name_list + name_list
    if num_colors > len(prime_names):
        ind_list = np.linspace(0, len(name_list), num_colors - 10, dtype = int, endpoint=False).tolist()
        color_names = prime_names + [name_list[ind] for ind in ind_list]
    else:
        color_names = prime_names[:num_colors]
    return color_names

def global_color_map(COLOR_DICT, ISM_list, out_dir='figures'):   
    # adapted from https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    ncols = 2
    n = len(COLOR_DICT)
    nrows = n // ncols + int(n % ncols > 0)

    cell_width = 1200
    cell_height = 100
    swatch_width = 180
    margin = 24
    topmargin = 40

    width = cell_width * 3 + 2 * margin
    height = cell_height * nrows + margin + topmargin
    dpi = 300

    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
    fig.subplots_adjust(margin/width, margin/height,
                        (width-margin)/width, (height-topmargin)/height)

    ax.set_xlim(0, cell_width * 4)
    ax.set_ylim(cell_height * (nrows-0.5), -cell_height/2.)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_axis_off()
    # ax.set_title(title, fontsize=24, loc="left", pad=10)
    ISM_list.append('OTHER')
    for i, name in enumerate(ISM_list):
        row = i % nrows
        col = i // nrows
        y = row * cell_height

        swatch_start_x = cell_width * col
        swatch_end_x = cell_width * col + swatch_width
        text_pos_x = cell_width * col + swatch_width + 50

        ax.text(text_pos_x, y, name, fontsize=14,
                fontname='monospace',
                horizontalalignment='left',
                verticalalignment='center')

        ax.hlines(y, swatch_start_x, swatch_end_x,
                  color=COLOR_DICT[name], linewidth=18)
    plt.savefig('{}/add_color_map.pdf'.format(out_dir), bbox_inches='tight', dpi=dpi)
    plt.show()
# ambiguous bases correction
def is_same(error, target, mask, ISM_LEN, ambiguous_base):
    match = np.array(list(target)) == np.array(list(error))
    res = np.logical_or(mask, match).sum() == ISM_LEN
    return res

def error_correction(error, ambiguous_base, base_to_ambiguous, ISM_list, ISM_LEN, THRESHOLD = 0.9):
    mask = [True if base in ambiguous_base else False for base in error]
    support_ISM = []
    for target_ISM in ISM_list:
        if is_same(error, target_ISM, mask, ISM_LEN, ambiguous_base):
            support_ISM.append(target_ISM)
    partial_correction = list(error)
    FLAG = True
    for position_idx in list(np.where(mask)[0]):
        possible_bases = set([candid_ISM[position_idx] for candid_ISM in support_ISM])
        possible_bases.discard('N')
        possible_bases.discard(error[position_idx])
        possible_bases.discard('-')
        non_ambiguous_set = set([])
        ambiguous_set = set([])
        for base in possible_bases:
            if base not in ambiguous_base:
                non_ambiguous_set.add(base)
            else:
                ambiguous_set.add(base)
        if len(ambiguous_set) == 0:
            if len(non_ambiguous_set) == 0:
                continue
            bases = ''.join(sorted(non_ambiguous_set))
            if len(bases) == 1:
                num_support = len([candid_ISM[position_idx] for candid_ISM in support_ISM if candid_ISM[position_idx] == bases])
                non_support = set([candid_ISM[position_idx] for candid_ISM in support_ISM if candid_ISM[position_idx] != bases])
                if num_support/len(support_ISM) > THRESHOLD and bases in ambiguous_base[error[position_idx]]:
                    partial_correction[position_idx] = bases
                else:
                    FLAG = False
                    print('LOG: one_base_correction failed because no enough support: {}/{}: {}->{}'.format(num_support, len(support_ISM), non_support, bases))
            elif bases in base_to_ambiguous:
                FLAG = False
                partial_correction[position_idx] = base_to_ambiguous[bases]
            else:
                FLAG = False
                print("LOG: can't find: {}".format(bases))
        else:
            bases_from_ambiguous_set = set([])
            ambiguous_bases_intersection = ambiguous_base[error[position_idx]].copy()  
            for base in ambiguous_set:
                bases_from_ambiguous_set = bases_from_ambiguous_set.union(ambiguous_base[base])
                ambiguous_bases_intersection = ambiguous_bases_intersection.intersection(ambiguous_base[base])
            
            if bases_from_ambiguous_set.issubset(ambiguous_base[error[position_idx]]) is False:
                print("LOG: new bases {} conflict with or are not as good as original bases {}".format(bases_from_ambiguous_set, ambiguous_base[error[position_idx]]))
                bases_from_ambiguous_set = ambiguous_base[error[position_idx]]
                
            bases_from_ambiguous_set = ''.join(sorted(bases_from_ambiguous_set))
            
            bases = ''.join(sorted(non_ambiguous_set))
            
            if len(bases) == 0:
                bases = bases_from_ambiguous_set
            if len(bases) == 1 and bases in bases_from_ambiguous_set:
                num_support = len([candid_ISM[position_idx] for candid_ISM in support_ISM if candid_ISM[position_idx] == bases])
                non_support = set([candid_ISM[position_idx] for candid_ISM in support_ISM if candid_ISM[position_idx] != bases])
                if num_support/len(support_ISM) > THRESHOLD and bases in ambiguous_bases_intersection:
                    partial_correction[position_idx] = bases
                else:
                    if bases not in ambiguous_bases_intersection:
                        print('LOG: conflicts dected between proposed correct and all supporting ISMs')
                        bases = ''.join(ambiguous_bases_intersection.add(base))
                        if bases in base_to_ambiguous and set(bases).issubset(ambiguous_base[error[position_idx]]):
                            FLAG = False
                            partial_correction[position_idx] = base_to_ambiguous[bases]
                    else:
                        FLAG = False
                        print('LOG: one_base_correction failed because no enough support: {}/{}: {}->{}'.format(num_support, len(support_ISM), non_support, bases))
            else:
                bases = ''.join(sorted(set(bases_from_ambiguous_set + bases)))
                if bases in base_to_ambiguous and set(bases).issubset(ambiguous_base[error[position_idx]]):
                    FLAG = False
                    partial_correction[position_idx] = base_to_ambiguous[bases]
                else:
                    FLAG = False
                    print("LOG: new bases {} conflict with or are not as good as original bases {}".format(bases, ambiguous_base[error[position_idx]]))
            
    return FLAG, ''.join(partial_correction)

def get_weblogo(seq_list, position):
    return Counter([seq_list[i][position] for i in range(len(seq_list))])

import matplotlib as mpl
from matplotlib.text import TextPath
from matplotlib.patches import PathPatch
from matplotlib.font_manager import FontProperties

fp = FontProperties(family="monospace", weight="bold") 
globscale = 1.35
LETTERS = { "T" : TextPath((-0.305, 0), "T", size=1, prop=fp),
            "G" : TextPath((-0.384, 0), "G", size=1, prop=fp),
            "A" : TextPath((-0.35, 0), "A", size=1, prop=fp),
            "C" : TextPath((-0.366, 0), "C", size=1, prop=fp),
            "U" : TextPath((-0.366, 0), "U", size=1, prop=fp),
          }
# LETTERS = { "T" : TextPath((0, 0), "T", size=1, prop=fp),
#             "G" : TextPath((0, 0), "G", size=1, prop=fp),
#             "A" : TextPath((0, 0), "A", size=1, prop=fp),
#             "C" : TextPath((0, 0), "C", size=1, prop=fp),
#             "U" : TextPath((0, 0), "U", size=1, prop=fp),
#           }

COLOR_SCHEME = {'G': 'orange', 
                'A': 'red', 
                'C': 'blue', 
                'T': 'darkgreen',
                'U': 'black'
               }

def letterAt(letter, x, y, yscale=1, ax=None):
    text = LETTERS[letter]

    t = mpl.transforms.Affine2D().scale(1*globscale, yscale*globscale) + \
        mpl.transforms.Affine2D().translate(x,y) + ax.transData
    p = PathPatch( text, lw=0, fc=COLOR_SCHEME[letter],  transform=t)
    if ax != None:
        ax.add_artist(p)
    return p

def get_nt_scores(weblogo):
    scores = []
    for i in range(weblogo.shape[1]):
        tmp = [('A', weblogo[0, i]), ('C', weblogo[1, i]), ('G', weblogo[2, i]), ('T', weblogo[3, i])]
        tmp.sort(key= lambda x: x[1])
        scores.append(tmp)
    return scores

def get_att_box(att):
    box = []
    for i in range(att.shape[0]):
        if att[i,0] > 0:
            if len(box) == 0:
                if i - 4 >= 0:
                    box.append([i-4, i+4])
                else:
                    box.append([0, i+4])
                if i + 4 >= att.shape[0]:
                    box[-1][-1] = att.shape[0]
                    break
            else:
                if i - 4 <= box[-1][-1]:
                    if i + 4 >= att.shape[0]:
                        box[-1][-1] = att.shape[0]
                        break
                    else:
                        box[-1][-1] = i + 4
                else:
                    if i - 4 >= 0:
                        box.append([i-4, i+4])
                    else:
                        box.append([0, i+4])
                    if i + 4 >= att.shape[0]:
                        box[-1][-1] = att.shape[0]
                        break
    return box

import matplotlib.patches as patches
def plot(ax, tmp_logo, tmp_att):
    ALL_SCORES2 = get_nt_scores(tmp_logo)
    boxes = get_att_box(tmp_att)
    all_scores = ALL_SCORES2
    x = 1
    maxi = 0
    for scores in all_scores:
        y = 0
        for base, score in scores:
            letterAt(base, x, y, score, ax)
            y += score
        x += 1
        maxi = max(maxi, y)
    maxi += maxi * 0.05
    ax.set_xticklabels([i for i in range(tmp_logo.shape[1])], rotation = 90, fontsize = 14)
    for box in boxes:
        rect = patches.Rectangle((box[0] + 1 - 0.5,0),box[1] - box[0],maxi,linewidth=2,edgecolor='r',facecolor='none')
        ax.add_patch(rect)

    maxi += maxi * 0.05
    ax.get_yaxis().set_visible(True)
    ax.set_xticks(range(1,x))
    ax.set_xlim((0, x)) 
    ax.set_ylim((0, maxi))      
    plt.show()
    
def plot_scale(ax, tmp_logo, xlabel, ylabel):
    ALL_SCORES2 = get_nt_scores(tmp_logo)
    all_scores = ALL_SCORES2
    x = 1
    maxi = 0
    for scores in all_scores:
        y = 0
        for base, score in scores:
            letterAt(base, x, y, score, ax)
            y += score
        x += 1
        maxi = max(maxi, y)
    maxi += maxi * 0.05
    ax.set_xticklabels([i + 1 for i in range(tmp_logo.shape[1])], rotation = 90)
    ax.tick_params(labelsize = 25)
    ax.get_yaxis().set_visible(True)
    ax.set_xticks(range(1,x))
    ax.set_xlim((0, x)) 
    ax.set_ylim((0, maxi))  
    ax.set_ylabel(ylabel, fontsize = 30) 
    if xlabel:
        ax.set_xlabel(xlabel, fontsize = 30) 
