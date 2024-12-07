### INF601 - Advanced Programming in Python
### Davon Morris
### Mini Project 4


# Mini Project 4 - Django

## Description

This project demonstrates building a web application using [Django](https://www.djangoproject.com/), a high-level Python web framework that encourages rapid development and clean, pragmatic design. 

The application allows users to manage their card collection, with features to create collections, add cards to collections, and view their collection.


## Getting Started

### Dependencies

```
pip install -r requirements.txt
```
### Installing

* Clone my repository to your IDE configured to run Python 3.12

### Setup Database

```
cd tcgapp

python manage.py migrate 
```

### Create Administrator
```
python manage.py createsuperuser
```

### Start Website

```
python manage.py runserver
```



### Go to website [http://localhost:8000/](http://localhost:8000/)

### For your first time, click register at the top right, or login using the credentials you chose for your superuser Admin account:


1. ### You will arrive at the home page for your collections.

2. ### Click the blue "Add Collection" button on the top right


3. ### Choose a collection name, and then click "Add Collection"


4. ### You will be taken back to the home page, go ahead and click the name of your collection that you just added.


5. ### Add your first card by typing a name into the input box that says "Enter new card name", and choose the quantity(default is 1)


6. ### When you are done adding cards, click save at the bottom left, and Go Home


7. ### You have now successfully created a collection and added cards to it.

8. ### If you would like to be in dark mode, click on the sun symbol at the top right, and it will switch to dark mode, the same applies if you would like to switch back to light mode

9. ### If you would like to remove a collection, click the red "Remove" button on the right side of the collection, and confirm that you would like to remove it.

10. ### If you would like to remove cards from a collection, click the red "Remove" button on the right side of the card, and then click save at the bottom left.



## Authors

Davon Morris

## Acknowledgments

[Django Documentation](https://docs.djangoproject.com/en/5.1/)

[Django Tips](https://code.tutsplus.com/10-insanely-useful-django-tips--net-974t)

[Set Login Required for Generic Views](https://stackoverflow.com/questions/2140550/how-to-require-login-for-django-generic-views)

[Crispy Forms](https://simpleisbetterthancomplex.com/tutorial/2018/08/13/how-to-use-bootstrap-4-forms-with-django.html?utm_source=youtube&utm_medium=video_description&utm_campaign=django_auth_tutorial&utm_content=channels)

[Bootstrap Documentation](https://getbootstrap.com/docs/4.5/getting-started/introduction/) - For styling and layout of the web pages.

[Stack Overflow](https://stackoverflow.com/) - For answering specific questions and providing solutions to coding challenges.


[W3Schools](https://www.w3schools.com/) - For clear and concise explanations of web development technologies.
