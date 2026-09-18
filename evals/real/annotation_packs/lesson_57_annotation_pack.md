# Annotation Pack — lesson_57

## Lesson metadata

- lesson_id: `lesson_57`
- document_id: `doc_23`
- source type: `document`
- source file/title: `6-CNN_for_Image_Classification.pdf`
- source_group: `file:ce10e7a6e7a8599107917393354752a63cc09abe0a6c550575d6d2a83c42dc24`
- chunk count: `43`
- page count OR duration: `43 pages`

## Source overview

**AI-GENERATED ORIENTATION SUMMARY — NOT GROUND TRUTH**

CNN for Image Classification Introduction to Deep Learning Image Classification 2 •Imageclassificationisthetaskofassigningalabel orclasstoanentireimage

## Source sections

### Page 1

Chunk IDs:
- `chunk_pdf_lesson_57_001`

Text:

CNN for Image Classification
Introduction to Deep Learning

### Page 2

Chunk IDs:
- `chunk_pdf_lesson_57_002`

Text:

Image Classification
2
•Imageclassificationisthetaskofassigningalabel
orclasstoanentireimage

### Page 3

Chunk IDs:
- `chunk_pdf_lesson_57_003`

Text:

Image Classification
3
•Imagesareexpectedtohaveonlyoneclassfor
eachimage

### Page 4

Chunk IDs:
- `chunk_pdf_lesson_57_004`

Text:

Image Classification
4
•Imageclassificationmodelstakeanimageas
inputandreturnapredictionaboutwhichclass
theimagebelongsto

### Page 5

Chunk IDs:
- `chunk_pdf_lesson_57_005`

Text:

Image Classification
5
•“Dogvs.cat”classificationisoneproblemofthe
so-calledbinaryclassificationofimages

### Page 6

Chunk IDs:
- `chunk_pdf_lesson_57_006`

Text:

Image Classification
6
•Having a grey scale image with size 28 * 28 presenting a 
number from 0-9
•Predict which number the image is presenting ?
•àProblem of multi-class classification of images

### Page 7

Chunk IDs:
- `chunk_pdf_lesson_57_007`

Text:

Image Classification
7
Multi-class vs. Multi-label classification

### Page 8

Chunk IDs:
- `chunk_pdf_lesson_57_008`

Text:

Image Datasets
8
You can visit this website to get information of the 
dataset: https://paperswithcode.com/datasets
Use in this lecture: 
•“Dogs vs. Cats” dataset downloaded from Kaggle 
https://www.kaggle.com/c/dogs-vs-cats/data
•“MNIST Dataset of handwritten digits” downloaded 
from Kaggle 
https://www.kaggle.com/datasets/hojjatk/mnist-dataset

### Page 9

Chunk IDs:
- `chunk_pdf_lesson_57_009`

Text:

Dataset Preparation
9
•Standardize images prior to the model requirement
•Standardize directories for training set, validation set and test set

### Page 10

Chunk IDs:
- `chunk_pdf_lesson_57_010`

Text:

CNN model for Image Classification
10
•Input data are images àchoose CNN model
•General progress: input image àConvolutional layer (Conv) + Pooling Layer 
(Pool) àFully Connected Layer (FC) àOutput

### Page 11

Chunk IDs:
- `chunk_pdf_lesson_57_011`

Text:

CNN model for Image Classification
11
•Input data are images àchoose CNN model
•General progress: input image àConvolutional layer (Conv) + Pooling Layer 
(Pool) àFully Connected Layer (FC) àOutput

### Page 12

Chunk IDs:
- `chunk_pdf_lesson_57_012`

Text:

CNN model for Image Classification
12
•Input data are images àchoose CNN model
•General progress: input image àConvolutional layer (Conv) + Pooling Layer 
(Pool) àFully Connected Layer (FC) àOutput

### Page 13

Chunk IDs:
- `chunk_pdf_lesson_57_013`

Text:

CNN model for Image Classification
13
•You can build a CNN network by yourself to perform image 
classification
•You can also use the existing CNN architecture like VGG, 
ResNet, etc. to perform image classification
•Or you can modify the existing CNN architecture (VGG, 
ResNet, etc.) to perform image classification

### Page 14

Chunk IDs:
- `chunk_pdf_lesson_57_014`

Text:

