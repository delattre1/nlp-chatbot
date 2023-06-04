# Essay 3

To create the threasholds and filter unsafe content, I used a kaggle tweets datased used for sentiment analysis. 

I trained a Logistic Regression model, with a CountVectorizer, that receives a text string, and classify it in Positive / Negative content.
Then I exported both trained model and the CountVectorizer to a file, so I can re-use them. 

Everytime a ```!crawl``` command is runned (and new pages are collected), the script send the entire text content from each page to the model.
Then the result of the model is normalized to be in the range of (-1, 1) (where 1 is the most positive sentiment), and the sentiment is store in a dict, 
Where the Key is the website URL, and the value is the sentiment analysis result. 

With that, everytime a !search / !wn_search is runned with the th (threshold) argument, the script uses the stored dict to filter only websites that have the sentiment (result > threshold)

# Essays links related to each project phase
### [README](../README.md)
### [Essay 00](./essay_0.md)
### [Essay 01](./essay_1.md)
### [Essay 02](./essay_2.md)
### [Essay 04](./essay_4.md)
### [Essay 05](./essay_5.md)