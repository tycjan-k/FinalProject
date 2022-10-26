# CS50's Final Project: Gym Note
### Video Demo: 
### Idea 
The idea for Gym Note came from practical need for an easy and intuitive but also complete and precise way to track exercises throughout gym sessions. 
Many people, while in gym, have their personal notebooks or use simple notebook apps on their phones to write down their exercises. The advantage of such
solutions are mainly the ease of usage and freedom in creating personal customization.
This web app allows to keep those advantages, so every user can make it work for their personal needs, and in the same time it offers more organised way to save entries and presents all necessary data without unnecessary distractions. 
### Code and template structure.
The main building blocks for this app are HTML and Python. Front-end is based on Bootstrap, from which various classes have found usage in creating the visual side of the site. Some changes to CSS were made in order to make the site more visible and aesthetically pleasing. Dark theme was chosen in order to make it more eye friendly. Everything is responsive to user's device and keeps all of the functionalities accessible irrespectively of the device's size. More about it can be found in demonstration video linked above.
Back-end is based mainly on Flask which among others takes care of template rendering, redirecting user to the proper page and keeping user's data in a session to allow more feature to be possible after logging in. CS50's library is also used to operate on database using SQLite queries. Workzeug's library allows for making the app more secure and keeps users passwords in the database in a hashed format. 
#### app.py
In this file, according to Flask's requirements, all of the apps main functions are located. Starting from the core register, login and logout functions to the more specific dealing with JavaScript fetch requests. Below the more developed ones are described.
##### register
If the form is submited it ensures that every field was correctly filled, or else it returns to the register page with an error message. It also looks whether username is already taken and whether or not the password matches the confirmation. If the request is GET the function just renders the page template. 
##### login
With GET request it renders the page template. With submitting the form it checks whether every field is filled, compares given password to the one assigned to the given username and if they match it logs the user in with a welcome message. 
##### train
With GET request it renders the page template with data for the specific training type that the user has chosen on his main page. With form being submitted it ensures that every field has been filled, adds to it the current date and the number of sets that have been completed on a given day. If data is saved successfully it gives the user adequate feedback.
##### new
After submitting the form in 'Create new training' page it ensures that user provided all of the needed data including only one type information, it being chosen from the list or provided as a new custom type. 
##### filtr and filtype
Both functions are complementary to each other. They allow for two step filtering in 'Your past trainings' tab by communicating with the JavaScript of the website. First filtype returns to the site all trainings of a chosen type to create a select menu for the user, then filtr returns one of the two page templates to create the table with appropriate data in it. If the chosen value is a specific training ID it returns only said training's data, if the value is 'all' it returns all of the trainings from given type.
##### progressroute 
It's a function used to create a table informing the user whether or not he has made a progress in his workouts. After getting the request from website's JavaScript with a training ID in it, the function then calculates and compares all of the previous results of this training. To each training day it assigns a value 'val' ensuing from the weight and repetitions made on a given day compared to the previous one. It also assigns different value to user's first training and to his best one. Value is returned to the webiste, along with the training date and weight and repetition results, in a form of a list of a dictionaries to make it possible for website's Jinja code to interpret it to give the user correct information.
##### forgot
This function enables a feature to access the account when the user forgets his password. It's based on a old school security question and answer method. Here answer basically works as a secondary password letting the user log in without the password he might've forgotten. The function itself first makes a get request for the username and then renders page template with a question assigned to this username. If the form is submitted it compares username and answer provided to those in the database and if they match it logs user in and redirects him to the page where he can create a new password in place of a forgotten one. If the given answer doesn't match the one in the database it flashes the user with a error message. 
#### Pages specification
##### Homepage
Homepage allows you to choose from three buttons in the navigation bar. On 'Home' site there is quick introduction to the application and links allowing user to log in or register. 'Log in' is a simple form for logging the user in and 'Register' is a bit more compound form, which demands more information for registration purposes. Apart from the regular username, password and password confirmation fields the user needs to provide a 'Security question' and 'Answer' to it for the case in which he forgets his password and needs to reset it to get access to his account. 
##### User's main page
After logging in user is redirected to his main page which welcomes him with an alert message. Taking advantage of time library, app informs the user of a current date and whether or not he has planned any exercises for this day of the week. Using the navigation bar he can log out from his account, go to account settings to change his password or security question or go back from any other page using the 'Gym Note' logo button.
First three buttons 'Create new training', 'Delete training' and 'Train' allow the user to insert, update and delete his workouts data from the database. The remaining two buttons 'Your past trainings' and 'Progress tracker' let the user to view his past entries, depending on which type or which exercise he wants to see.
##### Create new training
Creates the overall type of training in which the user wants to make entries. He can choose the type from the provided list or create his own custom type. Exercise name is a specific exercise in a given type. It needs to be provided to make things easier in other features, as the user will just choose this exercise from the ones filtered among the same type. Additionally user can specify a 'Training day' for an exercise so he can be reminded of it on a given day. 
##### Delete training
This feature allows for a quick and easy deletion of any unwanted trainings from user's database. It's build in a collapse button and requires only two clicks to delete a specific training. 
##### Train
Under the Train button is a menu of all of the user's training types, he needs to choose one of them to proceed. When in training page user obligatory needs to fill in the name, weight and repetitions fields as they are the core components of the database. Duration and additional notes are not obligatory and can be used depending on user preferences. Form is being send to the application which saves it in the database.
##### Your past trainings
This tab is a simple table showing the user all the saved information about his previous workouts. He can choose to filter specific type or exercise. Table uses JavaScript to communicate with the server and immediately show the user the filtered results from his trainings. 
##### Progress tracker
Progress tab allows the user to better compare the results of a specific exercise, it shows whether or not he made improvement in his training on a day to day basis based on average amount of weight lifted and repetitions made. Beside the progress or regress information the table can show the first time the user exercised and when he made his best result. If the result is different than a previous one but is not cleary a progress or a regress, there is a possible 'Mix up' option that makes it known that some changes in doing the exercise were made.