# Annotation Pack — lesson_05

## Lesson metadata

- lesson_id: `lesson_05`
- document_id: `doc_20`
- source type: `document`
- source file/title: `3-Neural_Network.pdf`
- source_group: `file:671f536b2582035bff08c654a2beeb6d235f3af252cbf7f14080eb222c425042`
- chunk count: `26`
- page count OR duration: `26 pages`

## Source overview

**AI-GENERATED ORIENTATION SUMMARY — NOT GROUND TRUTH**

Neural Network Introduction to Deep Learning Simple Neural Network Model •Logistic regression model: 2 •Two steps: (1) Linear sum: (2) Apply sigmoid function:

## Source sections

### Page 1

Chunk IDs:
- `chunk_pdf_lesson_05_001`

Text:

Neural Network
Introduction to Deep Learning

### Page 2

Chunk IDs:
- `chunk_pdf_lesson_05_002`

Text:

Simple Neural Network Model
•Logistic regression model:
2
•Two steps:
(1) Linear sum:
(2) Apply sigmoid function:

### Page 3

Chunk IDs:
- `chunk_pdf_lesson_05_003`

Text:

Simple Neural Network Model
3
Flow chat of logistic regression model

### Page 4

Chunk IDs:
- `chunk_pdf_lesson_05_004`

Text:

Simple Neural Network Model
4
Flow chat of logistic regression model
•W0 is called bias coefficient, or free coefficient
•Sigmoid function is called activation function

### Page 5

Chunk IDs:
- `chunk_pdf_lesson_05_005`

Text:

General Neural Network Model
5
•Input layer and output 
layer are required
•Hidden layers are 
optional
•Total layers = # layers – 1
•Each circle is called one 
node

### Page 6

Chunk IDs:
- `chunk_pdf_lesson_05_006`

Text:

General Neural Network Model
6
Each node in hidden layer and output layer:
•Is connected with all nodes with previous layer with the coefficents w
•Has a bias coefficient w0
•Follows two steps of linear sum and appliance of activation function (sigmoid)

### Page 7

Chunk IDs:
- `chunk_pdf_lesson_05_007`

Text:

General Neural Network Model
7
The neural network has: 3 layers, 2 nodes in input layer, 3 nodes in 
hidden layer 1, 3 nodes in hidden layer 2, 1 node in output layer

### Page 8

Chunk IDs:
- `chunk_pdf_lesson_05_008`

Text:

General Neural Network Model
8
Note: node 1 is not considered as a node since it is used to calculate 
bias of the node in the next layer

### Page 9

Chunk IDs:
- `chunk_pdf_lesson_05_009`

Text:

General Neural Network Model
9
•Node i in layer l with bias bi(l) has 2 steps: 
(1) Linear sum: 
(2) Apply activation function:

### Page 10

Chunk IDs:
- `chunk_pdf_lesson_05_010`

Text:

General Neural Network Model
10
•At node 2 of layer 1, we have:  
•At node 3 of layer 2, we have:

### Page 11

Chunk IDs:
- `chunk_pdf_lesson_05_011`

Text:

Feedforward
11
•Let call input layer x = a(0), with size 2*1, we have:

### Page 12

Chunk IDs:
- `chunk_pdf_lesson_05_012`

Text:

Feedforward
12
•Similarly, we have:

### Page 13

Chunk IDs:
- `chunk_pdf_lesson_05_013`

Text:

Feedforward
13
feedforward neural network

### Page 14

Chunk IDs:
- `chunk_pdf_lesson_05_014`

Text:

Loss function
14
•Gradient descent algorithm
•Step of derivative calculation of 
coefficients of loss function is done with 
the backpropagation algorithm  
à Will be taught in the next lecture

### Page 15

Chunk IDs:
- `chunk_pdf_lesson_05_015`

Text:

Logistic Regression vs. Neural Network
15
x1 AND x2
Problem: AND

### Page 16

Chunk IDs:
- `chunk_pdf_lesson_05_016`

Text:

Logistic Regression vs. Neural Network
16
Flow chart for the problem x1 AND x2

### Page 17

Chunk IDs:
- `chunk_pdf_lesson_05_017`

Text:

Logistic Regression vs. Neural Network
17
Flow chart for the problem NOT (x1 AND x2)

### Page 18

Chunk IDs:
- `chunk_pdf_lesson_05_018`

Text:

Logistic Regression vs. Neural Network
18
Separation line y = 1.5 - 1 * x1 - 1 * w2

### Page 19

Chunk IDs:
- `chunk_pdf_lesson_05_019`

Text:

Logistic Regression vs. Neural Network
19
x1 OR x2
Problem: OR

### Page 20

Chunk IDs:
- `chunk_pdf_lesson_05_020`

Text:

Logistic Regression vs. Neural Network
20
Flow chart for the problem x1 OR x2

### Page 21

Chunk IDs:
- `chunk_pdf_lesson_05_021`

Text:

Logistic Regression vs. Neural Network
21
Separation line for OR problem

### Page 22

Chunk IDs:
- `chunk_pdf_lesson_05_022`

Text:

Logistic Regression vs. Neural Network
22
x1 XOR x2
Problem: XOR

### Page 23

Chunk IDs:
- `chunk_pdf_lesson_05_023`

Text:

Logistic Regression vs. Neural Network
23
Cannot draw a separation line for XOR problem
àCannot solve the XOR problem using logistic regression
à Neural network ???

### Page 24

Chunk IDs:
- `chunk_pdf_lesson_05_024`

Text:

Logistic Regression vs. Neural Network
24
Rewrite XOR problem:

### Page 25

Chunk IDs:
- `chunk_pdf_lesson_05_025`

Text:

Logistic Regression vs. Neural Network
25
Solve XOR problem with several logistic regression models

### Page 26

Chunk IDs:
- `chunk_pdf_lesson_05_026`

Text:

26

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
