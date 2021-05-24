"""Here we will pre process a pdf script  """
# This Python file uses the following encoding: utf-8
import pandas as pd
import os
import requests
import boto3
import random
import json
import codecs
import string
import numpy as np
from matplotlib import pyplot as plt
# from sklearn.cluster import KMeans
import re
import math
import sys
# import groupdocs_conversion_cloud
#import urllib

# library's for ML that compute the distance between sentences
#from scipy import spatial
#from sent2vec.vectorizer import Vectorizer
import textdistance

#client = boto3.client('s3', 'us-east-2') # With Credentials
client = boto3.client('s3') # With Credentials

session = boto3.Session(
    aws_access_key_id='AKIAJPH5OEC3JDFW5CSA',
    aws_secret_access_key='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',
    region_name='us-east-2'
)
s3 = session.resource('s3')
bucket = s3.Bucket('imgn')


def from_int_to_string(num):
    s = str(num)
    return s

def from_string_to_int(str):
    n = int(str)
    return n

def from_sentence_to_str(sentence):
    s = str(sentence)
    return s

def findWholeWord(w):
    w = w.strip()
    w = w.casefold()
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def cleanEnd(word):
    endchar = word[len(word)-1]
    if re.search('\W', endchar) != None:
        cleanword = ""
        for i in range(len(word)-1):
            cleanword += word[i]
        cleanword = cleanword.strip()
        return cleanword
    else:
        return word

def end_with_space(str):
    return str.endswith(' ')

def end_with_number(str):
    num = ""
    num = re.search('\d\d\d|\d\d|\d', str)
    if num == None:
        return False
    else:
        return num.group()

def reversed_string(a_string):
    new_strings = []
    index = len(a_string) - 1
    leter_found = False
    signs = ""
    while not leter_found and index:
        if re.search('\w', a_string[index]) is not None:
            leter_found = True
            index += 1
        else:
            signs += a_string[index]
            index -= 1
    a_string_no_signs = ""
    for i in range(index):
        a_string_no_signs += a_string[i]


    while index:
        index -= 1
        new_strings.append(a_string_no_signs[index])

    new_strings.append(signs)
    return ''.join(new_strings)


