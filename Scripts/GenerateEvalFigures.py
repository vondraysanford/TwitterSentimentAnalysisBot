'''
Generates the model evaluation figures embedded in the README (light + dark variants).

Reproduces the evaluation protocol from Scripts/GenerateModel.ipynb:
    * features/target built identically to the notebook
    * 70/30 held-out split (random_state=1234)
    * 5-fold CV ROC (KFold shuffle, random_state=33) with XGBClassifier(scale_pos_weight)
    * confusion matrix from a same-spec model trained on train, scored on held-out test
    * feature importances read from the deployed Resources/model.pickle

Requires Resources/twitter_dataset_expanded.csv (gitignored - build it with
Scripts/GenerateExpandedTwitterDataset.py or see the Datasets section of the README).

Usage (from the repo root):
    python Scripts/GenerateEvalFigures.py [output_dir]   # default: docs/images
'''

# Imports
import json
import pickle
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, roc_curve, confusion_matrix)
from xgboost import XGBClassifier

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else 'docs/images'

# Feature order must match the deployed model (see get_user_info in sentimentbot.py)
FEATURES = ['verified', 'hour_created', 'default_profile_image', 'listed_count',
            'followers_count', 'following_count', 'tweet_count',
            'average_tweets_per_day', 'network', 'tweet_to_followers',
            'follower_acq_rate', 'following_acq_rate', 'listed_acq_rate']

FEATURE_LABELS = {
    'verified': 'Verified',
    'hour_created': 'Hour created',
    'default_profile_image': 'Default profile image',
    'listed_count': 'Listed count',
    'followers_count': 'Followers count',
    'following_count': 'Following count',
    'tweet_count': 'Tweet count',
    'average_tweets_per_day': 'Avg tweets / day',
    'network': 'Network (log fol. x log fri.)',
    'tweet_to_followers': 'Tweet-to-followers',
    'follower_acq_rate': 'Follower acq. rate',
    'following_acq_rate': 'Following acq. rate',
    'listed_acq_rate': 'Listed acq. rate',
}

# One theme per README color scheme; GitHub picks the variant via <picture> tags
THEMES = {
    'light': dict(surface='#fcfcfb', ink='#0b0b0b', secondary='#52514e',
                  muted='#898781', grid='#e1e0d9', baseline='#c3c2b7',
                  blue='#2a78d6',
                  ramp=['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5',
                        '#256abf', '#184f95', '#0d366b']),
    'dark': dict(surface='#1a1a19', ink='#ffffff', secondary='#c3c2b7',
                 muted='#898781', grid='#2c2c2a', baseline='#383835',
                 blue='#3987e5',
                 ramp=['#0d366b', '#184f95', '#256abf', '#3987e5',
                       '#6da7ec', '#9ec5f4', '#cde2fb']),
}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue', 'Arial', 'DejaVu Sans'],
})


def styled_axes(theme, figsize):
    fig, ax = plt.subplots(figsize=figsize, dpi=200)
    fig.patch.set_facecolor(theme['surface'])
    ax.set_facecolor(theme['surface'])
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(theme['baseline'])
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=theme['muted'], labelsize=8, length=3, width=0.8)
    return fig, ax


def save(fig, name, mode):
    path = f'{OUT_DIR}/{name}-{mode}.png'
    fig.savefig(path, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print('wrote', path)


# Data prep (mirrors GenerateModel.ipynb)
df = pd.read_csv('Resources/twitter_dataset_expanded.csv')
df['bot'] = df['bot_status'].apply(lambda x: 1 if x == 'bot' else 0)
DEFAULT_IMG = 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png'
df['default_profile_image'] = (df['profile_image_url'] == DEFAULT_IMG).astype(int)
df['verified'] = df['verified'].apply(lambda x: 1 if x in (True, 'True') else 0)
df['hour_created'] = pd.to_datetime(df['created_at']).dt.hour

X, y = df[FEATURES], df['bot']
estimate = (y == 0).sum() / (y == 1).sum()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=1234)

# Deployed model (for feature importances) - verify it matches the feature list
with open('Resources/model.pickle', 'rb') as read_file:
    deployed = pickle.load(read_file)
assert deployed.n_features_in_ == len(FEATURES), deployed.n_features_in_

# CV ROC on the training portion
kf = KFold(n_splits=5, shuffle=True, random_state=33)
Xa, ya = np.array(X_train), np.array(y_train)
mean_fpr = np.linspace(0, 1, 200)
fold_curves, fold_aucs, tprs = [], [], []
for train_ind, val_ind in kf.split(Xa, ya):
    model = XGBClassifier(scale_pos_weight=estimate)
    model.fit(Xa[train_ind], ya[train_ind])
    proba = model.predict_proba(Xa[val_ind])[:, 1]
    fpr, tpr, _ = roc_curve(ya[val_ind], proba)
    fold_curves.append((fpr, tpr))
    fold_aucs.append(roc_auc_score(ya[val_ind], proba))
    interp = np.interp(mean_fpr, fpr, tpr)
    interp[0] = 0.0
    tprs.append(interp)
