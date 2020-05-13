# CSC 322(Software Engineering Project)

# Active Teaming System

This system will facilitate active teaming of people with similar interest and skill-set to forge groups for a certain do-good project. There are four types of users in this system: Super User (SU), Ordinary User (OU)., VIPs and Visitors.

## Specifications
**Super User(SU)** can:
- [x] update membership.
- [x] maintain a list of taboo words.
- [x] shutdown group or punish OUs by score reduction.
- [x] process complaints about OU's.
- [x] have all privileges reserved for OU's inside any group.

**Ordinary User(OU)** can:
- [x] can form group by inviting other OUs.
- [x] put other OUs in Whitebox or Blackbox.
- [x] can moderate and post to the group page.
- [x] ask for meetup polling to find common time for all members to meet.
- [x] group members can vote to issue warning/praise/kickout/close a group.
- [x] can complains to SU about group or other OUs.
- [x] can send compliments about OUs to SU.

**Guest User (GU)** can:
- [x] view top 3 projects and top rating OUs profile.
- [x] register to be OU.
- [x] complain to SU about group or OUs.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Prerequisites

* [Python3](https://www.python.org/downloads/)

### Installing

After successfully installing python we might need(for windows) to install modules to successfully run this software: Flask-sqlalchemy, flask-bcrypt, flask- login, Pillow, flask-wtf and finally email-validator.   A step by step series of examples on the installation guide are as follows:

-----------------------ON MAC-----------------------------

# TO START
- [x] source env/bin/activate
- [x] python app.py

------------------------ON WINDOWS------------------------

# TO START

- [x] .\Scripts\activate

- [x] python app.py

## Built With

* [Flask] - The python3 API used
* [csv]- Database Management
* [draw.io] - To draw use-cases


## Authors

Haibin Mai
Junior Norabuena
Sambeg Raj Subedi


See also the list of [contributors]
Click here:
https://github.com/Ivan-bin/csc322
