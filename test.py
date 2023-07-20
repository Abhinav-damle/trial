from flask import Flask, render_template, request, jsonify,make_response
#from chatterbot import ChatBot
#from chatterbot.trainers import ChatterBotCorpusTrainer
#from duckduckpy import query
from spellchecker import SpellChecker
import summarizer as AbhishekSummarizer
import wikipedia
import aiml
import urllib
#from duckduckpy import query
import ast,json
import re
import operator
from difflib import SequenceMatcher
import sqlite3
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from nltk.tokenize import sent_tokenize




#from aaaa.py import  nsa

app = Flask(__name__)

mybot = aiml.Kernel()
mybot.setBotPredicate("name","searchbot")

mybot.learn('search.aiml')

search_flag=0#This search_flag is set when first search takes place
spell_flag=0#This flag is set when there is spelling mistake

option_flag=0#this flag is set when we choose any options from the list of topics provided
newSpell=""#this is to store the new spelling 

newWord=''#this is store the typed option 
moreinfo_dictionary={}#this is store results of more info
append_summary=[]#this is used to append summary
results=[]#this is store list of options that wikipedia provides.
titles=[]#this is a 2d list which we extract from wikipedia content using regualr expression
moreresults_count=0#this is to count number of more results
i=0#To itirate through the results
numberChosen=0#to store user selected number
words=[]#to store query or search word
matchedItem=""#variable to store matched text
information_flag=0#this flag is set when we have search from information box side
matchedMoreinfo=""#variable to store matched text
newUserId=0#user to store in db
userText=""#text entered by rhe user
search_id=0#search id to store in db
displayWord=""

###################################################################################Functions Necessary###########################################################################

def spelling(word):  # function to correct spelling

    spell = SpellChecker()
    w = word.split(" ")
    misspelled = spell.unknown(w)
    if len(misspelled):
        for word1 in misspelled:
            pass
        w = word.replace(','.join(str(s) for s in misspelled), str(spell.correction(word1)))
        return (w)


'''def handleAmbiguity(userText,summary2):#function to handle ambiguity
				global res
				global i
				global ut
				i=0
				d1=[]
				ut=int(userText)
				res=wikipedia.search(li[ut])
				#checkForDisambon(res)
				#lis=wikipedia.search(res[0], results=10)
				results=wikipedia.search(li[ut], results=10)
				s=summaryFunction(results,summary2)
				return s'''


def fullSummary(userText):  # function to get full summary
    global results
    global option_flag
    global numberChosen
    global newWord
    option_flag = 1
    if userText.isdigit():#for numeric option
        numberChosen = int(userText)
        append_summary2 = []
        try:
            informationSummary = wikipedia.summary(results[numberChosen], sentences=5)
            informationSummary = informationSummary.replace('\r\n', '\n').replace('\r', '\n')
            informationSummary = informationSummary.replace('=', '')
            informationSummary = re.sub('\|\s+(.+)\.svg', "", informationSummary)
            append_summary2.append(informationSummary)
            append_summary2.append("<br>")
        except wikipedia.exceptions.DisambiguationError as e:
            append_summary2.append("n")
        except IndexError:
            append_summary2.append("n")
        except wikipedia.exceptions.PageError:
            append_summary2.append("n")
        except KeyError:
            #source = ('<img src="{}" width="102px" height="102px"/>').format("/static/user.png")
            append_summary2.append("n")
    else:#for text option
        append_summary2 = []
        newWord = userText
        try:
            informationSummary = wikipedia.summary(newWord, sentences=5)
            informationSummary = informationSummary.replace('\r\n', '\n').replace('\r', '\n')
            informationSummary = informationSummary.replace('=', '')
            informationSummary = re.sub('\|\s+(.+)\.svg', "", informationSummary)
            append_summary2.append(informationSummary)
            append_summary2.append("<br>")
        except wikipedia.exceptions.DisambiguationError as e:
            lis = e.options
            informationSummary = wikipedia.summary(lis[0], sentences=5)
            informationSummary = informationSummary.replace('\r\n', '\n').replace('\r', '\n')
            informationSummary = informationSummary.replace('=', '')
            informationSummary = re.sub('\|\s+(.+)\.svg', "", informationSummary)
            append_summary2.append(informationSummary)
            append_summary2.append("n")
        except  KeyError:
            #source = ('<img src="{}" width="102px" height="102px"/>').format("/static/user.png")
            append_summary2.append("")
    return append_summary2

def summaryFunction_traditional():  # function to get summary
    global results
    global append_summary
    informationSummary = []
    append_summary = []
    s = ''
    #print(results)
    for i in range(0, 5):
        try:
            #chatSummary.append((' {} : {} ').format(i, wikipedia.page(results[i]).title))
            informationSummary = wikipedia.summary(results[i], sentences=4).strip()
            informationSummary = informationSummary.replace('\r\n', '\n').replace('\r', '\n')
            informationSummary = re.sub('\n+', "\n", informationSummary).replace('\n', '\n\n')
            informationSummary = re.sub('\|\s+(.+)\.svg', "", informationSummary)
            keyWord=results[i]
            keyWord=keyWord.replace(' ','%20')
            img=wikipedia.page(results[i])
            source = ('<i><a href=full_doc_traditional/search_word="{}" target="_blank">Link</a></i>').format(keyWord)
            image = ('<img src="{}" width="102px" height="102px"/>').format(img.images[0])
            html_text = '<b>{}</b><br>{}<br>{}<br>\n\n{}<br><br>'.format(wikipedia.page(results[i]).title,image,source,informationSummary)
            append_summary.append(html_text)
            print(append_summary)
        except IndexError:
            s = '{"a" : "sorry no more information is available","b" :"n", "c" : displayWord}'
            return s
        except wikipedia.exceptions.PageError:
            html_text =("<i>no entry found for {}</i>").format(results[i])
        except wikipedia.exceptions.DisambiguationError as e:
            continue
        except  KeyError:
            #source = ('<img src="{}" width="102px" height="102px"/>').format("/static/user.png")
            continue
            # exception_text = str(e).strip().replace("\n", "\n")
            # html_text = "<i>{}</i>".format(exception_text)
    if len(results[i]) == 0:
        s = '{"a" : "sorry no information is available", "b" :"n", "c" : words[1]}'
    elif append_summary:
            s = '{"a" : chatSummary, "b" : append_summary, "c" : displayWord}'
    return s
	
def sendLink(chatSummary):
    global i
    global append_summary
    global words
    global newSpell
    global results
    global information_flag
    global displayWord
    global userText
    global spell_flag
    print(i)
    j = i - 3
    s = ''
    for k in range(j,i):
        try:
            keyWord=results[k]
            keyWord=keyWord.replace(' ','%20')
            source = ('<i><a href=full_doc/search_word="{}" target="_blank">Link</a></i>').format(keyWord)
            chatSummary.append((' {} : {} - {}').format(k, wikipedia.page(results[k]).title,source))
        except IndexError:
            #print("1")
            s = '{"a" : "sorry no more information is available","b" :"n", "c" : displayWord}'
            return s
        except wikipedia.exceptions.PageError:
            html_text =("<i>no entry found for {}</i>").format(results[k])
        except wikipedia.exceptions.DisambiguationError as e:
            continue
        except  KeyError:
            #source = ('<img src="{}" width="102px" height="102px"/>').format("/static/user.png")
            continue
            # exception_text = str(e).strip().replace("\n", "\n")
            # html_text = "<i>{}</i>".format(exception_text)
    if len(results[i]) == 0:
        search_flag = 0
        #print("2")
        s = '{"a" : "sorry no information is available", "b" :"n", "c" : words[1]}'
    elif(spell_flag):
            s = '{"a" : chatSummary, "b" : "", "c" : newSpell}'
    else:
            s = '{"a" : chatSummary, "b" : "", "c" : displayWord}'

    return s
	