CNN model for Image Classification
14
Top 1-accuracy, performance and size on the ImageNet dataset
See: https://paperswithcode.com/sota/image-classification-on-
imagenetfor more information
Canziani, Paszke, and Culurciello. "An Analysis of Deep Neural 
Network Models for Practical Applications." (May 2016).

### Page 15

Chunk IDs:
- `chunk_pdf_lesson_57_015`

Text:

CNN model for Image Classification
15
Meta Pseudo Labels, HieuPham et al. (Jan 2021).

### Page 16

Chunk IDs:
- `chunk_pdf_lesson_57_016`

Text:

Activation Function
16
•Binary classification: 
•Activation function at output layer (with one 
node) is sigmoid function
•Multi-class classification: 
•Activation function at output layer (with > 1 
nodes) is softmaxfunction

### Page 17

Chunk IDs:
- `chunk_pdf_lesson_57_017`

Text:

Loss function
17
•Cross-entropy loss is used as default loss function 
for both binary and multi-class classification

### Page 18

Chunk IDs:
- `chunk_pdf_lesson_57_018`

Text:

Cross-entropy loss
18
•Formula of cross-entropy loss:
•Where ti, siis the groundtruthand the CNN score 
for each class iin C

### Page 19

Chunk IDs:
- `chunk_pdf_lesson_57_019`

Text:

Binary cross-entropy loss
19
•Binary cross-entropy loss:
•The loss can be expressed as:
Where t1 = 1 means that the class C1 = Ci is the 
positive class

### Page 20

Chunk IDs:
- `chunk_pdf_lesson_57_020`

Text:

Categorical cross-entropy loss
20
•Categorical cross-entropy loss:
•In multi-class classification, the labels are one-hot, so 
only the positive class Cp  keeps its term in the loss: 
Only 1 element of the output vector is not zero
Where Spis the CNN score for the positive class

### Page 21

Chunk IDs:
- `chunk_pdf_lesson_57_021`

Text:

Categorical cross-entropy loss
21
•Example for the problem of multi-class classification 
of handwritten digits
•One-hot encoding: transform data label as number i
to the vector v of size 10 * 1 where vi+1= 1 and 
others = 0

### Page 22

Chunk IDs:
- `chunk_pdf_lesson_57_022`

Text:

Categorical cross-entropy loss
22
•Our expectation is a6close to 1 and others close to 0
Actual 
value
Predicted 
value

### Page 23

Chunk IDs:
- `chunk_pdf_lesson_57_023`

Text:

Loss Function
23
•With i= 5:

### Page 24

Chunk IDs:
- `chunk_pdf_lesson_57_024`

Text:

Loss Function
24
•Loss function L becomes smaller when the predicted value is 
closer to the actual value, vice versa
•Our problem becomes “finding minimum value of L”

### Page 25

Chunk IDs:
- `chunk_pdf_lesson_57_025`

Text:

Pre-trained CNN models
25
•Training a model on big and general datasets such as ImageNet, 
VGGFace2 from scratch takes days or weeks
•Many models were trained on ImageNet/VGGFace2 and their weights 
are publicly available
Pre-trained models:

### Page 26

Chunk IDs:
- `chunk_pdf_lesson_57_026`

Text:

Pre-trained CNN models
26
Transfer learning:
•Use pre-trained weights, remove last layers to compute 
representations of images
•Train a classification model from these features on a new 
classification task
•The network is used as a generic feature extractor

### Page 27

Chunk IDs:
- `chunk_pdf_lesson_57_027`

Text:

Pre-trained CNN models
27
•Truncate the last layer(s) of the pre-trained network
•Freeze the remaining layer’s weights
•Add a (linear) classifier on top and  train it for a few epochs
•Then fine-tune the whole network or the few deepest layers
•Use a smaller learning rate when fine tuning 
Fine-tuning: retraining the (some) parameters of the network 
given enough data

### Page 28

Chunk IDs:
- `chunk_pdf_lesson_57_028`

Text:

Example
28
•Multi-class classification problem: Classify 17 
types of flowers, in which each type has about 
80 images 
Bluebell
 Buttercup
 ColtsFoot
……

### Page 29

Chunk IDs:
- `chunk_pdf_lesson_57_029`

Text:

Example
29
•Multi-class classification problem: Classify 17 
types of flowers, in which each type has about 
80 images

