### INF601 - Advanced Programming in Python
### Davon Morris
### Final Project
---
# Final Project - Django

## Description

This project demonstrates building a web application using [Django](https://www.djangoproject.com/), a high-level Python web framework that encourages rapid development and clean, pragmatic design. 

The application allows users to manage their card collection, with features to create collections, add cards to collections, and view their collections.

I use the [Scryfall](https://scryfall.com/docs/api) to search for cards, grab details, and add them to the user's collection

---
## Getting Started

### Dependencies

* Clone my repository to your IDE configured to run Python 3.12



```
pip install -r requirements.txt
```
### Installing


### Setup Database

```
cd tcgapp
python manage.py makemigrations
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

---

## Using the Site

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


---
## Authors

#### Davon Morris

---

## Acknowledgments

### Magic The Gathering

&nbsp;[Magic The Gathering](https://magic.wizards.com/en) - None of this would be possible without Magic The Gathering  being a thing.

&nbsp;[Scryfall](https://scryfall.com/docs/api) - REST-like API that allows requests to be made to query [MTG](https://magic.wizards.com/en) Data such as cards, sets, etc.



### Python

&nbsp;[General - Stack Overflow](https://stackoverflow.com/) - For answering specific questions and providing solutions to coding challenges.

### Django

&nbsp;[Django Documentation](https://docs.djangoproject.com/en/5.1/) - Documentation from the Django website directly

&nbsp;[Crispy Forms](https://django-crispy-forms.readthedocs.io/en/latest/) - Makes forms in Django look nice and a bit easier to configure

&nbsp;[Django Tips](https://code.tutsplus.com/10-insanely-useful-django-tips--net-974t) - Some tips that are useful

&nbsp;[Set Login Required for Generic Views](https://stackoverflow.com/questions/2140550/how-to-require-login-for-django-generic-views) - Helped me figure out how to set Login Required for Generic Views


### CSS

&nbsp;[Bootstrap](https://getbootstrap.com/docs/4.5/getting-started/introduction/) - For styling and layout of the web pages.

&nbsp;[Bootstrap Grid](https://getbootstrap.com/docs/4.0/layout/grid/) - Used for the smaller view of the card collection

&nbsp;[Bootstrap Table](https://getbootstrap.com/docs/4.0/content/tables/) - Used for table designs in the website

&nbsp;[W3Schools](https://www.w3schools.com/css/default.asp) - For clear and concise explanations of web development technologies.

&nbsp;[Dark Theme Suggestions/Principals](https://m2.material.io/design/color/dark-theme.html) - Helped me design my dark mode

&nbsp;[Detect Dark Mode](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme) - Points to what theme the user is using, allowing us to automatically apply light or dark themes

&nbsp;[Specificity](https://www.w3schools.com/css/css_specificity.asp) - Higher specificity wins, and applies its theme

&nbsp;[Media Queries](https://www.w3schools.com/css/css3_mediaqueries.asp) - Allows the ability to define different style rules for different media types.
