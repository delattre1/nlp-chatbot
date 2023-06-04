# Essay 2
First, I created the infrastructure for storing the crawled pages, using Minio (just like AWS S3, but local). 

Then I developed the functionality that receives one URL, get all the href links to other pages, and download the content from these pages. This is configured to run recursively with 2 levels of depth.

To develop search and wn_search I re-used the content from the classes.

And, everytime a new ```!crawl``` is runned, a new reverse_index is created.

# Essays links related to each project phase
### [README](../README.md)
### [Essay 00](./essay_0.md)
### [Essay 01](./essay_1.md)
### [Essay 03](./essay_3.md)
### [Essay 04](./essay_4.md)
### [Essay 05](./essay_5.md)