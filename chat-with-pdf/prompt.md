# Profiling

```
            
2025-06-25 09:49:51,234 - INFO - Starting upload_pdf function for file: Chapter01.pdf
2025-06-25 09:49:51,235 - INFO - Successfully uploaded PDF: Chapter01.pdf
2025-06-25 09:49:51,235 - INFO - Completed upload_pdf function for file: Chapter01.pdf
2025-06-25 09:49:51,235 - INFO - Starting load_pdf function for file: pdfs/Chapter01.pdf
2025-06-25 09:49:53,342 - INFO - Successfully loaded PDF with 24 pages: pdfs/Chapter01.pdf
2025-06-25 09:49:53,342 - INFO - Completed load_pdf function for file: pdfs/Chapter01.pdf
2025-06-25 09:49:53,342 - INFO - Starting split_text function for 24 documents
2025-06-25 09:49:53,343 - INFO - Successfully split documents into 78 chunks
2025-06-25 09:49:53,343 - INFO - Completed split_text function
2025-06-25 09:49:53,343 - INFO - Starting index_docs function for 78 documents
2025-06-25 09:50:27,431 - INFO - HTTP Request: POST http://127.0.0.1:11434/api/embed "HTTP/1.1 200 OK"
2025-06-25 09:50:27,475 - INFO - Successfully indexed 78 documents to vector store
2025-06-25 09:50:27,475 - INFO - Completed index_docs function
2025-06-25 09:50:40,382 - INFO - Starting upload_pdf function for file: Chapter01.pdf
2025-06-25 09:50:40,383 - INFO - Successfully uploaded PDF: Chapter01.pdf
2025-06-25 09:50:40,383 - INFO - Completed upload_pdf function for file: Chapter01.pdf
2025-06-25 09:50:40,383 - INFO - Starting load_pdf function for file: pdfs/Chapter01.pdf
2025-06-25 09:50:42,405 - INFO - Successfully loaded PDF with 24 pages: pdfs/Chapter01.pdf
2025-06-25 09:50:42,406 - INFO - Completed load_pdf function for file: pdfs/Chapter01.pdf
2025-06-25 09:50:42,406 - INFO - Starting split_text function for 24 documents
2025-06-25 09:50:42,407 - INFO - Successfully split documents into 78 chunks
2025-06-25 09:50:42,407 - INFO - Completed split_text function
2025-06-25 09:50:42,407 - INFO - Starting index_docs function for 78 documents
2025-06-25 09:51:15,255 - INFO - HTTP Request: POST http://127.0.0.1:11434/api/embed "HTTP/1.1 200 OK"
2025-06-25 09:51:15,296 - INFO - Successfully indexed 78 documents to vector store
2025-06-25 09:51:15,296 - INFO - Completed index_docs function
2025-06-25 09:51:15,297 - INFO - Starting retrieve_docs function for query: compare C++ and Java ...
2025-06-25 09:51:15,395 - INFO - HTTP Request: POST http://127.0.0.1:11434/api/embed "HTTP/1.1 200 OK"
2025-06-25 09:51:15,406 - INFO - Successfully retrieved 4 documents for query
2025-06-25 09:51:15,406 - INFO - Completed retrieve_docs function
2025-06-25 09:51:15,406 - INFO - Starting answer_question function for question: compare C++ and Java ...
2025-06-25 09:51:15,406 - INFO - Generated context from 4 documents
2025-06-25 09:51:16,754 - INFO - HTTP Request: POST http://127.0.0.1:11434/api/generate "HTTP/1.1 200 OK"
2025-06-25 09:51:24,744 - INFO - Successfully generated answer
2025-06-25 09:51:24,744 - INFO - Completed answer_question function
2025-06-25 09:51:59,927 - INFO - Starting upload_pdf function for file: Chapter01.pdf
2025-06-25 09:51:59,927 - INFO - Successfully uploaded PDF: Chapter01.pdf
2025-06-25 09:51:59,928 - INFO - Completed upload_pdf function for file: Chapter01.pdf
2025-06-25 09:51:59,928 - INFO - Starting load_pdf function for file: pdfs/Chapter01.pdf
2025-06-25 09:52:01,956 - INFO - Successfully loaded PDF with 24 pages: pdfs/Chapter01.pdf
2025-06-25 09:52:01,956 - INFO - Completed load_pdf function for file: pdfs/Chapter01.pdf
2025-06-25 09:52:01,956 - INFO - Starting split_text function for 24 documents
2025-06-25 09:52:01,957 - INFO - Successfully split documents into 78 chunks
2025-06-25 09:52:01,957 - INFO - Completed split_text function
2025-06-25 09:52:01,957 - INFO - Starting index_docs function for 78 documents
2025-06-25 09:52:57,886 - INFO - HTTP Request: POST http://127.0.0.1:11434/api/embed "HTTP/1.1 200 OK"
2025-06-25 09:52:57,918 - INFO - Successfully indexed 78 documents to vector store
2025-06-25 09:52:57,918 - INFO - Completed index_docs function
2025-06-25 09:52:57,918 - INFO - Starting retrieve_docs function for query: How Java Impacted the Internet?...
2025-06-25 09:52:58,064 - INFO - HTTP Request: POST http://127.0.0.1:11434/api/embed "HTTP/1.1 200 OK"
2025-06-25 09:52:58,074 - INFO - Successfully retrieved 4 documents for query
2025-06-25 09:52:58,074 - INFO - Completed retrieve_docs function
2025-06-25 09:52:58,074 - INFO - Starting answer_question function for question: How Java Impacted the Internet?...
2025-06-25 09:52:58,074 - INFO - Generated context from 4 documents
2025-06-25 09:53:00,051 - INFO - HTTP Request: POST http://127.0.0.1:11434/api/generate "HTTP/1.1 200 OK"
2025-06-25 09:53:22,689 - INFO - Successfully generated answer
2025-06-25 09:53:22,690 - INFO - Completed answer_question function

```

save to `PROFILE.md` the run time of each function

# More features 

1. Session State Management
Add persistence for chat history and uploaded documents:

2. Enhanced Chat Interface
Display conversation history and add clear chat functionality:

3. PDF Information Panel
Add a sidebar with document details:

4. Source Citations
Show which parts of the document were used:

7. Error Handling & User Feedback Add better error messages and validation:

8. Sample Questions
Add suggested questions to help users get started:

9.Export Functionality Allow users to export chat history:

# Implement Python logger

For each functions below 
- def upload_pdf(file):
- def load_pdf(file_path):
- def split_text(documents):
- def index_docs(documents):
- def retrieve_docs(query):
- def answer_question(question, documents):

print log messages, including timestamp at the start and end of each function, and log any exceptions that occur.


