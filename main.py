#!/usr/bin/env python3
import requests,json
from discord import SyncWebhook, Webhook
from time import sleep

def post_to_channel(repl_dict,webhook):
    #when the API call returns a tweet without any media attached to it the json object returns an object by the len of 1 (see tweet.json) if there is a object of len 2 there is media attached (photo.json)
    #seperates the media types and posts the url to the webhook to Discord
    if len(repl_dict) != 1:
        for i in range(0,len(repl_dict["includes"]["media"])):
            typ = repl_dict["includes"]["media"][i]["type"]
            if typ == "photo":
                webhook.send(repl_dict["includes"]["media"][i]["url"])
            elif typ == "video":
                webhook.send(repl_dict["includes"]["media"][i]["variants"][1]["url"])
            elif typ == "animated_gif":
                webhook.send(repl_dict["includes"]["media"][i]["variants"][0]["url"])


def get_twt_id(name,headers,webhook):
    #calls the most recent tweets of the $name variable and returns only the id of the latest tweet (the id is the value pair of answer_dict["data"][0]["id"])

    url = f"https://api.twitter.com/2/tweets/search/recent?query=from%3A{name}"
    response = requests.request("GET",url,headers=headers) #with HTTP GET and authorization in the headers calls API
    while response.status_code != 200:
        sleep(900)
        response = requests.request("GET",url,headers=headers) #with HTTP GET and authorization in the headers calls API
    answer = response.content.decode() #turns byte stream into str
    answer_dict = json.loads(answer) #turns str to python dict
    if len(answer_dict["meta"]) == 1:
        return (0,0)
    else:
        try:
            id1 = int(answer_dict["data"][0]["id"])
            try:
                id2 = int(answer_dict["data"][1]["id"])
                return (id1,id2)
            except:
                return (id1,0)
        except:
            return (0,0)

def posts(id_list,compare_list):
    #compares the ids in the id_dict with the compare_dict to see which new posts were created and only returns a list with only the  ids of the new posts

    post_list = []
    for twt_id in id_list:
        if twt_id != 0:
            if twt_id not in compare_list:
                post_list.append(twt_id)
        else:
            continue
        
    return post_list


def get_reply(post_list, headers, webhook):
    #each tweet gets polled with their id (variable $twt_id) and the the answer gets passed to the post_to_channel() function
    for twt_id in post_list:

        tweetlookup = f"https://api.twitter.com/2/tweets?ids={twt_id}&expansions=attachments.media_keys&media.fields=duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width,alt_text,variants"
        tweetresp = requests.request("GET",tweetlookup,headers=headers) #with HTTP GET and authorization in the headers calls API
        while tweetresp.status_code != 200:
            sleep(900)
            tweetlookup = f"https://api.twitter.com/2/tweets?ids={twt_id}&expansions=attachments.media_keys&media.fields=duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width,alt_text,variants"
            tweetresp = requests.request("GET",tweetlookup,headers=headers) #with HTTP GET and authorization in the headers calls API                
        repl = tweetresp.content.decode() #turns byte stream into str
        repl_dict = json.loads(repl) #turns str to python dict
            
        post_to_channel(repl_dict=repl_dict,webhook=webhook)


def main():
        #setup default environment
        webhook = SyncWebhook.from_url("") #add your own webhook url from discord
        bear_token=r"" # place bearer token here
        headers = {"Authorization": f"Bearer {bear_token}"}
        log = open("log.txt",mode="a")
        at = [] #add your twitter users (only the part after the @)

        compare_list = []
        id_dict = {}
        for name in at:
            id_dict[name] = ""

        while True:
            try:
                current_id_list = []

                for name in at:
                    id_dict[name] = get_twt_id(name=name,headers=headers,webhook=webhook)#get id of latest tweets
                    current_id_list.append(id_dict[name][0])
                    current_id_list.append(id_dict[name][1])
                
                current_id_list.sort()
                compare_list.sort()

                if current_id_list != compare_list: #if the compare_dict and id_dict is the same no new posts were created so the script goes to sleep in line 86
                    post_list = posts(id_list=current_id_list,compare_list=compare_list)
                    get_reply(post_list=post_list,headers=headers,webhook=webhook)
                    compare_list.clear()
                    for twt_id in current_id_list:
                        compare_list.append(twt_id)
                    sleep(900)
                else:
                    sleep(900) #i schleep
            except Exception as error:
                webhook.send("Error, check log for more Info")
                log.write(f"{error}\n")
                log.close()
                break


if __name__ == "__main__":
    main()