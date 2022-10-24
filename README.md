# CS50's Final Project: Gym Note
### Video Demo: 
### Idea 
The idea for Gym Note came from practical need for an easy and intuitive but also complete and precise way to track exercises throughout gym sessions. 
Many people, while in gym, have their personal notebooks or use simple notebook apps on their phones to write down their exercises. The advantage of such
solutions are mainly the ease of usage and freedom in creating personal customization.
This web app allows to keep those advantages, so every user can make it work for their personal needs, and in the same time it offers more organised way to save entries and presents all necessary data without unnecessary distractions. 
### Code structure
The main building blocks for this app are HTML and Python. Front-end is based on Bootstrap, from which various classes have found usage in creating the visual side of the site. Some changes to CSS were made in order to make the site more visible and aesthetically pleasing. Dark theme was chosen in order to make it more eye friendly. Everything is responsive to user's device and keeps all of the functionalities accessible irrespectively of the device's size. More about it can be found in demonstration video linked above.
Back-end is based mainly on Flask which among others takes care of template rendering, redirecting user to the proper page and keeping user's data in a session to allow more feature to be possible after logging in. CS50's library is also used to operate on database using SQLite queries. Workzeug's library allows for making the app more secure and keeps users passwords in the database in a hashed format. 
### Specification
#### Homepage
Homepage allows you to choose from three buttons in the navigation bar. On 'Home' site there is quick introduction to the application and links allowing user to log in or register. 'Log in' is a simple form for logging the user in and 'Register' is a bit more compound form, which demands more information for registration purposes. Apart from the regular username, password and password confirmation fields the user needs to provide a 'Safety question' and 'Answer' to it for the case in which he forgets his password and needs to reset it to get access to his account. 
#### User's main page
After logging in user is redirected to his main page which welcomes him with an alert message. Taking advantage of time library, app informs the user of a current date and whether or not he has planned any exercises for this day of the week. Using the navigation bar he can log out from his account, go to account settings to change his password or safety question or go back from any other page using the 'Gym Note' logo button.
First three buttons 'Create new training', 'Delete training' and 'Train' allow the user to insert, update and delete his workouts data from the database.  