def summaryFunction(chatSummary):  # function to get summary
    global i
    global append_summary
    global words
    global newSpell
    global results
    global information_flag
    global displayWord
    global userText
    global spell_flag
    informationSummary = []
    append_summary = []
    j = i + 3
    s = ''
    print(results)
    for i in range(i, j):
        try:
            img=wikipedia.page(results[i])
            chatSummary.append((' <br>{} : {}&nbsp&nbsp<img src="{}" width="52px" height="52px"/> ').format(i, wikipedia.page(results[i]).title,img.images[0]))
            informationSummary = wikipedia.summary(results[i], sentences=2).strip()
            informationSummary = informationSummary.replace('\r\n', '\n').replace('\r', '\n')
            informationSummary = re.sub('\n+', "\n", informationSummary).replace('\n', '\n\n')
            informationSummary = re.sub('\|\s+(.+)\.svg', "", informationSummary)
            keyWord=results[i]
            keyWord=keyWord.replace(' ','%20')
            source = ('<img src="{}" width="102px" height="102px"/>').format(img.images[0])
            html_text = '<b>{}</b><br><br>\n\n{}<br>\n\n{}<br><br>'.format(wikipedia.page(results[i]).title, source,
                                                                   informationSummary)
            append_summary.append(html_text)
            #print(i)
        except IndexError:
            if (len(append_summary)>0):
                                       continue
            else:
                 s = '{"a" : "sorry no more information is available","b" :"", "c" : displayWord}'
                 return s
        except wikipedia.exceptions.PageError:
            html_text =("<i>no entry found for {}</i>").format(results[i])
        except wikipedia.exceptions.DisambiguationError as e:
            continue
            # exception_text = str(e).strip().replace("\n", "\n")
            # html_text = "<i>{}</i>".format(exception_text)
        except  KeyError:
            #source = ('<img src="{}" width="102px" height="102px"/>').format("/static/user.png")
            continue
			
    if len(results[i-3]) == 0:
        search_flag = 0
        print("2")
        s = '{"a" : "sorry no information is available", "b" :"n", "c" : words[1]}'
    elif append_summary:
        # print(newSpell)
		#print(i)
        i += 1# chatSummary.append(' or type "more results" to get more results.')
        #print(i)
        if (spell_flag):
            s = '{"a" : chatSummary, "b" : append_summary, "c" : newSpell}'
        else:
            s = '{"a" : chatSummary, "b" : append_summary, "c" : displayWord}'
        # conn=create_connection()
        # chatInformation=(str(userText),str(chatSummary),str(append_summary),newUserId)
        # store_chat(conn,chatInformation)
        # conn.commit()
        #i += 1
    return s


def getResults(word):  # function to remove disambiguation results
				#try:
				#print("2")
				res = wikipedia.search(word)
				#except IndexError:
								#list1 = []
				#return list1
						
				list1 = []
				if (len(res) > 0):
					a = 0
					for a in range(10):
						words = res[a].split("(")
						if(res[a] not in list1):	
							if len(words) > 1:
								if (words[1] == "disambiguation)"):
									continue
								else:
									list1.append(res[a].lower())
							else:
								list1.append(res[a].lower())
						else:
							continue
				else:
					list1.append("no results")
				#print(list1)
				return list1


def listComparison(userTextReply, method):  # function to compare partial text with list of results.
    global matchedItem
    global matchedMoreinfo
    global results
    global titles
    global i
    d = {}
    if (method == 1):#method one is to compare with results
        #print(results)
        if(results):
            for k in range(0, i):
                d[results[k]] = similar1(userTextReply, results[k])
                sorted_d = sorted(d.items(), key=operator.itemgetter(1))
			#print(sorted_d)
            if (sorted_d[-1][1] > 0.60):
                matchedItem = sorted_d[-1][0]
				# print(sorted_d[-1][1])
				# print(matchedItem)
                return 1
            else:
                return 0
        else:
                return 0
        '''else:
            for i in range(len(results)):
                d[results[i]]=similar1(userTextReply , results[i])
                sorted_d = sorted(d.items(), key=operator.itemgetter(1))
            #print(sorted_d)
            if(sorted_d[-1][1]>0.50):
                matchedItem=sorted_d[-1][0]
                matchedItem2=sorted_d[-2][0]
                print(sorted_d[-2][0])
                print(matchedItem)
                return 1
            else:
                return 0'''
    elif (method == 2):#method two is to compare with titles(more info)
        if (len(titles) > 10):
            #print("entered1")
            for k in range(10):
                #print("entered2")
                d[titles[k][0]] = similar1(userTextReply, titles[k][0])
                sorted_d = sorted(d.items(), key=operator.itemgetter(1))
            #print(sorted_d)
            if (sorted_d[-1][1] > 0.60):
                #print("entered3")
                matchedMoreinfo = sorted_d[-1][0]
                # print(sorted_d[-1][1])
                # print(matchedItem)
                return 1
            else:
                return 0
        elif(titles):
            for k in range(len(titles)):
                d[titles[k][0]] = similar1(userTextReply, titles[k][0])
                sorted_d = sorted(d.items(), key=operator.itemgetter(1))
            # print(sorted_d)
            if (sorted_d[-1][1] > 0.60):
                matchedMoreinfo = sorted_d[-1][0]
                # print(sorted_d[-1][1])
                # print(matchedItem)
                return 1
            else:
                return 0
        else:
                return 0

def similar1(a, b):
    return SequenceMatcher(None, a, b).ratio()


def create_connection():  # function to setup database connection.
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    conn = sqlite3.connect('chat2.db')

    return conn


def create_user(conn, value):  # function to create new users in database
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO users(name)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, value)
    return cur.lastrowid


def store_chat(conn, chatInformation):  # function to store messages in database.


    sql = ''' INSERT INTO messages(search_id,user_text,bot_reply,information,user_id)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, chatInformation)
    return cur.lastrowid


def chat_log(conn, chatInformation):  # function to store users and search id's


    sql = ''' INSERT INTO chat_log(search_id,user_id)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, chatInformation)
    return cur.lastrowid

