# AILA2020_sent_cls

[competition source](https://sites.google.com/view/aila-2021)  
## Task
- sequence classification
- Categories:  
  - Argument  
  - Ruling by Lower Court  
  - Ruling by Present Court  
  - Ratio of the decision  
  - Facts  
  - Precedent  
  - Statute  


## Dataset
- 60 traning documents  
  -  split to 48:12 training:validation  
-  10 testing documents  

## Data analyzation
- categories distribution  
<img src="https://user-images.githubusercontent.com/56257705/164142010-700b63f4-d799-4e17-96ac-05e946d4fd5e.png" width="500" />

- tokens length of sentence  
![](https://i.imgur.com/9LKGPqc.png)  
(max: 383)  
![](https://i.imgur.com/QL8F7u5.png)  
(max: 286)  

- seq_len of document  
![](https://i.imgur.com/ByC8aCB.png)  
(max: 658)  
![](https://i.imgur.com/RjnN870.png)  
(max: 471)  

## Model  
- Bert-BiLSTM-CRF  
<img src="https://user-images.githubusercontent.com/56257705/164142250-e5fa90f8-0fb2-47c1-a237-d57fd4b786f6.png" width="500" />  
- BERT_CLSlike  
<img src="https://user-images.githubusercontent.com/56257705/165811478-3ca8ac08-b787-4b8a-b8d3-143254cebcb0.png" width="500" />  
- BERT_NERlike  
<img src="https://user-images.githubusercontent.com/56257705/165811629-8cd272c4-9f35-4fec-ab3f-081c75f0d4bc.png" width="500" />  
- pipe-line model  
<img src="https://user-images.githubusercontent.com/56257705/164142728-fca88c85-548d-45c1-b8c5-1d91c5fdbd64.png" width="500" />  

## Result  
  
||Fin-tuned BERT|BERT|  
|-|-|-|  
|valid|0.66|0.591|  
|test|0.6627|0.6582|  
