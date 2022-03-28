
from ..utils import *
from .dataset import NERlikeDataset
from .model import NERlikeBERTClassifier
import numpy as np
import pandas as pd
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset 
from transformers import BertTokenizerFast
from tqdm.auto import tqdm

# Configurations
cfg = {}
cfg['model_name'] = 'nlpaueb/legal-bert-base-uncased'
cfg['split'] = 0.8
cfg['batch_size'] = 4
cfg['epoch'] = 7
cfg['lr'] = 1e-5
cfg['seq_len'] = 7 # number of input sentences
cfg['device'] =  "cuda" if torch.cuda.is_available() else "cpu"
# Paths
BASEPATH = os.path.dirname(__file__)
TRAINPATH = os.path.join(BASEPATH, '../processed_data/train_data.csv')
VALIDPATH = os.path.join(BASEPATH, '../processed_data/valid_data.csv')
CATNAMEPATH = os.path.join(BASEPATH, '../processed_data/catagories_name.json')

# Fix random seed for reproducibility
same_seeds(0)

def main():
    # Read files
    train_df = pd.read_csv(TRAINPATH)
    valid_df = pd.read_csv(VALIDPATH)
    classes, num_class = read_classes(CATNAMEPATH)

    # Tokenize sentence
    tokenizer = BertTokenizerFast.from_pretrained(cfg['model_name'])

    train_tokenized = tokenizer(train_df['sentence'].tolist(), add_special_tokens=False)
    valid_tokenized = tokenizer(valid_df['sentence'].tolist(), add_special_tokens=False)

    # Dataset / Dataloader
    train_set = NERlikeDataset(train_df, train_tokenized, seq_len=cfg['seq_len'])
    valid_set = NERlikeDataset(valid_df, valid_tokenized, seq_len=cfg['seq_len'])
    train_loader = DataLoader(train_set, batch_size=cfg['batch_size'], shuffle=True)
    valid_loader = DataLoader(valid_set, batch_size=cfg['batch_size'], shuffle=False)

    # print(train_set[0][0]['target'].shape)
    # Model / optimizer / scheduler
    model = NERlikeBERTClassifier(cfg['model_name'], num_class, freeze_bert=False).to(device=cfg['device'])
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg['lr'], eps=1e-8)
    # optimizer = torch.optim.SGD(model.parameters(), lr=cfg['lr'], momentum=0.9)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=1, factor=0.1, min_lr=cfg['lr']*0.01)
    # scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=1e-4, steps_per_epoch=len(train_loader), epochs=cfg['epoch'])
    # scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max= 2, eta_min=1e-6)
    criterion = torch.nn.CrossEntropyLoss()

    tr_losses, vl_losses, tr_acces, vl_acces, lrs = [], [], [], [], []

    # Running epoch
    for epoch in range(cfg['epoch']):
        print(f'epoch: {epoch}')
        tr_loss, tr_acc = train_one(model, train_loader, optimizer, criterion, scheduler)
        vl_loss, vl_acc = valid_one(model, valid_loader, criterion)
        lrs.append(get_lr(optimizer))
        scheduler.step(vl_acc)
        tr_losses.append(tr_loss)
        vl_losses.append(vl_loss)
        tr_acces.append(tr_acc)
        vl_acces.append(vl_acc)

    # Plot train/valid loss, accuracy, learning rate
    plot_fg(tr_losses, 'losses', 'loss', vl_losses)
    plot_fg(tr_acces, 'acces', 'acc', vl_acces)
    plot_fg(lrs, 'lrs', 'lr')

    
def train_one(model, dataloader, optimizer, criterion, scheduler):
    model.train()
    totalloss=0
    totalacc=0
    with tqdm(dataloader, unit='batch', desc='Train') as tqdm_loader:
        for idx, (data, sent_mask) in enumerate(tqdm_loader):
            for d in data:
                data[d] = data[d].to(cfg['device'])

            output, loss = model(**data)

            optimizer.zero_grad()
            loss.backward()
                        
            optimizer.step()
            # scheduler.step()

            nowloss = loss.item()

            pred = torch.argmax(output.cpu(), dim=2)
            acc = acc_counting(pred, data['target'].cpu(), sent_mask)

            totalloss += nowloss
            totalacc += acc
            tqdm_loader.set_postfix(loss=nowloss, avgloss=totalloss/(idx+1), avgACC=totalacc/(idx+1))
    return totalloss/len(tqdm_loader), totalacc/len(tqdm_loader)

def valid_one(model, dataloader, criterion):
    model.eval()
    totalloss=0
    bestloss=10
    totalacc=0
    bestacc=0
    with torch.no_grad():
        with tqdm(dataloader,unit='batch',desc='Valid') as tqdm_loader:
            for idx, (data, sent_mask) in enumerate(tqdm_loader):
                for d in data:
                    data[d] = data[d].to(cfg['device'])

                output, loss = model(**data)

                nowloss = loss.item()

                pred = torch.argmax(output.cpu(), dim=2)
                acc = acc_counting(pred, data['target'].cpu(), sent_mask)

                totalloss += nowloss
                totalacc += acc

                tqdm_loader.set_postfix(loss=nowloss, avgloss=totalloss/(idx+1) ,avgACC=totalacc/(idx+1))
        
            avgloss = totalloss/len(tqdm_loader)
            # if avgloss <= bestloss:
            #     bestloss = avgloss
            #     bestacc = totalacc/len(tqdm_loader)
            #     torch.save(model.state_dict(),'./best_model.pth')
    return totalloss/len(tqdm_loader), totalacc/len(tqdm_loader)
if __name__ == '__main__':
    main()