def traditional_search_log(conn, chatInformation):  # function to store users and search id's


    sql = ''' INSERT INTO traditional_search(search_word,search_results)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, chatInformation)
    return cur.lastrowid


###############################################################Main Web service Code#########################################################################

@app.route("/")
def home():
    return render_template("chat.html")
	
@app.route('/normal_search')
def cool_form():
    return render_template('normal_search.html')
	
@app.route("/get")
def get_bot_response():
    #Parsing the test from the Chatbot
		global search_flag #
		global spell_flag  #
		global option_flag #
		global newSpell #
		global moreresults_count #
		global spell_moreresults_count #
		global append_summary #
		global i
		global words
		global results
		global numberChosen
		global newWord
		global titles
		global moreinfo_dictionary
		global matchedItem
		global matchedMoreinfo
		global displayWord
		global newUserId
		global userText
		global search_id
		global information_flag
		userText = request.args.get('msg')
		userText=userText.lower()
		spell = SpellChecker()
		m = mybot.respond(userText)
		words = m.split("@")
		
        # the Words would be main response extracted from the AIML and then
        # it will further split based on the @ Sign and later will be saved in the list named as Word where word [0]
        # contain the Aiml response and [1] contain the Query needed for the search
		
		if((userText == "go back") and (option_flag) and (i>=3)):#this part of the code is executed when user wants to go back to previous results
									chatSummary=[]
									titles=[]
									moreinfo_dictionary={}
									option_flag=0
									print(i)
									i=i-3
									print(i)
									chatSummary.append('Displaying previous results, you can select one among these options:')
									#print(wikipedia.summary(results[i],sentences=2))
									s=summaryFunction(chatSummary)
									conn=create_connection()
									chatInformation=(search_id,str(userText),str(chatSummary),str(append_summary),newUserId)
									store_chat(conn,chatInformation)
									conn.commit()
									dict1 = eval(s)
									return dict1
		elif((userText == "go back") and (search_flag or spell_flag) and (i>3)):#this part of the code is executed when user wants to go back to previous results
									chatSummary=[]
									titles=[]
									moreinfo_dictionary={}
									i=i-6
									moreresults_count=moreresults_count-1
									chatSummary.append('Displaying previous results, or you can select one among these options:')
									#print(wikipedia.summary(results[i],sentences=2))
									s=summaryFunction(chatSummary)
									conn=create_connection()
									chatInformation=(search_id,str(userText),str(chatSummary),str(append_summary),newUserId)
									store_chat(conn,chatInformation)
									conn.commit()
									dict1 = eval(s)
									return dict1
					
		elif userText == "no" and spell_flag ==1:#to handle if suggested spelling is incorrect
								search_flag=1
								spell_flag=0
								append_summary=[]
								i=0
								moreresults_count=0
								chatSummary=[]
								#print("1")
								#print(displayWord)
								#if(information_flag):
								results=getResults(displayWord)
								print(results)
								if (len(results)>2):
										print("hi1")
										chatSummary=[]
										chatSummary.append('I know few things about '+displayWord+', choose one option among the options provided:')
										s=summaryFunction(chatSummary)
										conn=create_connection()
										chatInformation=(search_id,str(userText),str(chatSummary),str(append_summary),newUserId)
										store_chat(conn,chatInformation)
										conn.commit()
								else:
										i=0
										search_flag=0
										moreresults_count=0
										titles=[]
										moreinfo_dictionary={}
										s='{"a" : "Please rephrase your query", "b" : "", "c" : ""}'
								dict1 = eval(s)
								return dict1
								'''else:
									print(words)
									results=getResults(words[1])
									print("hi2")
									if (len(results)>2):
											chatSummary=[]
											displayWord=words[1]
											chatSummary.append('I know few things about '+words[1]+', choose one option among the options provided:')
											s=summaryFunction(chatSummary)
											conn=create_connection()
											chatInformation=(search_id,str(userText),str(chatSummary),str(append_summary),newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
									else:
											i=0
											search_flag=0
											moreresults_count=0
											titles=[]
											moreinfo_dictionary={}
											s='{"a" : "Please rephrase your query", "b" : "", "c" : ""}'
									dict1 = eval(s)
									return dict1'''

		#print(words)
		
		elif userText == "more results" and  search_flag == 1 and moreresults_count != 2:#rendering more information # Can see more results

				moreresults_count += 1
				option_flag=0
				titles=[]
				moreinfo_dictionary={}
				append_summary=[]
				if spell_flag:
					results=getResults(newSpell)
				elif information_flag:
					results=getResults(displayWord)
				if (len(results)>2):
					chatSummary=[]
					chatSummary.append('These are the next set of options, you can choose one option among the options provided:')
					s=summaryFunction(chatSummary)
					conn=create_connection()
					chatInformation=(search_id,str(userText),str(chatSummary),str(append_summary),newUserId)
					store_chat(conn,chatInformation)
					conn.commit()
				else:
					i=0
					search_flag=0
					moreresults_count=0
					titles=[]
					moreinfo_dictionary={}
					s='{"a" : "Please rephrase your query", "b" : "", "c" : ""}'
				dict1 = eval(s)
				return dict1
		elif userText == "more results" and search_flag == 1 and moreresults_count == 2:
																	#search_flag=0
																	s='{"a" : "sorry no information is available", "b" : "", "c" : words[1]}'
																	conn=create_connection()
																	chatInformation=(search_id,str(userText),"sorry no information is available","",newUserId)
																	store_chat(conn,chatInformation)
																	conn.commit()
																	dict1 = eval(s)
																	return dict1
		elif userText == "more results" and not(search_flag or spell_flag): # I and vishal need resit think about spell flag here
											s='{"a" : "this is not right option", "b" : ""}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),"this is not right option","",newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1			
		else:#response to query of the user
			''' This case would be resposible passing the standard conversations. Estaliblished Data base connections'''
			if len(words) == 1:
				if((userText in moreinfo_dictionary.keys())and option_flag):
									option_flag=1
									informationSummary=moreinfo_dictionary[userText]
									chatSummary='Detailed information about '+userText+' is provided.'
									s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
									conn=create_connection()
									chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
									store_chat(conn,chatInformation)
									conn.commit()
									dict1 = eval(s)
									return dict1
				elif((listComparison(userText,2) and titles)):
											option_flag=1
											informationSummary=moreinfo_dictionary[matchedMoreinfo]
											chatSummary='Detailed information about '+matchedMoreinfo+' is provided.'
											s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
				elif((userText in results[0:i] and (search_flag or spell_flag) and i>0)):
											option_flag=1
											informationSummary=fullSummary(userText)
											chatSummary='Brief information about '+userText+' is provided'
											s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
				elif((listComparison(userText,1) and (search_flag or spell_flag) and i>0)):#to comapre partially matched text
														option_flag=1
														newWord=matchedItem
														informationSummary=fullSummary(matchedItem)
														chatSummary='Displaying results of '+matchedItem
														s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
														conn=create_connection()
														chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
														store_chat(conn,chatInformation)
														conn.commit()
														dict1 = eval(s)
														return dict1
				else:
					s='{"a" : words[0]}'
					search_id=0
					conn=create_connection()
					value=("chatbot",)
					newUserId=create_user(conn,value)
					conn.commit()
					chatInformation=(search_id,str(userText),str(words[0]),"",newUserId)
					store_chat(conn,chatInformation)
					conn.commit()
					#print(newUserId)
					#converting into dictionary
					dict1 = eval(s)
					return(dict1)
			elif len(words)>1:#checking the search query (with the spilt of @)
							#if len(newSpell)==0:
								''' REmove the black space '''
								n=str(words[1]).strip()
								w = n.split(" ")
								''' check the syntax, Could be replace by the spelling funcations and spelling functions need to modify where it may give list of relevent suggestions and could also return the true and false'''
								misspelled = spell.unknown(w)
								if words[1]=='yes' and spell_flag:#when user confirms the new spelling
									titles=[]
									moreinfo_dictionary={}
									append_summary=[]
									search_flag=1
									spell_flag=1
									i=0
									#displayWord=newSpell
									#print("hi")
									results=getResults(newSpell)
									if (len(results)>2):
										chatSummary=[]
										chatSummary.append('Displaying results of '+newSpell+',you can choose one option among the options provided :')
										s=summaryFunction(chatSummary)
										conn=create_connection()
										chatInformation=(search_id,str(userText),str(chatSummary),str(append_summary),newUserId)
										store_chat(conn,chatInformation)
										conn.commit()
									else:
										i=0
										search_flag=0
										moreresults_count=0
										titles=[]
										moreinfo_dictionary={}
										s='{"a" : "Please rephrase your query", "b" : "", "c" : ""}'
										conn=create_connection()
										chatInformation=(search_id,str(userText),"Please rephrase your query","",newUserId)
										store_chat(conn,chatInformation)
										conn.commit()
									dict1 = eval(s)
									return dict1
								elif words[1]=='yes' and not spell_flag:
										s='{"a" : "I am not sure, please enter valid query", "b" : "", "c" : ""}'
										conn=create_connection()
										chatInformation=(search_id,str(userText),"I am not sure, please enter valid query","",newUserId)
										store_chat(conn,chatInformation)
										conn.commit()
								elif( words[0]=="open" and (titles)):#to dispaly the summary of option chosen after moreinfo.
											if(words[1].isdigit()):
												option_flag=1
												numberChosen1=int(words[1])
												chatSummary=[]
												try:
													informationSummary=titles[numberChosen1][1]
													chatSummary.append('Detailed information about '+titles[numberChosen1][0]+' is provided.')
												except IndexError:
													chatSummary=[]
													chatSummary.append('this is not right option')
													informationSummary=""
												except wikipedia.exceptions.PageError:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
											else:
												if(words[1] in moreinfo_dictionary.keys()):#check if we have user text is present in the moreinfo_dictionary.
													print(i)
													option_flag=1
													informationSummary=moreinfo_dictionary[words[1]]
													chatSummary='Detailed information about '+words[1]+' is provided.'
													s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
                                               #List functions
												elif(listComparison(words[1],2)):
													print(i)
													option_flag=1
													informationSummary=moreinfo_dictionary[matchedMoreinfo]
													chatSummary='Detailed information about '+matchedMoreinfo+' is provided.'
													s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												else:
													chatSummary='This is not a right option, please select valid option.'
													s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
								elif( words[0]=="open" and (search_flag or spell_flag)):#to dispaly the summary of option chosen.
									if(words[1].isdigit()):
										option_flag=1
                                        # check with the search results here i will count the number of results display in chatbox
										if(int(words[1])<i):
											informationSummary=fullSummary(words[1])
											if(len(informationSummary)==1):
												chatSummary='This is not right option, please choose another option'
												s='{"a" : chatSummary, "b" :"" , "c" : displayWord}'
											else:
												chatSummary='Brief information about '+results[int(words[1])]+' is provided.'
												s='{"a" : chatSummary, "b" : informationSummary , "c" : displayWord}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
										else:
											chatSummary='This is not a right option, please select valid option.'
											s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
##################################Checking the User text is present in the list and not
									else:
											if (words[1] in results[0:i]):#check if we have user text is present in the list.
												option_flag=1
												informationSummary=fullSummary(words[1])
												chatSummary='Brief information about '+words[1]+' is provided'
												s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
											elif(listComparison(words[1],1)):#to comapre partially matched text
												option_flag=1
												newWord=matchedItem
												informationSummary=fullSummary(matchedItem)
												chatSummary='Displaying results of '+matchedItem
												s='{"a" : chatSummary, "b" : informationSummary, "c" : displayWord}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),str(informationSummary),newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
											else:
												chatSummary='This option is not present'
												s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
								elif( words[0]=="link" and (search_flag or spell_flag)):
												chatSummary=[]
												chatSummary.append('Displaying results of')
												s=sendLink(chatSummary)
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
								elif( words[0]=="link" and not(search_flag or spell_flag)):
												chatSummary='This option is not present'
												s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
                                        ##########################we are here 
								elif words[0] =="show" and search_flag:#open full document and highlight important information.
									if words[1].isdigit():#full doc with neumeric option
										if(int(words[1])<i):
												option_flag=1 # Indicating the option choose
												try:
													summary=wikipedia.page(results[int(words[1])]).content
												except wikipedia.exceptions.PageError:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												except wikipedia.exceptions.DisambiguationError as e:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												summary=re.sub(r"\.(?=\S)", '. ', summary)
												alltitles1 = re.findall(r'(={1,5})\s(.+)\s*(.+)', summary)
												titles1=[]
												for t in range(len(alltitles1)):
													''' Removing the equal signs from the title in multi dimensional'''
													try:
														text =re.sub(r'=','',alltitles1[t][1].lower())
														text.replace(' ', '')
													except IndexError:
														chatSummary=[]
														chatSummary.append("Detailed information is not available, please choose another option")
														s='{"a" : chatSummary,"b" :""}'
														
													''' Check the whats is going on  Why? check if count space'''
													#print(text)
													if text not in ('See also','References','Further reading','External links','Notes','Bibliography'):
																		text2=alltitles1[t][2]
																		if(len(text2)>100):
																			titles1.append([text[0:-1].lower(),text2])
												highlightText= AbhishekSummarizer.main(wikipedia.page(results[int(words[1])]).url,wikipedia.page(results[int(words[1])]).title, 2, 50)
												#highlightText= AbhishekSummarizer.main(wikipedia.page(results[int(words[1])]).url,wikipedia.page(results[int(words[1])]).title, 2, 50)
												highlight2=highlightText
												newHighlight=[]
												linkText=[]
												for item in range(len(highlightText)):
													newHighlight.append(((re.sub(r" ?\[[^)]+\]", "", highlightText[item])).strip()).replace('"','').replace(',','').replace("'",'').replace("'",""))
													linkText.append(((re.sub(r" ?\[[^)]+\]", "", highlight2[item])).strip()))
												#resu=[]
												#resu.append(re.sub(r"\[[0-9]*\]", "", highlightText[:][:]))
												#print(type(highlightText))
												#print(highlightText)
												#print(type(sent_tokenize(str(highlightText))))
												#l1=sent_tokenize(str(highlightText))
												#l2=sent_tokenize(str(wikipedia.summary("india")))
												#print(l1[14][4:])
												#print(l2[1])
												#print(titles[1][1])
												#print(titles[1][0])
												anchorTag=[]
												#intro=[]
												#intro.append((str(wikipedia.summary(results[int(words[1])])).split(".")))
												#print(intro)
												#for t in sent_tokenize(wikipedia.summary(results[int(words[1])])):
													#print(t)
												introText=wikipedia.summary(results[int(words[1])])
												#for j in range(len(titles1)):
												for k in range(len(linkText)):
													if(linkText[k] in sent_tokenize(introText)):
														#print(k)
														anchor_text = '<a href="#{}">{}</a><br>'.format("intro",linkText[k])
														if(anchor_text not in anchorTag):
															anchorTag.append(anchor_text)
													elif(introText.find(linkText[k])>=0):
													#elif(linkText[k] not in sent_tokenize(str(titles1[j][1]))):
														if(linkText[k]=="."):
																continue
														else:
															anchor_text = '<a href="#{}">{}</a><br>'.format("intro",linkText[k])
															anchorTag.append(anchor_text)
												#print(anchorTag)
												#newhighlight=[]
												for j in range(len(titles1)):
													#print(j)
													for l in range(len(linkText)):
														#newhighlight.append(highlightText[l].replace('"','').replace(',','').replace("'",'').replace("'",""))
														if(linkText[l] in sent_tokenize(str(titles1[j][1]))):
															#print(l)
															anchor_text1 = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
															anchorTag.append(anchor_text1)
														elif(str(titles1[j][1]).find(linkText[l])>=0):
														#elif(linkText[k] not in sent_tokenize(str(titles1[j][1]))):
															if(linkText[l]=="."):
																continue
															else:
																anchor_text = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
																anchorTag.append(anchor_text)#elif(linkText[l] not in sent_tokenize(introText)):
																#anchor_text1 = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
															#anchorTag.append(anchor_text1)
												divTag=[]
												#print(summary)
												summ=wikipedia.summary(results[int(words[1])])
												print(summ)
												#summ=summ.replace("/n", "").replace("/s", "")
												summ = summ.replace('\n', '').replace('\r', '')
												#summ = summ.replace('\t', '').replace('\s', '')
												summ = re.sub('\t', " ", summ).replace('\s', '')
												summ = re.sub('\|\s+(.+)\.svg', " ", summ)
												#print(summ)
												#summ=re.sub('', '', summ)
												summ=re.sub('\"', '', summ)
												summ=re.sub('\'', '', summ)
												
												summ=re.sub(r"\.(?=\S)", '. ', summ)
												divTag.append('<div id="intro">{}</div><br>'.format(summ))
												#print(divTag)
												for a in range(len(titles1)):
													div_text='<div id={}><b>{}</b><br>{}</div><br>'.format(titles1[a][0].replace(" ", ""),titles1[a][0],titles1[a][1].replace("/n", " ").replace('\'', '').replace('  ', ' '))
													divTag.append(div_text)
												full_text='<div>{}<br><br><div class="fulldoc1">{}</div></div>'.format(anchorTag,divTag)
												#highlightText = wikipedia.summary(results[numberChosen]).strip()
												#highlightText = highlightText.replace('\r\n', '\n').replace('\r', '\n')
												#highlightText = re.sub('\n+', "\n", highlightText).replace('\n', '\n\n')
												#highlightText = re.sub('\|\s+(.+)\.svg', "", highlightText)
												#print(anchorTag)
												chatSummary='Displayed full document of '+results[int(words[1])]+'.'
												s='{"a" : chatSummary,"b" :"","c" :"", "d" : full_text , "e" : newHighlight,"t" : "div.fulldoc1"}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),str(summary),newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
										else:
											chatSummary='This is not a right option, please select valid option.'
											s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
										
									else:#full doc with text option
										if(words[1] in results[0:i]):
												option_flag=1 # Indicating the option choose
												try:
													summary=wikipedia.page(words[1]).content
												except wikipedia.exceptions.PageError:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												except wikipedia.exceptions.DisambiguationError as e:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												summary=re.sub(r"\.(?=\S)", '. ', summary)
												alltitles1 = re.findall(r'(={1,5})\s(.+)\s*(.+)', summary)
												titles1=[]
												for t in range(len(alltitles1)):
													''' Removing the equal signs from the title in multi dimensional'''
													try:
														text =re.sub(r'=','',alltitles1[t][1].lower())
														text.replace(' ', '')
													except IndexError:
														chatSummary=[]
														chatSummary.append("Detailed information is not available, please choose another option")
														s='{"a" : chatSummary,"b" :""}'
														
													''' Check the whats is going on  Why? check if count space'''
													#print(text)
													if text not in ('See also','References','Further reading','External links','Notes','Bibliography'):
																		text2=alltitles1[t][2]
																		if(len(text2)>100):
																			titles1.append([text[0:-1].lower(),text2])
												highlightText= AbhishekSummarizer.main(wikipedia.page(words[1]).url,wikipedia.page(words[1]).title, 2, 50)
												#highlightText= AbhishekSummarizer.main(wikipedia.page(results[int(words[1])]).url,wikipedia.page(results[int(words[1])]).title, 2, 50)
												highlight2=highlightText
												newHighlight=[]
												linkText=[]
												for item in range(len(highlightText)):
													newHighlight.append(((re.sub(r" ?\[[^)]+\]", "", highlightText[item])).strip()).replace('"','').replace(',','').replace("'",'').replace("'",""))
													linkText.append(((re.sub(r" ?\[[^)]+\]", "", highlight2[item])).strip()))
												#resu=[]
												#resu.append(re.sub(r"\[[0-9]*\]", "", highlightText[:][:]))
												#print(type(highlightText))
												#print(highlightText)
												#print(type(sent_tokenize(str(highlightText))))
												#l1=sent_tokenize(str(highlightText))
												#l2=sent_tokenize(str(wikipedia.summary("india")))
												#print(l1[14][4:])
												#print(l2[1])
												#print(titles[1][1])
												#print(titles[1][0])
												anchorTag=[]
												#intro=[]
												#intro.append((str(wikipedia.summary(results[int(words[1])])).split(".")))
												#print(intro)
												#for t in sent_tokenize(wikipedia.summary(results[int(words[1])])):
													#print(t)
												introText=wikipedia.summary(words[1])
												#for j in range(len(titles1)):
												for k in range(len(linkText)):
													if(linkText[k] in sent_tokenize(introText)):
														#print(k)
														anchor_text = '<a href="#{}">{}</a><br>'.format("intro",linkText[k])
														if(anchor_text not in anchorTag):
															anchorTag.append(anchor_text)
													elif(introText.find(linkText[k])>=0):
													#elif(linkText[k] not in sent_tokenize(str(titles1[j][1]))):
														if(linkText[k]=="."):
																continue
														else:
															anchor_text = '<a href="#{}">{}</a><br>'.format("intro",linkText[k])
															anchorTag.append(anchor_text)
												#print(anchorTag)
												#newhighlight=[]
												for j in range(len(titles1)):
													#print(j)
													for l in range(len(linkText)):
														#newhighlight.append(highlightText[l].replace('"','').replace(',','').replace("'",'').replace("'",""))
														if(linkText[l] in sent_tokenize(str(titles1[j][1]))):
															#print(l)
															anchor_text1 = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
															anchorTag.append(anchor_text1)
														elif(str(titles1[j][1]).find(linkText[l])>=0):
														#elif(linkText[k] not in sent_tokenize(str(titles1[j][1]))):
															if(linkText[l]=="."):
																continue
															else:
																anchor_text = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
																anchorTag.append(anchor_text)#elif(linkText[l] not in sent_tokenize(introText)):
																#anchor_text1 = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
															#anchorTag.append(anchor_text1)
												divTag=[]
												#print(summary)
												summ=wikipedia.summary(words[1])
												#summ=summ.replace("/n", "").replace("/s", "")
												summ = summ.replace('\n', '').replace('\r', '')
												#summ = summ.replace('\t', '').replace('\s', '')
												summ = re.sub('\t', " ", summ).replace('\s', '')
												summ = re.sub('\|\s+(.+)\.svg', " ", summ)
												#print(summ)
												#summ=re.sub('', '', summ)
												summ=re.sub('\"', '', summ)
												summ=re.sub('\'', '', summ)
												
												summ=re.sub(r"\.(?=\S)", '. ', summ)
												divTag.append('<div id="intro">{}</div><br>'.format(summ))
												#print(divTag)
												for a in range(len(titles1)):
													div_text='<div id={}><b>{}</b><br>{}</div><br>'.format(titles1[a][0].replace(" ", ""),titles1[a][0],titles1[a][1].replace("/n", " ").replace('\'', '').replace('  ', ' '))
													divTag.append(div_text)
												full_text='<div>{}<br><br><div class="fulldoc1">{}</div></div>'.format(anchorTag,divTag)
												#highlightText = wikipedia.summary(results[numberChosen]).strip()
												#highlightText = highlightText.replace('\r\n', '\n').replace('\r', '\n')
												#highlightText = re.sub('\n+', "\n", highlightText).replace('\n', '\n\n')
												#highlightText = re.sub('\|\s+(.+)\.svg', "", highlightText)
												#print(anchorTag)
												chatSummary='Displayed full document of '+words[1]+'.'
												s='{"a" : chatSummary,"b" :"","c" :"", "d" : full_text , "e" : newHighlight,"t" : "div.fulldoc1"}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),str(summary),newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
										elif(listComparison(words[1],1)):
												option_flag=1 # Indicating the option choose
												try:
													summary=wikipedia.page(matchedItem).content
												except wikipedia.exceptions.PageError:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												except wikipedia.exceptions.DisambiguationError as e:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												summary=re.sub(r"\.(?=\S)", '. ', summary)
												alltitles1 = re.findall(r'(={1,5})\s(.+)\s*(.+)', summary)
												titles1=[]
												for t in range(len(alltitles1)):
													''' Removing the equal signs from the title in multi dimensional'''
													try:
														text =re.sub(r'=','',alltitles1[t][1].lower())
														text.replace(' ', '')
													except IndexError:
														chatSummary=[]
														chatSummary.append("Detailed information is not available, please choose another option")
														s='{"a" : chatSummary,"b" :""}'
														
													''' Check the whats is going on  Why? check if count space'''
													#print(text)
													if text not in ('See also','References','Further reading','External links','Notes','Bibliography'):
																		text2=alltitles1[t][2]
																		if(len(text2)>100):
																			titles1.append([text[0:-1].lower(),text2])
												highlightText= AbhishekSummarizer.main(wikipedia.page(matchedItem).url,wikipedia.page(matchedItem).title, 2, 50)
												#highlightText= AbhishekSummarizer.main(wikipedia.page(results[int(words[1])]).url,wikipedia.page(results[int(words[1])]).title, 2, 50)
												highlight2=highlightText
												newHighlight=[]
												linkText=[]
												for item in range(len(highlightText)):
													newHighlight.append(((re.sub(r" ?\[[^)]+\]", "", highlightText[item])).strip()).replace('"','').replace(',','').replace("'",'').replace("'",""))
													linkText.append(((re.sub(r" ?\[[^)]+\]", "", highlight2[item])).strip()))
												#resu=[]
												#resu.append(re.sub(r"\[[0-9]*\]", "", highlightText[:][:]))
												#print(type(highlightText))
												#print(highlightText)
												#print(type(sent_tokenize(str(highlightText))))
												#l1=sent_tokenize(str(highlightText))
												#l2=sent_tokenize(str(wikipedia.summary("india")))
												#print(l1[14][4:])
												#print(l2[1])
												#print(titles[1][1])
												#print(titles[1][0])
												anchorTag=[]
												#intro=[]
												#intro.append((str(wikipedia.summary(results[int(words[1])])).split(".")))
												#print(intro)
												#for t in sent_tokenize(wikipedia.summary(results[int(words[1])])):
													#print(t)
												introText=wikipedia.summary(matchedItem)
												#for j in range(len(titles1)):
												for k in range(len(linkText)):
													if(linkText[k] in sent_tokenize(introText)):
														#print(k)
														anchor_text = '<a href="#{}">{}</a><br>'.format("intro",linkText[k])
														if(anchor_text not in anchorTag):
															anchorTag.append(anchor_text)
													elif(introText.find(linkText[k])>=0):
													#elif(linkText[k] not in sent_tokenize(str(titles1[j][1]))):
														if(linkText[k]=="."):
																continue
														else:
															anchor_text = '<a href="#{}">{}</a><br>'.format("intro",linkText[k])
															anchorTag.append(anchor_text)
												#print(anchorTag)
												#newhighlight=[]
												for j in range(len(titles1)):
													#print(j)
													for l in range(len(linkText)):
														#newhighlight.append(highlightText[l].replace('"','').replace(',','').replace("'",'').replace("'",""))
														if(linkText[l] in sent_tokenize(str(titles1[j][1]))):
															#print(l)
															anchor_text1 = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
															anchorTag.append(anchor_text1)
														elif(str(titles1[j][1]).find(linkText[l])>=0):
														#elif(linkText[k] not in sent_tokenize(str(titles1[j][1]))):
															if(linkText[l]=="."):
																continue
															else:
																anchor_text = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
																anchorTag.append(anchor_text)#elif(linkText[l] not in sent_tokenize(introText)):
																#anchor_text1 = '<a href="#{}">{}</a><br>'.format(titles1[j][0].replace(" ", ""),linkText[l])
															#anchorTag.append(anchor_text1)
												divTag=[]
												#print(summary)
												summ=wikipedia.summary(matchedItem)
												#summ=summ.replace("/n", "").replace("/s", "")
												summ = summ.replace('\n', '').replace('\r', '')
												#summ = summ.replace('\t', '').replace('\s', '')
												summ = re.sub('\t', " ", summ).replace('\s', '')
												summ = re.sub('\|\s+(.+)\.svg', " ", summ)
												#print(summ)
												#summ=re.sub('', '', summ)
												summ=re.sub('\"', '', summ)
												summ=re.sub('\'', '', summ)
												
												summ=re.sub(r"\.(?=\S)", '. ', summ)
												divTag.append('<div id="intro">{}</div><br>'.format(summ))
												#print(divTag)
												for a in range(len(titles1)):
													div_text='<div id={}><b>{}</b><br>{}</div><br>'.format(titles1[a][0].replace(" ", ""),titles1[a][0],titles1[a][1].replace("/n", " ").replace('\'', '').replace('  ', ' '))
													divTag.append(div_text)
												full_text='<div>{}<br><br><div class="fulldoc1">{}</div></div>'.format(anchorTag,divTag)
												#highlightText = wikipedia.summary(results[numberChosen]).strip()
												#highlightText = highlightText.replace('\r\n', '\n').replace('\r', '\n')
												#highlightText = re.sub('\n+', "\n", highlightText).replace('\n', '\n\n')
												#highlightText = re.sub('\|\s+(.+)\.svg', "", highlightText)
												#print(anchorTag)
												chatSummary='Displayed full document of '+matchedItem+'.'
												s='{"a" : chatSummary,"b" :"","c" :"", "d" : full_text , "e" : newHighlight,"t" : "div.fulldoc1"}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),str(summary),newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
										else:
												chatSummary='This option is not present'
												s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
								elif words[0] =="full" and search_flag:#open full document and highlight important information.
									if words[1].isdigit():#full doc with neumeric option
										if(int(words[1])<i):
												option_flag=1 # Indicating the option choose
												try:
													summary=wikipedia.page(results[int(words[1])]).content
												except wikipedia.exceptions.PageError:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												except wikipedia.exceptions.DisambiguationError as e:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												
												summary = summary.replace('\n==', '<b>').replace('==\n', '</b><br>')#  replacing  bold the title and giving the space
												summary = summary.replace('\r\n', '\n').replace('\r', '\n')# replace the setting up the cursor for new line and begining
												summary = summary.replace('\n\n', '<br><br>')# giving space
												summary = summary.replace('=', '')
												summary = re.sub('\|\s+(.+)\.svg', "", summary) #
												summary = re.sub(r"\.(?=\S)", '. ', summary)
												#(re.sub(r" ?\[[^)]+\]", "", item)
												highlightText= AbhishekSummarizer.main(wikipedia.page(results[int(words[1])]).url,wikipedia.page(results[int(words[1])]).title, 2, 50)
												newHighlight=[]
												for item in range(len(highlightText)):
													newHighlight.append((re.sub(r" ?\[[^)]+\]", "", highlightText[item])).strip())
												print(newHighlight)
												#highlightText = wikipedia.summary(results[numberChosen]).strip()
												#highlightText = highlightText.replace('\r\n', '\n').replace('\r', '\n')
												#highlightText = re.sub('\n+', "\n", highlightText).replace('\n', '\n\n')
												#highlightText = re.sub('\|\s+(.+)\.svg', "", highlightText)
												chatSummary='Displayed full document of '+results[int(words[1])]+'.'
												s='{"a" : chatSummary,"b" :"","c" :"", "d" : summary, "e" : newHighlight,"t" : "div.modal-content"}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),str(summary),newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
										else:
											chatSummary='This is not a right option, please select valid option.'
											s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
										
									else:#full doc with text option
										if(words[1] in results[0:i]):
											option_flag=1
											try:
												summary=wikipedia.page(words[1]).content
												summary = summary.replace('\n==', '<b>').replace('==\n', '</b><br>')
												summary = summary.replace('\r\n', '\n').replace('\r', '\n')
												summary = summary.replace('\n', '<br>')
												summary = summary.replace('\n\n', '<br><br>')
												summary = summary.replace('=', '')
												summary = re.sub('\|\s+(.+)\.svg', "", summary)
												highlightText= AbhishekSummarizer.main(wikipedia.page(words[1]).url,wikipedia.page(words[1]).title , 2, 50)
											except wikipedia.exceptions.PageError:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
											except wikipedia.exceptions.DisambiguationError as e:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
											#highlightText = wikipedia.summary(newWord).strip()
											#highlightText = highlightText.replace('\r\n', '\n').replace('\r', '\n')
											#highlightText = re.sub('\|\s+(.+)\.svg', "", highlightText)
											#highlightText = re.sub('\n+', "\n", highlightText).replace('\n', '\n\n')
											chatSummary='Displayed full document of '+words[1]+'.'
											s='{"a" : chatSummary,"b" :"","c" :"", "d" : summary, "e" : highlightText,"t" : "div.modal-content"}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),str(chatSummary),str(summary),newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
										elif(listComparison(words[1],1)):
											option_flag=1
											try:
												summary=wikipedia.page(matchedItem).content
												summary = summary.replace('\n==', '<b>').replace('==\n', '</b><br>')
												summary = summary.replace('\r\n', '\n').replace('\r', '\n')
												summary = summary.replace('\n', '<br>')
												summary = summary.replace('\n\n', '<br><br>')
												summary = summary.replace('=', '')
												summary = re.sub('\|\s+(.+)\.svg', "", summary)
												highlightText= AbhishekSummarizer.main(wikipedia.page(matchedItem).url,wikipedia.page(matchedItem).title , 2, 50)
											except wikipedia.exceptions.PageError:
													chatSummary=[]
													chatSummary.append("This is not a right option, please rephrase your query.")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
											except wikipedia.exceptions.DisambiguationError as e:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
											#highlightText = wikipedia.summary(newWord).strip()
											#highlightText = highlightText.replace('\r\n', '\n').replace('\r', '\n')
											#highlightText = re.sub('\|\s+(.+)\.svg', "", highlightText)
											#highlightText = re.sub('\n+', "\n", highlightText).replace('\n', '\n\n')
											chatSummary='Displayed full document of '+matchedItem+'.'
											s='{"a" : chatSummary,"b" :"","c" :"", "d" : summary, "e" : highlightText,"t" : "div.modal-content"}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),str(chatSummary),str(summary),newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
										else:
												chatSummary='This option is not present'
												s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
								elif words[0] =="more" and search_flag:#more information with options on the displayed results.
									if(words[1].isdigit()):
										if(int(words[1])<i):
											option_flag=1 #When we options, we have to make sure that is more info
											''' Extract  all the titles'''
											try:
												alltitles = re.findall(r'(={1,5})\s(.+)\s*(.+)', wikipedia.page(results[int(words[1])]).content)
											except wikipedia.exceptions.PageError:
												chatSummary=[]
												chatSummary.append("This is not right option, please choose another option")
												s='{"a" :chatSummary ,"b" :""}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
											except wikipedia.exceptions.DisambiguationError as e:
													chatSummary=[]
													chatSummary.append("This is not a right option, please choose another option")
													s='{"a" :chatSummary ,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
											titles=[]
											for t in range(len(alltitles)):
												''' Removing the equal signs from the title in multi dimensional'''
												try:
													text =re.sub(r'=','',alltitles[t][1].lower())
													text.replace(' ', '')
												except IndexError:
													chatSummary=[]
													chatSummary.append("Detailed information is not available, please choose another option")
													s='{"a" : chatSummary,"b" :""}'
													
												''' Check the whats is going on  Why? check if count space'''
												#print(text)
												if text not in ('See also','References','Further reading','External links','Notes','Bibliography'):
																	text2=alltitles[t][2]
																	if(len(text2)>100):
																		titles.append([text[0:-1].lower(),text2])

											if(len(titles)==0):
												chatSummary=[]
												chatSummary.append("Detailed information is not available, please choose another option")
												s='{"a" : chatSummary,"b" :""}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
											else:

												'''
												Sending All the tiles to Chat summary to display
												'''

												chatSummary=[]
												moreinfo_dictionary={} # converting those titles into dictionary
												moreinfo_dictionary=dict(titles) #
												chatSummary.append("Displaying detailed options for "+results[int(words[1])]+", you can choose one option from the options provided to get detailed explanation: ")
												if(len(titles)>10):
													for u in range(10):
														chatSummary.append((' {} : {} ').format(u,titles[u][0]))
													s='{"a" : chatSummary,"b" :"", "c" : displayWord}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												else:
													for u in range(len(titles)):
														chatSummary.append((' {} : {} ').format(u,titles[u][0]))
													s='{"a" : chatSummary,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
										else:
											chatSummary='This is not a right option, please select valid option.'
											s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
							#################################################more info options for digit ends #######################################
									else:
										'''##################################More info for the word  Text#################################
										 4th December '''
										print(i)
										if(words[1] in results[0:i]):
											print(i)
											option_flag=1
											alltitles = re.findall(r'(={1,5})\s(.+)\s*(.+)', wikipedia.page(words[1]).content)
											titles=[]
											for t in range(len(alltitles)):
												text =re.sub(r'=','',alltitles[t][1].lower())
												text.replace(' ', '')
												if text not in ('See also','References','Further reading','External links','Notes','Bibliography'):
																	text2=alltitles[t][2]
																	if(len(text2)>100):
																		titles.append([text[0:-1].lower(),text2])
											if(len(titles)==0):
													chatSummary=[]
													chatSummary.append("This is not right option, please choose another option")
													s='{"a" : chatSummary,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
											else:
												chatSummary=[]
												moreinfo_dictionary={}
												moreinfo_dictionary=dict(titles)
												chatSummary.append("Displaying detailed options for "+words[1]+", you can choose one option from the options provided to get detailed explanation: ")
												if(len(titles)>10):
													for u in range(10):
														chatSummary.append((' {} : {} ').format(u,titles[u][0]))
													s='{"a" : chatSummary,"b" :"", "c" : displayWord}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
												else:
													for u in range(len(titles)):
														chatSummary.append((' {} : {} ').format(u,titles[u][0]))
													s='{"a" : chatSummary,"b" :"", "c" : displayWord}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
										elif(listComparison(words[1],1)):
											print(i)
											option_flag=1
											try:
												alltitles = re.findall(r'(={1,5})\s(.+)\s*(.+)', wikipedia.page(matchedItem).content)
											except wikipedia.exceptions.DisambiguationError as e:
												#alltitles = re.findall(r'(={1,5})\s(.+)\s*(.+)', wikipedia.page(matchedItem2).content)
												chatSummary="please rephrase your query"
												s='{"a" : chatSummary,"b" :""}'
												conn=create_connection()
												chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
												store_chat(conn,chatInformation)
												conn.commit()
												dict1 = eval(s)
												return dict1
											titles=[]
											for t in range(len(alltitles)):
												try:
													text =re.sub(r'=','',alltitles[t][1].lower())
													text.replace(' ', '')
												except IndexError:
													chatSummary=[]
													chatSummary.append("Detailed information is not available, please choose another option")
													s='{"a" : chatSummary,"b" :""}'
												if text not in ('See also','References','Further reading','External links','Notes','Bibliography'):
																	text2=alltitles[t][2]
																	if(len(text2)>100):
																		titles.append([text[0:-1].lower(),text2])
											if(len(titles)==0):
													chatSummary=[]
													chatSummary.append("Detailed information is not available, please choose another option")
													s='{"a" : chatSummary,"b" :""}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													return dict1
											else:
												chatSummary=[]
												moreinfo_dictionary={}
												moreinfo_dictionary=dict(titles)
												chatSummary.append("Displaying detailed options for "+matchedItem+", you can choose one option from the options provided to get detailed explanation: ")
												if(len(titles)>10):
													for u in range(10):
														chatSummary.append((' {} : {} ').format(u,titles[u][0]))
													s='{"a" : chatSummary,"b" :"", "c" : displayWord}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													dict1 = eval(s)
													print(i)
													return dict1
												else:
													for u in range(len(titles)):
														chatSummary.append((' {} : {} ').format(u,titles[u][0]))
													s='{"a" : chatSummary,"b" :"", "c" : displayWord}'
													conn=create_connection()
													chatInformation=(search_id,str(userText),str(chatSummary),"",newUserId)
													store_chat(conn,chatInformation)
													conn.commit()
													print(i)
													dict1 = eval(s)
													return dict1
										else:
											chatSummary='This option is not present'
											s='{"a" : chatSummary, "b" : "", "c" : displayWord}'
											conn=create_connection()
											chatInformation=(search_id,str(userText),"This is not a right option, please select valid option.","",newUserId)
											store_chat(conn,chatInformation)
											conn.commit()
											dict1 = eval(s)
											return dict1
								elif len(misspelled):#if spelling mistake is detected.
											spell_flag=1
											search_flag=0
											information_flag=0
											displayWord=words[1]
											newSpell=spelling(n)
											s='{"a" : "Did you mean "+newSpell+"?"}'
											dict1 = eval(s)
											return(dict1)
								else:
									#print(words[1])

									'''
									Case 1: Search from the chat

									'''

									append_summary=[]
									i=0
									displayWord=""
									information_flag=0
									spell_flag=0
									search_flag=1
									moreresults_count=0
									titles=[]
									moreinfo_dictionary={}
									chatSummary=[]

									results=getResults(words[1])

									'''
									word[0] chat reponse
									word[1] searh keyword

									'''

									if (len(results)>2):
										'''first search results.'''
										option_flag=0
										displayWord=words[1]
										chatSummary.append('I know few things about '+words[1]+', choose one option among the options provided:')
										s=summaryFunction(chatSummary)
										#print(chatSummary)
										#print(append_summary)
										search_id+=1
										conn=create_connection()
										chatInformation=(search_id,str(userText),str(chatSummary),str(append_summary),newUserId)
										store_chat(conn,chatInformation)
										conn.commit()
										conn=create_connection()
										chatInformation=(search_id,newUserId)
										chat_log(conn,chatInformation)
										conn.commit()
									else:
										i=0
										search_flag=0
										moreresults_count=0
										titles=[]
										moreinfo_dictionary={}
										'''sending the chat message

										a:Chat message
										b:Information wiki
										c: Search keyword (query)

										'''
										s='{"a" : "Please check  your search word", "b" : "", "c" : ""}'
		dict1 = eval(s)
		return dict1

@app.route('/normal_information')
def normal_information():#function to return normal serach results
		global chatSummary
		global append_summary
		global displayWord
		global results
		global i
		i=0
		chatSummary=[]
		append_summary=[]
		userText = request.args.get('search')
		displayWord=userText
		#print(userText)
		results=getResults(userText)
		#print(results)
		s=summaryFunction_traditional()
		conn=create_connection()
		chatInformation=(str(userText),str(append_summary))
		traditional_search_log(conn,chatInformation)
		conn.commit()
		#print(append_summary)
		dict1 = eval(s)
		return dict1

@app.route('/full_doc/<string:search_word>')
def full_doc(search_word):
	#search_word = request.args.get('arg')
	search_word.replace('%20',' ')
	#search_word.replace('search_word=','')
	#print(search_word[12:])
	summary=wikipedia.page(search_word[12:]).content
	summary = summary.replace('\n==', '<b>').replace('==\n', '</b><br>')#  replacing  bold the title and giving the space
	summary = summary.replace('\r\n', '\n').replace('\r', '\n')# replace the setting up the cursor for new line and begining
	summary = summary.replace('\n\n', '<br><br>')# giving space
	summary = summary.replace('=', '')
	summary = re.sub('\|\s+(.+)\.svg', "", summary)
	#summary = summary.replace('\n==', '\n').replace('==\n', '\n')
	#summary = summary.replace('\r\n', '\n').replace('\r', '\n')
	#summary = summary.replace('\n', '<br>')
	#summary = summary.replace('\n\n', '<br><br>')
	#summary = summary.replace('=', '')
	#summary = re.sub('\|\s+(.+)\.svg', "", summary)
	highlightText= AbhishekSummarizer.main(wikipedia.page(search_word[12:]).url,wikipedia.page(search_word[12:]).title , 2, 50)
	s='{"a" : "", "b" : "" ,"c" :"", "d" : summary, "e" : highlightText}'
	dict1 = eval(s)
	return render_template('full_doc.html',data=dict1)
	
@app.route('/full_doc_traditional/<string:search_word>')
def full_doc1(search_word):
	#search_word = request.args.get('arg')
	search_word.replace('%20',' ')
	#search_word.replace('search_word=','')
	#print(search_word[12:])
	summary=wikipedia.page(search_word[12:]).content
	summary = summary.replace('\n==', '<b>').replace('==\n', '</b><br>')#  replacing  bold the title and giving the space
	summary = summary.replace('\r\n', '\n').replace('\r', '\n')# replace the setting up the cursor for new line and begining
	summary = summary.replace('\n\n', '<br><br>')# giving space
	summary = summary.replace('=', '')
	summary = re.sub('\|\s+(.+)\.svg', "", summary)
	#summary = summary.replace('\n==', '\n').replace('==\n', '\n')
	#summary = summary.replace('\r\n', '\n').replace('\r', '\n')
	#summary = summary.replace('\n', '<br>')
	#summary = summary.replace('\n\n', '<br><br>')
	#summary = summary.replace('=', '')
	#summary = re.sub('\|\s+(.+)\.svg', "", summary)
	#highlightText= AbhishekSummarizer.main(wikipedia.page(search_word[12:]).url,wikipedia.page(search_word[12:]).title , 2, 50)
	#s='{"a" : "", "b" : "" ,"c" :"", "d" : summary, "e" : highlightText}'
	#dict1 = eval(s)
	return render_template('full_doc _traditional.html',data=summary)






@app.route('/information')
def information():#function to return normal serach results
		userText = request.args.get('search')
		global i
		global results
		global search_flag
		global spell_flag
		global moreresults_count
		global titles
		global moreinfo_dictionary
		global information_flag
		global search_id
		global words
		global displayWord
		global newUserId
		global newSpell
		displayWord=userText
		search_id=0
		i=0
		search_flag=1
		information_flag=1
		moreresults_count=0
		results=[]
		titles=[]
		moreinfo_dictionary={}
		chatSummary=[]
		#displayWord=""
		spell_flag=0
		spell = SpellChecker()
		n=str(userText).strip()
		w = n.split(" ")
		misspelled = spell.unknown(w)
		if len(misspelled):#if spelling mistake is detected.
											spell_flag=1
											search_flag=0
											newSpell=spelling(n)
											s='{"a" : "Did you mean "+newSpell+"?","b" : ""}'
											dict1 = eval(s)
											return(dict1)
		results=getResults(userText)
		#print(results)
		if(len(results)>2):
				chatSummary.append('I know few things about '+userText+', choose one option among the options provided:')
				s=summaryFunction(chatSummary)
				conn=create_connection()
				value=("infobot",)
				newUserId=create_user(conn,value)
				conn.commit()
				chatInformation=(search_id,"",str(chatSummary),str(append_summary),newUserId)
				store_chat(conn,chatInformation)
				conn.commit()
		else:
				i=0
				search_flag=0
				moreresults_count=0
				titles=[]
				moreinfo_dictionary={}
				s='{"a" : "Please rephrase your query", "b" : "", "c" : ""}'
		dict1 = eval(s)
		return dict1
	
	


if __name__ == "__main__":
    app.run(debug="true")
