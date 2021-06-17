# Evaluating group fairness in online tutoring rankings

### Bachelor Thesis Universitat Pompeu Fabra
#### Javier Rando Ramírez
#### June 2021

---

Ensuring equal opportunities for everyone is one of the main concerns of modern societies. Machine learning algorithms emerged as a tool to make fair decisions since they should be free from human biases. However, many scandals have shown that this is not the case. In fact, artificial intelligence can reproduce discrimination against groups of people. Given the complexity of the systems and their opacity, it is really important to monitor their results and evaluate potential biases. In this work, we evaluate fairness in search engines retrieving people as results. We focus on online language tutoring platforms where teachers are hired to teach a language. First elements in the ranking will potentially obtain more students. Thus, if some groups are undervalued by the algorithm, they will be less likely to earn income from the platform. Furthermore, we measure how price varies depending on teachers background and attributes. The protected attributes monitored in the analysis are gender and country of origin.

---

⚠️ &nbsp; Data is not provided because it includes personal information about users. Also, output cells containing information have been deleted. If you want access, feel free to contact me. &nbsp; ⚠️

---

## Contents
This repository contains the whole code used throught my Bachelor Thesis. It is structured in two main sections:
* `crawling/`: scripts used to retrieve data from sources and transformation. They are Python scripts that can be executed through an IDE or command line.
* `analysis/`: notebooks to conduct experiments and analysis.
