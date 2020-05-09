# CSC 322(Software Engineering Project)

# Active Teaming System

This system will facilitate active teaming of people with similar interest and skill-set to forge groups for a certain do-good project. There are three types of users in this system: Super User (SU), Ordinary User (OU) and Guest (GU).

## Specifications
**Super User(SU)** can:
- [x] update membership.
- [x] maintain a list of taboo words.
- [x] unlock any locked document.
- [x] process complaints about OU's.
- [x] have all privileges reserved for OU's inside any group.

**Ordinary User(OU)** can:
// need to write

**Guest User (GU)** can:
// need to write

**General Features:**
//need to write

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Prerequisites

* [Python3](https://www.python.org/downloads/)

### Installing

After successfully installing python we might need to install modules to successfully run this software: Flask-sqlalchemy, flask-bcrypt, flask- login, Pillow, flask-wtf and finally email-validator.   A step by step series of examples on the installation guide are as follows:

-----------------------OnN MAC---------------------------------
# TO START
source env/bin/activate
python3 app.py

------------------------ON WINDOWS------------------------------
pip3 install virtualenv
```

```
virtualenv env
```

```
run env\Scripts\activate
```
```
pip3 install flask-sqlalchemy
```
```
pip3 install flask-bcrypt
```
pip3 install flask-login

pip3 install Pillow

pip3 install flask-wtf

pip3 install email-validator

## Built With

* [Flask] - The python3 API used
* [csv]- Database Management
* [draw.io] - To draw use-cases


## Authors

Haibin Mai
Junior Norabuena
Sambeg Raj Subedi


See also the list of [contributors]