mean_tpr = np.mean(tprs, axis=0)
mean_tpr[-1] = 1.0

# Held-out test metrics
final = XGBClassifier(scale_pos_weight=estimate)
final.fit(X_train, y_train)
pred = final.predict(X_test)
proba = final.predict_proba(X_test)[:, 1]
metrics = dict(
    accuracy=accuracy_score(y_test, pred),
    precision=precision_score(y_test, pred),
    recall=recall_score(y_test, pred),
    f1=f1_score(y_test, pred),
    roc_auc=roc_auc_score(y_test, proba),
    cv_auc_mean=float(np.mean(fold_aucs)),
    cv_auc_std=float(np.std(fold_aucs)),
    n_train=len(X_train), n_test=len(X_test),
    bots=int(y.sum()), humans=int((y == 0).sum()),
)
cm = confusion_matrix(y_test, pred)

for mode, t in THEMES.items():

    # ROC curve
    fig, ax = styled_axes(t, (5.4, 4.2))
    ax.grid(axis='both', color=t['grid'], linewidth=0.6)
    ax.set_axisbelow(True)
    for fpr, tpr in fold_curves:
        ax.plot(fpr, tpr, color=t['blue'], lw=1, alpha=0.28)
    ax.plot(mean_fpr, mean_tpr, color=t['blue'], lw=2,
            label=f'Mean ROC (AUC = {np.mean(fold_aucs):.3f} $\\pm$ {np.std(fold_aucs):.3f})')
    ax.plot([0, 1], [0, 1], ls='--', lw=1.2, color=t['baseline'], label='Chance')
    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.01, 1.02)
    ax.set_xlabel('False positive rate', fontsize=9, color=t['secondary'])
    ax.set_ylabel('True positive rate', fontsize=9, color=t['secondary'])
    ax.set_title('Bot Classifier ROC - 5-fold cross-validation',
                 fontsize=10.5, color=t['ink'], pad=12, loc='left')
    leg = ax.legend(loc='lower right', fontsize=8, frameon=False)
    for txt in leg.get_texts():
        txt.set_color(t['secondary'])
    save(fig, 'roc-curve', mode)

    # Confusion matrix
    cmap = LinearSegmentedColormap.from_list('seq', t['ramp'])
    fig, ax = styled_axes(t, (4.4, 4.0))
    ax.imshow(cm, cmap=cmap)
    labels = ['Human', 'Bot']
    ax.set_xticks([0, 1], labels)
    ax.set_yticks([0, 1], labels)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    thresh = cm.min() + (cm.max() - cm.min()) / 2
    total = cm.sum()
    for i in range(2):
        for j in range(2):
            hot = cm[i, j] > thresh
            dark_cell = hot if mode == 'light' else not hot
            color = '#ffffff' if dark_cell else '#0b0b0b'
            ax.text(j, i, f'{cm[i, j]:,}', ha='center', va='center',
                    fontsize=15, fontweight='bold', color=color)
            ax.text(j, i + 0.16, f'{cm[i, j] / total:.1%}', ha='center',
                    va='center', fontsize=8.5, color=color, alpha=0.85)
    ax.set_xlabel('Predicted label', fontsize=9, color=t['secondary'])
    ax.set_ylabel('True label', fontsize=9, color=t['secondary'])
    ax.set_title(f'Confusion Matrix - held-out test set (n = {total:,})',
                 fontsize=10.5, color=t['ink'], pad=12, loc='left')
    save(fig, 'confusion-matrix', mode)

    # Feature importance (deployed model)
    imp = sorted(zip(FEATURES, deployed.feature_importances_), key=lambda p: p[1])
    names = [FEATURE_LABELS[f] for f, _ in imp]
    vals = [v for _, v in imp]
    fig, ax = styled_axes(t, (6.2, 4.6))
    ax.grid(axis='x', color=t['grid'], linewidth=0.6)
    ax.set_axisbelow(True)
    ax.barh(names, vals, color=t['blue'], height=0.62)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', length=0, labelsize=8.5)
    for lbl in ax.get_yticklabels():
        lbl.set_color(t['secondary'])
    ax.set_xlabel('Importance (gain-based score)', fontsize=9, color=t['secondary'])
    ax.set_title('Feature Importance - deployed XGBoost model',
                 fontsize=10.5, color=t['ink'], pad=12, loc='left')
    save(fig, 'feature-importance', mode)

print(json.dumps(metrics, indent=2))
