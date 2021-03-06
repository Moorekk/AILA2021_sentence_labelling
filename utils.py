import numpy as np
import pandas as pd
import torch
import random
import os
def same_seeds(seed):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True

import json
def read_classes(CATNAMEPATH):
    with open(CATNAMEPATH) as f:
        data = json.load(f)
        classes = data.values()
        num_class = len(classes)
        return classes, num_class

def get_lr(optimizer):
    for param_group in optimizer.param_groups:
        return param_group['lr']

def acc_counting(pred, truth, mask=None):
    # tensor, tensor, tensor(bool)
    pred = torch.Tensor(pred) if not isinstance(pred, torch.Tensor) else pred
    truth = torch.Tensor(truth) if not isinstance(truth, torch.Tensor) else truth
    pred = pred.view(-1)
    truth = truth.view(-1)
    if mask != None:
        mask = torch.Tensor(mask) if not isinstance(mask, torch.Tensor) else mask
        mask = mask.view(-1)
        assert pred.shape == truth.shape == mask.shape, f'Shape not match! {pred.shape}, {truth.shape}, {mask.shape}'
        acc = 0
        tt = torch.sum(mask)
        for i in range(len(pred)):
            if mask[i] == 1 and pred[i] == truth[i]:
                acc += 1
        # print(acc)
        return (acc / tt).item()
    else:
        assert pred.shape == truth.shape, f'Shape not match! {pred.shape}, {truth.shape}'
        acc = torch.sum(pred == truth)
        return (acc / len(pred)).item()

import matplotlib.pyplot as plt

def plot_fg(x1, title, y, path, x2=None):
    plt.clf()
    plt.title(title)
    plt.xlabel('epoch')
    plt.ylabel(y)
    plt.plot(x1, label='train')
    if x2 is not None:
        plt.plot(x2, label='valid')
    plt.legend()
    # plt.show()
    plt.savefig(os.path.join(path, title+'.jpg'))
    
def plot_confusion_matrix(conf_matrix, save_fg_path='./confusion_matrix.png'):
    plt.clf()
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.matshow(conf_matrix, cmap=plt.cm.Blues, alpha=0.3)
    for i in range(conf_matrix.shape[0]):
        for j in range(conf_matrix.shape[1]):
            ax.text(x=j, y=i,s=conf_matrix[i, j], va='center', ha='center', size='xx-large')
    
    plt.xlabel('Predictions', fontsize=18)
    plt.ylabel('Actuals', fontsize=18)
    plt.title('Confusion Matrix', fontsize=18)
    plt.show()
    if(save_fg_path!=None):
        plt.savefig(save_fg_path)
        
# calculate accuracy
def doc_accuracy_score(df, pred, isPrint=True, mask=None):
    docid = set(df['docid'].tolist())
    ttdacc, allacc, alltt = 0, 0, 0
    for id in docid:
        idxrange = df.index[df['docid'] == id].tolist()
        # print(idxrange)
        # print(idxrange)
        if mask is not None:
            acc = acc_counting(df['category'][idxrange].tolist(), pred[idxrange].tolist(), mask[idxrange].tolist())
        else:
            acc = acc_counting(df['category'][idxrange].tolist(), pred[idxrange].tolist())
        if isPrint:
            print(f'Document {id:0>2d} acc: {acc:.4f}')
        ttdacc += acc
        allacc += acc * len(pred[idxrange])
        alltt += len(pred[idxrange])
    # print(ttdacc/len(docid))
    # print(allacc/alltt)
    if isPrint:
        print(f'Average acc over documents: {ttdacc/len(docid):.4f}')
        print(f'Average acc of all sentences:  {allacc/alltt:.4f}')
    else:
        return ttdacc/len(docid), allacc/alltt