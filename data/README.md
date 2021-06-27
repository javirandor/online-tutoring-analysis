# Data

This folder contains anonymized data to reproduce results. However, small modifications were made to ensure anonymization. We released two different ranking files:
* `simplified_ranking/`: contain listings with protected attributes and language that can be used for FAIR and statistical analysis. No personal information is provided and price was rounded to the closest multiple of 3 to avoid identification. 
* `modeling_ranking/`: provide the data to train the regressors for position. Since they use more information that can lead to identification, further anonymization was conducted. We provide the transformed dataset that can be used for training because transformation requires sensitive features such as name. Moreover, language is not provided, and price and first letter are scaled.

Finally, `misc/` includes a list with all available languages and the number of teachers for each platform. It is used to sort results by descending average number of teachers.
