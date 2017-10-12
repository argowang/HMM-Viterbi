Name: Junyi Wang

------------------------------
WordIntoRare.py

This file includes the implementation of the function to calculate emission parameter and the function to change rare frequency words into _RARE_

HOW TO RUN THE CODE
When hw4_1.py is executed, it will automatically take ./ner_train.dat as input and take ./ner_train.dat.rare_processed as output. It does not require the ner_train.dat.rare_processed to be existed. If the file does not exist, the script will generate a file with this name. Therefore, to get 4_1.txt, the grader will need to run the count_freqs.py on ner_train.dat.rare_processed.

The emission parameter calculation function when called will not return a specific value, instead, it will return a dict contains all emission parameters. The dictionary was designed to have the following structure: (word, label) -> emission parameter. Therefore, if you want to get the emission parameter of a specifc pair, you could do the following:
e_dict = emission_parameter(ner_count)
print e_dict[(word, label)]
The time complexity for this function is linear and the time complexity of retreive particular emission parameter is O(1). 

The idea behind into_rare function is simple. Traverse the data and use a dict to keep the count of each word. Then do another traversal and change the word with frequency < 5 into _RARE_

------------------------------
naivePredict.py

This file again includes the implementation of the function to calculate emission parameter and the function to predict the label of a given word.

HOW TO RUN THE CODE
When hw4_2.py is executed, it will automatically take ./4_1.txt, ./ner_dev.dat as input and ./4_2.txt as output. It is ok if ./4_2.txt does not exist before. The script will generate it automatically. Notice the file requires the 4_1.txt to work and to get 4_1.txt, the grader needs to run count_freqs.py on ner_train.dat.rare_processed

PERFORMANCE
after running eval_ne_tagger.py ner_dev.key 4_2.txt
we get the following output

Found 14043 NEs. Expected 5931 NEs; Correct: 3117.

	 precision 	recall 		F1-Score
Total:	 0.221961	0.525544	0.312106
PER:	 0.435451	0.231230	0.302061
ORG:	 0.475936	0.399103	0.434146
LOC:	 0.147750	0.870229	0.252612
MISC:	 0.491689	0.610206	0.544574

OBSERVATION AND COMMENTS
1. For all same word w, we always get the same label l. We cannot find another lable l' such that e(w,l') > e(w,l)
2. The precission of this baseline algorithm is pretty low.
3. When comparing our prediction with ner_dev.key, I observe that many incorrect prediction has a relatively large log(e) (or, the absolute value of its log(e) is relatively small). Those correct predictions tend to have small log(e) value (or, the absolute value of its log(e) is large)
4. Words that do not exist in 4_1.txt or have low frequency always get the B-LOC prediction, which will maximize the emission parameter

------------------------------
trigramCal.py

This file implements a function that given a trigram input, will print out the log probability of trigram.

HOW TO RUN THE CODE
When hw5_1.py is executed, it will automatically take 4_1.txt and trigrams.txt as inputs. The output is printed out to the terminal.

The idea behind hw5_1.py is similar to calculating emission parameter. I record all the counts of trigrams and bigrams, then use the formula to calculate the probability. The probability is stored in a dictionary.

------------------------------
Viterbi.py
This file implements the viterbi algorithm

HOW TO RUN THE CODE
When hw5_2.py is executed, it will automatically take 4_1.txt as training file and ner_dev.dat as the file to work on, the output will be directed to 5_2.txt. If 5_2.txt did not exist, the script will generate it automatically.

The idea behind the code, I basically follow the pseudocode taught in the lecture, create dict for pi and bp, and store the values into the dict. 

PERFORMANCE
after running eval_ne_tagger.py ner_dev.key 5_2.txt
we get the following output

Found 4647 NEs. Expected 5931 NEs; Correct: 3657.

	 precision 	recall 		F1-Score
Total:	 0.786959	0.616591	0.691435
PER:	 0.744311	0.605005	0.667467
ORG:	 0.659729	0.473842	0.551544
LOC:	 0.895994	0.695202	0.782929
MISC:	 0.827048	0.690554	0.752663

OBSERVATION:
1. When compared with the result of baseline method, we can see the precision increases tremendously in every category.
2. The algorithm takes longer time (but still acceptable) to run, mainly because now we have O(nK^3) time complexity, while we have linear before. 
3. The viterbi algorithm does very well in LOC, while the baseline has the worst performance in LOC.


------------------------------
ImprovedViterbi.py

This file first divides the words into different meaningful categories. Then rerun the viterbi algorithm.

HOW TO RUN THE CODE:
After hw6.py is called, the program will
1. automatically take ner_train.dat as input and change rare words into corresponding categories. The output of 
this step is a middle file named ner_train.dat.categorized.
2. use in-python exec call to run count_freqs.py on ner_train.dat.categorized. The output of this step is 6_input
3. take 6_input as training file, ner_dev.dat as input to be worked on. The prediction result is dumped into 6.txt

I chose the following patterns:
All capital words
All lowercase rare words
Pure numbers
Small number with . e.g. 0.42
Large number with , e.g. 10,000
Number with dashes(date) e.g. 1995-08-01
Capital words with period(s) U.S.
Initial capital
All other words are categorized as _RARE_

PERFORMANCE
After running eval_ne_tagger.py on 6.txt and ner_dev.key, we get the following result

Found 5794 NEs. Expected 5931 NEs; Correct: 4312.

	 precision 	recall 		F1-Score
Total:	 0.744218	0.727027	0.735522
PER:	 0.819468	0.787813	0.803329
ORG:	 0.529880	0.695815	0.601616
LOC:	 0.866622	0.712105	0.781802
MISC:	 0.821756	0.680782	0.744656

OBSERVATIONS
As we can see, the performance is increased tremendously in many dimensions. 
1. The total correct number increases by 18%. 
2. Performance in PER increases significantly.
3. Almost all categories' F1-score increases (except MISC)
4. Total precision drops a little, but the recall and F1-score increase significantly
5. Performance in MISC category is worsened by a little. 

DISCUSSION
Overall, the performance is improved by grouping the low-frequency words based on informative patterns, rather than just into a single class rare. The instinct behind is that, words with similar patterns are more likely to have the same type. For example, all capital words are more likely to be organizations. Words with capital intial such as London, Beijing are more likely to be Location. But before, they are all treated the same. Therefore, this method improves the performance. 