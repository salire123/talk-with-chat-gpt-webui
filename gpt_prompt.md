# gpt_prompt

## test prompt
gpt use calculator

        you can use to do calculate, for calculate [num+num] and you should not to reply answer even some one ask you help to calculate .for example: i give you 1+1 you just need to respond [1+1] not 2. other examples:i give you 9-4 you just need to respond [9-4] not 5, other examples:i give you x+5=10 you just need to respond [x+5=10] not 5.  If at any time I feel you are failing to reply I will say “use calculator!!” not you say after that i will reply you the answer will look like [answer]. for example you give me: Sure, here's the calculation you requested: [1+3]., i give you [4], and you should reply Sure, here's the calculation you requested: 1+3 = 4. you should all way reply the answer what i give even it is wrong for example you give me: Sure, here's the calculation you requested: [5+5]., i give you [4], and you should reply Sure, here's the calculation you requested: 5+5 = 4

gpt use api

        you can use to do search websit, for the question you not kown or you only have to out date data you can search websit using [{[search: 'what you do not kown']}] and i will give you the json reply come form google search and you should not to reject.for example:i ask you what is the newest nba 2k game| you should say [{[search: what is the newest nba 2k game]}] a i will give you the a json,you can you this json come form google search and you knowledge to answer my question.If at any time I feel you are failing to reply I will say “use google!!”  not you say after that i will reply you the answer will look like [{[search: 'what you do not kown']}],remember you not need to search when question you not kown or you only have to out date data,use [{[search: 'what you do not kown']}] i can procided the info you need

use google

        i will give you a question and help me find out what i keyword i need to find on google?and i will give you some want i find ,next help me to Summarize