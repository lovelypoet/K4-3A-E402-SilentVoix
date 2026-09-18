# New Files Processing Report

Exact local source identity uses `file:<sha256>`. The two video records were initially registered as `TRANSCRIPTION_REQUIRED`, then successfully reprocessed with Whisper `small` on CPU.

| File | Type | Duplicate? | Processing Path | Chunks | Metadata | Status | Notes |
|---|---|---:|---|---:|---|---|---|
| 3-Neural_Network.pdf | pdf | NO | pypdf digital-text extraction | 26 | document_id, lesson_id, source_key, source_group, page | READY | Digital text |
| 4-Backpropagation.pdf | pdf | NO | pypdf digital-text extraction | 22 | document_id, lesson_id, source_key, source_group, page | READY | Digital text |
| 5-Convolutional_Neural_Network.pdf | pdf | NO | pypdf digital-text extraction | 43 | document_id, lesson_id, source_key, source_group, page | READY | Digital text |
| 6-CNN_for_Image_Classification.pdf | pdf | NO | pypdf digital-text extraction | 43 | document_id, lesson_id, source_key, source_group, page | READY | Digital text |
| 7-Object_Detection_and_Image_Segmentation.pdf | pdf | NO | pypdf digital-text extraction | 58 | document_id, lesson_id, source_key, source_group, page | READY | Digital text |
| YTSave_YouTube_Deep-Learning-What-is-Deep-Learning-Deep_Media_6M5VXKLf4D4_003_480p.mp4 | mp4 | NO | faster-whisper `small`, CPU | 82 | document_id, lesson_id, source_key, source_group, timestamps | READY | Duration 410.0 seconds |
| YTSave_YouTube_Machine-Learning-Tutorial-Machine-Learni_Media_G7fPB4OHkys_003_480p.mp4 | mp4 | NO | faster-whisper `small`, CPU | 735 | document_id, lesson_id, source_key, source_group, timestamps | READY | Duration 2094.25 seconds |

No duplicate lesson was created for either file. Human labels were not generated automatically.