# here we group scene using name proximity
def scenes_grouping(file_path_json, folder, filename_json, file_path_json_ret, filename_json_ret):

    json_data = {}

    file_obj = None
    url = file_path_json
    try:
        # Create random file path
        n = random.randint(100000, 999999);
        s = from_int_to_string(n)
        file_name_json = "./DataImgn/Download/" + s + ".json"
        #file_name = filename

        #r = requests.get(url)
        response = client.get_object(
            Bucket='imgn',
            Key=folder+'/'+filename_json
        )

        if not os.path.exists('./DataImgn'):
            os.makedirs('./DataImgn')
        if not os.path.exists('./DataImgn/Download'):
            os.makedirs('./DataImgn/Download')
        with open(file_name_json, 'wb') as file_obj:
            #file_obj.write(r.content)
            file_obj.write(response['Body'].read())
            file_path_json = file_name_json
            is_download = True

    except IOError:
        i = 0
    finally:
        if (file_obj):
            file_obj.close()

    f = None
    try:
        with open(file_name_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            #json_data = json.loads(f, encoding="UTF-8")
    except IOError:
        i = 0
    finally:
        if (f):
            f.close()

    #json_data = json.loads(scenes)
    #print("scenes", json_data)
    sentences = []
    for scene in json_data:
        # print("scene", scene['name'], scene['scene_id'])
        clean_name = re.sub('["]', '', scene['name'])
        clean_name = re.sub("'", '', clean_name)
        clean_name = re.sub("’", '', clean_name)
        clean_name = re.sub('\W', " ", clean_name)
        clean_name = ' '.join(clean_name.split())
        clean_name = clean_name.strip()
        sentences.append(clean_name)
    #vectorizer = Vectorizer()
    #vectorizer.bert(sentences)
    #vectors_bert = vectorizer.vectors
    distances = []

    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if j > i:
                #distances.append((i, j, spatial.distance.cosine(vectors_bert[i], vectors_bert[j])))
                distances.append((i, j, textdistance.entropy_ncd(sentences[i], sentences[j])))
    distances.sort(key=lambda tup: tup[2], reverse=False)
    """
    for dist in distances:
        print("dist", dist)
    """
    groups = [[distances[0][0], distances[0][1]]]
    grouped_index = [distances[0][0], distances[0][1]]
    groups_set = []
    i = 0
    scene_counter = 2
    # grouping all the identical scene names
    while scene_counter < len(sentences) and i < len(distances) and distances[i][2] == 0:
        flag_found_group = False
        j = 0
        while j < len(groups) and not flag_found_group and distances[i][2] == 0:
            if distances[i][0] in groups[j] or distances[i][1] in groups[j]:
                if distances[i][0] not in groups[j]:
                    groups[j].append(distances[i][0])
                    grouped_index.append(distances[i][0])
                    scene_counter += 1
                if distances[i][1] not in groups[j]:
                    groups[j].append(distances[i][1])
                    grouped_index.append(distances[i][1])
                    scene_counter += 1
                flag_found_group = True
            j += 1
        if not flag_found_group:
            groups.append([distances[i][0], distances[i][1]])
            grouped_index.append(distances[i][0])
            grouped_index.append(distances[i][1])
            scene_counter += 2
        i += 1

    # group similar groups
    i = 0
    try:
        while i < len(groups):
            j = 0
            while j < len(groups):
                if i != j:
                    matches = 0
                    for word in sentences[groups[i][0]].split():
                        if word in sentences[groups[j][0]]:
                            matches += 1
                    if matches > 1 and textdistance.entropy_ncd(sentences[groups[i][0]], sentences[groups[j][0]]) < 0.07:
                        for index in groups[j]:
                            groups[i].append(index)
                        groups.remove(groups[j])
                    else:
                        j += 1
                else:
                    j += 1
            i += 1
    except:
        pass

    # groping the similar sentences to there best group fit
    for i in range(len(sentences)):
        if i not in grouped_index:
            min_dis = 1
            min_index = 0
            group_num = 0
            for group_num in range(len(groups)):
                sentence_to_group = sentences[i]
                rep_from_group = sentences[groups[group_num][0]]
                sentence_to_group_split = sentence_to_group.split()
                rep_from_group_split = rep_from_group.split()
                matches = 0
                for word in sentence_to_group_split:
                    if word in rep_from_group_split:
                        matches += 1
                if textdistance.entropy_ncd(rep_from_group, sentence_to_group) < min_dis and matches > 1:
                    min_dis = textdistance.entropy_ncd(rep_from_group, sentence_to_group)
                    min_index = group_num
            best_rep = sentences[groups[min_index][0]]
            if min_dis < 0.1:
                groups[min_index].append(i)
            else:
                groups.append([i])
            grouped_index.append(i)

    # sorting the groups by proximity of an element from group1 and group 2
    i = 1
    index_min = 0
    groups_sorted = [groups[index_min]]
    while i < len(groups):
        min_group_dist = 1
        sentence_index = groups[index_min][0]
        groups.remove(groups[index_min])
        sen_group = sentences[sentence_index]
        matches = 0
        match_found = False
        for j in range(len(groups)):
            if index_min != j:
                for sen_index in range(len(groups[j])):
                    sen = sentences[groups[j][sen_index]]
                    for word in sen_group.split():
                        if word in sen:
                            matches += 1
                    if textdistance.entropy_ncd(sentences[sentence_index], sen) < min_group_dist and matches > 0:
                        min_group_dist = textdistance.entropy_ncd(sentences[sentence_index], sen)
                        index_min = j
                        match_found = True
        if not match_found:
            for j in range(len(groups)):
                if index_min != j:
                    for sen_index in range(len(groups[j])):
                        sen = sentences[groups[j][sen_index]]
                        if textdistance.entropy_ncd(sentences[sentence_index], sen) < min_group_dist:
                            min_group_dist = textdistance.entropy_ncd(sentences[sentence_index], sen)
                            index_min = j

        groups_sorted.append(groups[index_min])

    for i in range(len(groups_sorted)):
        groups_set.append(set(groups_sorted[i]))

    # Building the json file
    final_groups = []
    counter = 0
    sentences_index = []
    for i in range(len(groups_set)):
        final_groups.append([])
        for index in groups_set[i]:
            counter += 1
            print("group", i, sentences[index], counter)
            final_groups[i].append(json_data[index])
            sentences_index.append(index)
        print("----------------------end group------------------------")
    print("number of scenes grouped", counter)
    print("len sentences", len(sentences))
    print("len sentences index", len(sentences_index))

    grouped_index.sort()
    print("grouped index", grouped_index)
    print("len grouped index", len(grouped_index))
    print("-----sentences not grouped-------")
    cu = 0
    for i in range(len(sentences)):
        if i not in sentences_index:
            cu += 1
            print("not grouped", cu, sentences[i])

    # print("final_groups", final_groups)
    final_groups_dict = {}
    final_groups_dict.update({'groups': final_groups})
    # print("final_groups_dict", final_groups_dict)
    json_data = json.dumps(final_groups_dict, ensure_ascii=False).encode('utf-8')
    # return a 2d array
    # [[scene1, scene3, ...],[...]]

    try:
        os.remove(file_path_json)
    except:
        pass

    try:

        # s3 = boto3.resource('s3')
        # obj = s3.Object('imgn', folder+'/'+filename_json_ret)
        # obj.put(Body=json.dumps(json_data))

        bucket.put_object(Key=folder+'/'+filename_json_ret, Body=json_data)

        # response = client.put_object(
        #     Bucket='imgn',
        #     Body=json_data,
        #     Key=folder+'/'+filename_json_ret
        # )
        #Body = str(json.dumps(json_data)),
    except IOError:
        pass

    return json_data

