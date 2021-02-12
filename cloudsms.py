from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
import os
from newsapi import NewsApiClient
import textdistance
import json

WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = "+12262429729"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEWS_API_CLIENT = NewsApiClient(api_key=NEWS_API_KEY)
NEWS_API_TOP_HEADLINES_LINK = "https://newsapi.org/v2/top-headlines?country=ca&apiKey="+str(NEWS_API_KEY)+"&language=en&sortBy=popularity"
GOOGLE_SEARCH_API_LINK = "https://www.googleapis.com/customsearch/v1?key="+str(GOOGLE_API_KEY)+"&q="

#Numerical variables to fine tune control of what is sent back to the user
TOP_NEWS_AMOUNT = 5
RELEVANT_NEWS_AMOUNT = 3


#Send an individual text-based message
def send_individual_message(recipient,body):

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        recipient,
        body=body,
        from_=TWILIO_PHONE_NUMBER)

#Send an image as an MMS attachment
def send_individual_image(recipient,picturepath):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.api.account.messages.create(
        to=recipient,
        from_=TWILIO_PHONE_NUMBER,
        media_url=picturepath)

#Search google for an image, if found, send to the recipient that requested it
def find_and_send_image(recipient,query):

    url = GOOGLE_SEARCH_API_LINK+query
    data = requests.get(url).json()
    picturepath = None
    for item in data['items']:
        try:
            picturepath = item['pagemap']['cse_image'][0]['src']
            break
        except:
            send_individual_message(recipient,"Could not find a matching image")
            return
    send_individual_image(recipient,picturepath)



# Get news from the news API
def send_news(recipient,input=None):
    if input is None:
        top_headlines = requests.get(NEWS_API_TOP_HEADLINES_LINK).json()

        for x in range(0, TOP_NEWS_AMOUNT):
            send_individual_message(recipient,top_headlines['articles'][x]['title'] + "\n\n" + top_headlines['articles'][x][
                    'description'] + "\n" + top_headlines['articles'][x]['url'])
    else:
        relevant_headlines = requests.get("https://newsapi.org/v2/everything?q="+input+"&apiKey="+NEWS_API_KEY+"&language=en&sortBy=popularity").json()

        for x in range(0, RELEVANT_NEWS_AMOUNT):
            send_individual_message(recipient,relevant_headlines['articles'][x]['title'] + "\n\n" + relevant_headlines['articles'][x][
                                        'description'] + "\n" + relevant_headlines['articles'][x]['url'])


# Functions to get information from Wolfram Alpha API (This is the all-encompassing results engine)
def get_wolfram_api_link(input):
    return "http://api.wolframalpha.com/v2/query?appid="+str(WOLFRAM_APP_ID)+"&input="+input+"&output=json"

def get_wolfram_full_results(input):
    VALID_POD_TITLES = ["Result","Definition","Results","Wikipedia summary"]
    wolfram_response = requests.get(get_wolfram_api_link(input)).json()

    if "queryresult" not in wolfram_response.keys():
        return "Your request could not be fulfilled"

    if wolfram_response["queryresult"]["success"] == False:
        return "Your request could not be fulfilled"

    for pod in wolfram_response["queryresult"]["pods"]:
        if pod["title"] in VALID_POD_TITLES:
            return pod["subpods"][0]["plaintext"]


app = Flask(__name__)
#Main code to handle the response
@app.route("/handleTwilio", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()
    body = request.form['Body']
    recipient = request.form['From']

    #Give the user top headline relevant query news information
    top_news_phrases_relevant = ["recent news about","news about","headlines about","give me news about"]
    for phrase in top_news_phrases_relevant:
        if phrase in body.lower():
            try:
                about_index = body.index("about")
                send_news(recipient,body[about_index+6:])
                resp.message("Your news is being dispatched")
                return str(resp)
            except ValueError:
                resp.message("Failed to fetch news, if you are trying to obtain news about a specific topic, ask 'news about [query]'")
                return str(resp)

    #Give the user top headline news information
    top_news_phrases = ["give me the top headlines","what is the recent news","news","recent news","top headlines","news in canada","top news","trending news","trending headlines"]
    for phrase in top_news_phrases:
        #Check if the user is plausible to be asking for the top headlines
        if (textdistance.hamming.normalized_similarity(phrase,body) > 0.75):
            send_news(recipient)
            resp.message("Your news is being dispatched")
            return str(resp)


    #Find and send images to the user
    images_phrases = ["find a picture of", "pictures of","picture of","image of","find an image of","images of"]
    for phrase in images_phrases:
        if phrase in body.lower():
            try:
                about_index = body.index("of")
                find_and_send_image(recipient,body[about_index+3:])
                resp.message("Image being retrieved")
                return str(resp)
            except ValueError:
                resp.message("Failed to fetch image, please ask like: 'image of [image]'")
                return str(resp)


    #If wolfram full results is the only thing we can do, continue with that
    resp.message(get_wolfram_full_results(body))
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=44,debug=True)