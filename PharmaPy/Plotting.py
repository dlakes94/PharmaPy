# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 18:02:01 2022

@author: dcasasor
"""

import matplotlib.pyplot as plt
import numpy as np

from PharmaPy.Errors import PharmaPyValueError


special = ('alpha', 'beta', 'gamma', 'phi', 'rho', 'epsilon', 'sigma', 'mu',
           'nu', 'psi', 'pi')


def latexify_name(name, units=False):
    parts = name.split('/')

    out = []
    count = 0
    for part in parts:
        sep = None
        if '**' in part:
            segm = part.split('**')
            sep = '^'
        elif '_' in part:
            segm = part.split('_')
            sep = '_'
        else:
            segm = [part]

        for ind, s in enumerate(segm):
            if s in special:
                segm[ind] = '\\' + s

        if sep is None:
            if count > 0:
                part = part + '^{-1}'
            else:
                part = segm[0]
        else:
            inv = ''
            if count > 0:
                inv = '-'

            part = segm[0] + sep + '{' + inv + segm[1] + '}'

        out.append(part)
        count += 1

    if len(out) > 1:
        out = ' \ '.join(out)
    else:
        out = out[0]

    if units:
        out = '$\mathregular{' + out + '}$'
    else:
        out = '$' + out + '$'

    return out


def color_axis(ax, color):
    ax.spines['right'].set_color(color)
    ax.tick_params(axis='y', colors=color, which='both')
    ax.yaxis.label.set_color(color)


def get_indexes(names, picks):
    names = [a for a in names]
    out = []

    lower_names = [str(a).lower() if isinstance(a, str) else a for a in names]

    for pick in picks:
        if isinstance(pick, str):
            low_pick = pick.lower()
            if low_pick in lower_names:
                out.append(lower_names.index(low_pick))
            else:
                mess = "Name '%s' not in the set of compound names "
                "listed in the pure-component json file" % low_pick
                raise PharmaPyValueError(mess)

        elif isinstance(pick, (int, np.int32, np.int64)):
            out.append(pick)

    return out


def get_state_data(uo, *state_names):

    time = uo.timeProf
    di = {}
    for name in state_names:
        idx = None
        if isinstance(name, (tuple, list, range)):
            state, idx = name
        else:
            state = name

        y = getattr(uo, state + 'Prof')
        if idx is not None:
            y = y[:, idx]

        di[state] = y

    return time, di


def get_states_result(result, *state_names):
    time = result.time

    out = {}
    for key in state_names:
        idx = None
        if isinstance(key, (list, tuple, range)):
            state, idx = key
            indexes = result.di_states[state]['index']
            idx = get_indexes(indexes, idx)
        else:
            state = key

        y = getattr(result, state)

        if idx is not None:
            y = y[:, idx]

        out[state] = y

    return time, out


def plot_function(uo, state_names, fig_map=None, ylabels=None,
                  include_units=True, **fig_kwargs):
    if hasattr(uo, 'dynamic_result'):
        time, data = get_states_result(uo.dynamic_result, *state_names)
    else:
        time, data = get_state_data(uo, *state_names)

    if fig_map is None:
        fig_map = range(len(data))

    fig, ax_orig = plt.subplots(**fig_kwargs)

    if isinstance(ax_orig, np.ndarray):
        axes = ax_orig.flatten()
    else:
        axes = (ax_orig, )

    count = 0
    linestyles = ('-', '--', '-.', ':')
    colors = plt.cm.tab10

    names = list(data.keys())

    for ind, idx in enumerate(fig_map):
        name = names[ind]
        y = data[name]
        twin = False

        index_y = False
        states_and_fstates = uo.states_di | uo.fstates_di
        index_y = states_and_fstates[name].get('index', False)

        if isinstance(state_names[ind], (tuple, list, range)):
            y_ind = state_names[ind][1]
            y_ind = get_indexes(index_y, y_ind)

            index_y = [index_y[a] for a in y_ind]

        if len(axes[idx].lines) > 0:
            ax = axes[idx].twinx()
            count += len(axes[idx].lines)
            twin = True
        else:
            ax = axes[idx]

        if y.ndim == 1:
            y = y.reshape(-1, 1)

        for sp, row in enumerate(y.T):
            ax.plot(time, row, color=colors(count),
                    linestyle=linestyles[count % len(linestyles)])

            if twin:
                color_axis(ax, colors(count))

            count += 1

        if ylabels is None:
            ylabel = name
        else:
            ylabel = latexify_name(ylabels[ind])

        units = states_and_fstates[name].get('units', '')
        if len(units) > 0:
            unit_name = latexify_name(states_and_fstates[name]['units'],
                                      units=True)
            ylabel = ylabel + ' (' + unit_name + ')'

        if index_y:
            ax.legend(index_y, loc='best')

        ax.set_ylabel(ylabel)

        count = 0

    if len(axes) == 1:
        axes = axes[0]

    return fig, ax_orig
