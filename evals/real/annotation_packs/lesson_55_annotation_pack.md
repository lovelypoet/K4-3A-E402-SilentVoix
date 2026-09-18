# Annotation Pack — lesson_55

## Lesson metadata

- lesson_id: `lesson_55`
- document_id: `doc_21`
- source type: `document`
- source file/title: `4-Backpropagation.pdf`
- source_group: `file:af003baca65806097f7c614cc422612892df1966ae9a60d24b40790376f02fe8`
- chunk count: `22`
- page count OR duration: `22 pages`

## Source overview

**AI-GENERATED ORIENTATION SUMMARY — NOT GROUND TRUTH**

Backpropagation Introduction to Deep Learning XOR problem 2 x1 XOR x2

## Source sections

### Page 1

Chunk IDs:
- `chunk_pdf_lesson_55_001`

Text:

Backpropagation
Introduction to Deep Learning

### Page 2

Chunk IDs:
- `chunk_pdf_lesson_55_002`

Text:

XOR problem
2
x1 XOR x2

### Page 3

Chunk IDs:
- `chunk_pdf_lesson_55_003`

Text:

Neural Network Model for XOR
3
Neural Network Model for XOR problem

### Page 4

Chunk IDs:
- `chunk_pdf_lesson_55_004`

Text:

Neural Network Model for XOR
4
Neural Network for XOR problem:
•Model: 2-2-1: 2 nodes in input layer, 2 nodes in hidden 
layers, 1 node in output layer
•Nodes 1 are added to calculate bias in next layers
•Each node in hidden layers and output layer are 
performed two steps: 
 (1) Linear sum
 (2) Apply activation function

### Page 5

Chunk IDs:
- `chunk_pdf_lesson_55_005`

Text:

Feedforward
5

### Page 6

Chunk IDs:
- `chunk_pdf_lesson_55_006`

Text:

In Matrix form
6

### Page 7

Chunk IDs:
- `chunk_pdf_lesson_55_007`

Text:

In Matrix form
7

### Page 8

Chunk IDs:
- `chunk_pdf_lesson_55_008`

Text:

Loss Function
8
For each data point (x[i], yi), the loss function L is 
defined as follows:
In which: yi is the actual value of data, !𝑦𝑖  is the 
value predicted by the model:

### Page 9

Chunk IDs:
- `chunk_pdf_lesson_55_009`

Text:

Loss Function
9
For all data points, the loss function J is defined 
as follows:

### Page 10

Chunk IDs:
- `chunk_pdf_lesson_55_010`

Text:

Gradient Descent
10
•To apply gradient descent, we need to calculate the 
derivative of the coefficient W and bias b of the loss 
function: 
•Step 1, calculate L’ with W(2), b(2)  ,we have:  
In which:

### Page 11

Chunk IDs:
- `chunk_pdf_lesson_55_011`

Text:

Gradient Descent
11
Chain rule for node 1 layer 2

### Page 12

Chunk IDs:
- `chunk_pdf_lesson_55_012`

Text:

Gradient Descent
12
From the chain rule, we have:

### Page 13

Chunk IDs:
- `chunk_pdf_lesson_55_013`

Text:

Gradient Descent
13
From the chain rule, we have:

### Page 14

Chunk IDs:
- `chunk_pdf_lesson_55_014`

Text:

Gradient Descent
14
Similarly, we have:

### Page 15

Chunk IDs:
- `chunk_pdf_lesson_55_015`

Text:

Gradient Descent
15
Step 2, calculate L’ with W(1), b(1) , since:
Apply chain rule, we have:

### Page 16

Chunk IDs:
- `chunk_pdf_lesson_55_016`

Text:

Gradient Descent
16
We have: 
Therefore:

### Page 17

Chunk IDs:
- `chunk_pdf_lesson_55_017`

Text:

Gradient Descent
17
We have: 
Therefore:

### Page 18

Chunk IDs:
- `chunk_pdf_lesson_55_018`

Text:

Gradient Descent
18
Similarly:

### Page 19

Chunk IDs:
- `chunk_pdf_lesson_55_019`

Text:

Gradient Descent
19

### Page 20

Chunk IDs:
- `chunk_pdf_lesson_55_020`

Text:

General Model
20

### Page 21

Chunk IDs:
- `chunk_pdf_lesson_55_021`

Text:

General Model
21
Feedforward process
Backpropagation process

### Page 22

Chunk IDs:
- `chunk_pdf_lesson_55_022`

Text:

22

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
