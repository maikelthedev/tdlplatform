# This creates new tests and stores them in a remote mongdodb.

import click
from pymongo import MongoClient
import datetime
import random
import configparser


# First lets create a click command to create one
@click.group()
def create():
    pass


# Don't forget to cover the password, find it in click documentation
@create.command()
@click.option('--host_name', prompt="Host Name")
@click.option('--db_name', prompt="DB Name")
@click.option('--user_name', prompt="User")
@click.option('--password', prompt="Password")
def configdb(host_name, db_name, user_name, password):
    """Sets up the database to use"""
    # Check if there is a valid config if not then go ahead, otherwise tell the user
    if check_config():
        print("There is already a configuration")
        ask = input("Do you want to overwrite it? [y/n]")
        if ask.lower() != "y":
            print("No change has been made")
            return

    # Reconfig
    client = MongoClient(host_name, 27017)
    db = client[db_name]
    try:
        connect = db.authenticate(user_name, password)
        print('It works and you\'re in')

    except (Exception):
        print("You can't access that server or database")
        return

    config = configparser.ConfigParser()
    config['SERVER'] = {
        "host_name": host_name,
        "db_name": db_name,
        "user_name": user_name,
        "password": password
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print("Configuration saved!")

def check_config():
    config = configparser.ConfigParser()
    if config.read('config.ini') == []:
        return False
    else:
        return True

def connect():
    config = configparser.ConfigParser()
    config.read('config.ini')
    host_name = config['SERVER']['host_name']
    db_name = config['SERVER']['db_name']
    user_name = config['SERVER']['user_name']
    password = config['SERVER']['password']
    client = MongoClient("mongodb://" + user_name + ":" + password + "@" + host_name + ":27017")
    db = client[db_name]
    return db


@create.command()
def edittest():
    """Edits an already existing test or creates a new test"""
    if check_config() == False:
        print("No DB configured")
        return
    db = connect()
    selected_skill = skill_selector(db)

    selected_page = page_selector(selected_skill, db)
    cursor = db.pages.find({"skill": selected_skill, "title": selected_page})
    for document in cursor:
        print("Your choice is:\t", document['title'])
    if 'test' in document:
        print("This test already has", len(document['test']), "questions")
    add_questions(selected_page, selected_skill, db)
    cursor = db.pages.find({"skill": selected_skill, "title": selected_page})
    for document in cursor:
        ledocument = document
    print("This page has now:", len(ledocument['test']), "questions")


def skill_selector(db):
    print('Select a skill')
    # First show all the skills and select one
    cursor = db.skills.find()
    choice = []
    index = 1
    for document in cursor:
        choice.append(document['title'])
        print(str(index) + ")", document['title'])
        index += 1
    user_answer = int(input("Please select a skill: ")) - 1
    selected_skill = choice[user_answer]
    return selected_skill


def page_selector(selected_skill, db):
    # Show the pages of that skill and which one have a test already
    cursor = db.pages.find({"skill": selected_skill})
    print("Has a test\t\tTitle")
    choice = []
    index = 1
    for document in cursor:
        choice.append(document['title'])
        print(str(index) + ")", 'test' in document, "\t", document["title"])
        index += 1
    user_answer = int(input("Please select a skill: ")) - 1
    selected_page = choice[user_answer]
    return selected_page


def add_questions(selected_page, selected_skill, db):
    choice = "y"
    while choice == "y":
        question = input("The question:")
        print("The question is:", question)
        print("You can introduce as many answers as you want, to stop type one spacebar then intro")
        user_input = ""
        answers = []
        while user_input != " ":
            user_input = input("Answer:")
            if user_input == " ":
                break
            else:
                answers.append(user_input)
        print("These are the answers:")
        index = 0
        for answer in answers:
            print(str(index + 1) + ")", answer)
            index += 1
        correct_answer = int(input("Which one is the correct one: ")) - 1
        question_and_answers = {
            "question": question,
            "answers": answers,
            "correct_index": correct_answer
        }

        results = db.pages.update(
            {"skill": selected_skill, "title": selected_page},
            {"$push": {"test": question_and_answers}}
        )
        choice = input("Do you want to add another question [y/n]:").lower()


@create.command()
def testme():
    """Tests your knowledge of a page"""
    if check_config() == False:
        print("No DB configured")
        return
    db = connect()
    selected_skill = skill_selector(db)
    selected_page = page_selector(selected_skill, db)
    cursor = db.pages.find({"skill": selected_skill, "title": selected_page})
    for document in cursor:
        if 'test' in document:
            tests = document['test']
        else:
            print("There are no tests for that page")
            return

    # This should be limited to 20 questions, don't forget to change that.
    totals = 0

    if len(tests) < 20:
        print("Can't test you while the tests are less than 20")
        print("Currently the page has only", len(tests), "tests")
        return
    selected = random.sample(tests, 20)
    for test in selected:
        print()
        print(test['question'], "\tCurrent Score:", totals)
        dash = "-" * len(test['question'])
        print(dash)
        answers = test['answers']
        for answer in answers:
            print(str(answers.index(answer) + 1) + ") " + answer)
        user_answer = int(input("Please enter the index of the right answer: ")) - 1

        if user_answer == test['correct_index']:
            totals += 1
            print("Right answer, your points are: " + str(totals) + " points")
        else:
            print("Wrong answer, moving on")

    # From here is about what to do with the test:
    now = datetime.datetime.now()

    # This uploads the results
    results = db.pages.update(
        {"skill": selected_skill, "title": selected_page},
        {"$push": {"scores": {"score": totals, "date": now}}}
    )
    print()
    print("You got:", totals, "questions correct out of 20")
    percentage = str(round(totals / 20 * 100)) + "%"
    print("That's a score of", percentage, "right")


@create.command()
def testskill():
    """Tests a whole skill by taking a sample from different pages"""
    if check_config() == False:
        print("No DB configured")
        return
    db = connect()
    selected_skill = skill_selector(db)
    tests = []
    cursor = db.pages.find({"skill": selected_skill})
    for document in cursor:
        if 'test' in document:
            tests.extend(document['test'])
    if len(tests) < 20:
        print("Can't test you while the tests are less than 20")
        print("Currently the skill has only", len(tests), "tests")
        return
    totals = 0
    selected = random.sample(tests, 20)
    for test in selected:
        print()
        print(test['question'], "\tCurrent Score:", totals)
        dash = "-" * len(test['question'])
        print(dash)
        answers = test['answers']
        for answer in answers:
            print(str(answers.index(answer) + 1) + ") " + answer)
        user_answer = int(input("Please enter the index of the right answer: ")) - 1

        if user_answer == test['correct_index']:
            totals += 1
            print("Right answer, your points are: " + str(totals) + " points")
        else:
            print("Wrong answer, moving on")

    # From here is about what to do with the test:
    now = datetime.datetime.now()

    # This uploads the results
    results = db.skills.update(
        {"title": selected_skill},
        {"$push": {"scores": {"score": totals, "date": now}}}
    )
    print()
    print("You got:", totals, "questions correct out of 20")
    percentage = str(round(totals / 20 * 100)) + "%"
    print("That's a score of", percentage, "right")
    if totals <= 15:
        level = "Learning"
    else:
        level = "Familiar"

    mastery = db.skills.update(
        {"title": selected_skill},
        {"$set": {"mastery": level}}
    )
    print("Level updated to:", level)


if __name__ == '__main__':
    create()