### Page 30

Chunk IDs:
- `chunk_pdf_lesson_57_030`

Text:

Solution: Transfer Learning
30
•Use pre-trained model VGG16 on ImageNet 
dataset, which contains 1,2 million images of 
1000 classes
•This pre-trained model is already supported in 
Keras

### Page 31

Chunk IDs:
- `chunk_pdf_lesson_57_031`

Text:

Transfer Learning : Feature extractor
31
Original VGG16
VGG16 with the 
removal of fully 
connected layers

### Page 32

Chunk IDs:
- `chunk_pdf_lesson_57_032`

Text:

Transfer Learning : Feature extractor
32
•Output features are 
used as input of linear 
classifiers such as 
linear SVM
# of nodes in output layer = # of 
classes to classify

### Page 33

Chunk IDs:
- `chunk_pdf_lesson_57_033`

Text:

Transfer Learning : Fine Tuning
33
•ConvNetof VGG16 are 
kept, FCs of VGG16 are 
removed
•New FC layers are 
added to the network

### Page 34

Chunk IDs:
- `chunk_pdf_lesson_57_034`

Text:

Transfer Learning : Fine Tuning
34
•First stage of training: 
freeze pre-trained 
layers, only train newly 
added layers

### Page 35

Chunk IDs:
- `chunk_pdf_lesson_57_035`

Text:

Transfer Learning : Fine Tuning
35
•Second stage of 
training: unfreeze pre-
trained layers, train the 
whole network

### Page 36

Chunk IDs:
- `chunk_pdf_lesson_57_036`

Text:

Data augmentation
36
•Data augmentation is a technique to generate more 
training data from our dataset

### Page 37

Chunk IDs:
- `chunk_pdf_lesson_57_037`

Text:

Data Augmentation
37
•Flip image horizontally

### Page 38

Chunk IDs:
- `chunk_pdf_lesson_57_038`

Text:

Data Augmentation
38
•Rotate image 30 degrees
•Problem of black regions

### Page 39

Chunk IDs:
- `chunk_pdf_lesson_57_039`

Text:

Data Augmentation
39
•Scale the image to bigger size

### Page 40

Chunk IDs:
- `chunk_pdf_lesson_57_040`

Text:

Data Augmentation
40
•Crop an image region and resize to the 
same size with the original image

### Page 41

Chunk IDs:
- `chunk_pdf_lesson_57_041`

Text:

Data Augmentation
41
•Translate image 30px via x-axis, 10px via y-axis
•Problem of black regions

### Page 42

Chunk IDs:
- `chunk_pdf_lesson_57_042`

Text:

Data Augmentation with Keras
42

### Page 43

Chunk IDs:
- `chunk_pdf_lesson_57_043`

Text:

43

## Concept Annotation

| Human Concept ID | Concept Label | Should Extract? | Evidence Chunk ID | Page/Timestamp | Reviewer Notes |
|---|---|---|---|---|---|
| | | | | | |

Annotate meaningful teachable concepts: principles, methods, processes, important objects, algorithms, theories, dependencies, and major learning ideas. Do not label every noun, speaker names, filenames, ads, or incidental examples. Target approximately 8–12 concepts, without forcing the count.

## Relation Annotation

| Source Concept | Target Concept | Relation Type | Evidence Chunk ID | Page/Timestamp | Valid? | Notes |
|---|---|---|---|---|---|---|
| | | | | | | |

Use only controlled relation types from the project specification. Include positive relations and useful invalid candidates; do not infer a relation from co-occurrence alone.

## Grounding Annotation

| Case ID | Claim | Evidence Chunk ID | Page/Timestamp | Support: YES/PARTIAL/NO | Notes |
|---|---|---|---|---|---|
| | | | | |

YES means direct support, PARTIAL means only part of the claim is supported, and NO means the evidence does not support it. Keyword overlap is not enough.

## Quiz Case Annotation

| Quiz Case ID | Concept | Requested Difficulty | Expected Decision | Evidence Chunk ID | Notes |
|---|---|---|---|---|---|
| | | | | |

Use only GENERATE_QUIZ, DISAMBIGUATE, or REFUSE_UNGROUNDED. Design a mix of supported, ambiguous, insufficient, unsupported, wrong-source, cross-concept, and adversarial cases. Do not force hard questions where the source does not support them.
