# Evaluating group fairness in online tutoring rankings

### Bachelor Thesis Universitat Pompeu Fabra
#### Javier Rando Ramírez
#### June 2021

---

Ensuring equal opportunities for everyone is one of the main concerns of modern societies. Machine learning algorithms emerged as a tool to make fair decisions since they should be free from human biases. However, many scandals have shown that this is not the case. In fact, artificial intelligence can reproduce discrimination against groups of people. Given the complexity of the systems and their opacity, it is really important to monitor their results and evaluate potential biases. In this work, we evaluate fairness in search engines retrieving people as results. We focus on online language tutoring platforms where teachers are hired to teach a language. First elements in the ranking will potentially obtain more students. Thus, if some groups are undervalued by the algorithm, they will be less likely to earn income from the platform. Furthermore, we measure how price varies depending on teachers background and attributes. The protected attributes monitored in the analysis are gender and country of origin.

---

⚠️ &nbsp; Released data is anonymized to avoid user identification. Also, output cells containing personal information have been deleted. If you want access to detailed experimental data, feel free to contact me. &nbsp; ⚠️

---

### Contents
This repository contains the whole code used throught my Bachelor Thesis. It is structured in three main sections:
* `data-acquisition/`: Contains the Python scripts used to crawl the information from websites. Notice that sources might be updated and the provided code might be no longer useful.
* `analysis/`: Jupyter Notebooks required to reproduce results.
* `data/`: Anonymized datasets.

Each of the folders contain a README file with further intructions on organization and execution.

Also a PDF version of my Bachelor Thesis can be found in the main folder of this repository.

---

### Ethical considerations
(Extracted from the Thesis. I strongly request that it is respected in any extension of this work.)

We conducted a risk assessment for our work in order to identify the parties that could be harmed. This section discusses ethical considerations, risks, and the implemented mitigation strategies. We identify two main groups to pay attention to: users and platforms.

#### Users

Preserving privacy is the main concern. We believe the risk for teachers is minimal because we use public information anyone can access. However, we infer gender without explicit consent. European legislation with respect to gender is vague and it is not considered sensitive. To preserve privacy and to prevent a person from being offended by the assignment of a certain gender, we release anonymized data that may not lead to identify an individual. As few attributes as possible are released to replicate the results. Moreover, features that might be unique such as price are rounded. Further information about data and transformations is presented in reproducibility Appendix E \[from the Thesis\].

Finally, we think that users' data is analyzed for public interest and any finding in this work will be utilized to their advantage. At no point information has been used for commercial purposes.


#### Platforms

Although web scraping is not always permitted by companies, we think that obtaining information is valuable for public interest. We do it in a responsible way to ensure that it never poses a risk to the availability of their website. Since crawling rules were not specified by platforms themselves, we established conservative waiting times to avoid any type of overload in the servers.
