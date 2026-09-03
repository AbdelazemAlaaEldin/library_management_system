**# 📚 The Reading Room — Library Management System**

A modern Django-based Library Management System designed to provide a simple,

interactive, and visually engaging experience for both library members and

librarians.

The project combines Django's backend capabilities with HTML, CSS, and

JavaScript to create a complete library workflow including authentication,

book browsing, searching, borrowing, returning, and loan management.

\---

**## ✨ Project Overview**

**\*\*The Reading Room\*\*** is a web-based Library Management System developed as a

team project.

The system allows registered members to:

\- Create a library account

\- Log in and log out securely

\- Browse the available book collection

\- Search for books

\- Filter books by category

\- Sort books in different ways

\- View detailed book information

\- Borrow available books

\- View their current borrowed books

\- Return borrowed books

\- Receive clear success and error messages

Librarians can manage the library's books and loans through Django's built-in

administration interface.

The project also includes several additional interface and user-experience

features such as book covers, an interactive library entrance, grid/list

views, and an ambient audio player.

\---

**## 🎯 Project Goals**

The main goals of the project are to:

\- Build a complete Django web application from scratch.

\- Apply Object-Oriented Programming and Python concepts in a real project.

\- Implement user authentication using Django's authentication system.

\- Design and implement relational database models.

\- Create a complete borrowing and returning workflow.

\- Practice frontend development using HTML, CSS, and JavaScript.

\- Implement client-side validation alongside server-side validation.

\- Work collaboratively using Git and GitHub.

\- Follow a structured development workflow from setup to testing and deployment-ready documentation.

\---

**#  Features**

**## 🔐 Authentication**

The system provides a complete authentication workflow.

**### Registration**

Users can create a new library account using:

\- Username

\- Email

\- Password

\- Password confirmation

The registration form includes:

\- Client-side validation using JavaScript

\- Required-field validation

\- Email format validation

\- Password confirmation validation

\- Django server-side validation

After successful registration, the user is automatically logged in.

**\*\*Screenshot Placeholder\*\***

\> \`![Registration](assets/screenshots/register.png)\`

\---

**### 🔑 Login**

Existing members can log in using Django's built-in authentication system.

The system also preserves the intended destination when appropriate,

allowing users to continue to the requested page after authentication.

**\*\*Screenshot Placeholder\*\***

\> \`![Login](assets/screenshots/login.png)\`

\---

**### 🚪 Logout**

Authenticated users can safely log out of their account.

After logout, the user is returned to the library entrance.

\---

**# 🏛️ Library Entrance**

The application includes a dedicated library entrance experience before users

enter the main collection.

The entrance provides options such as:

\- Sign in

\- Register

\- Continue as Guest

It also includes an animated visual experience designed around the library

theme.

**\*\*Screenshot Placeholder\*\***

\> \`![Library Entrance](assets/screenshots/entrance.png)\`

\---

**# 📚 Book Catalog**

Authenticated members can browse the library's collection of books.

Each book contains information such as:

\- Title

\- Author

\- ISBN

\- Category

\- Total copies

\- Available copies

\- Publication date

Books are managed through Django Admin.

**\*\*Screenshot Placeholder\*\***

\> \`![Book Catalog](assets/screenshots/catalog.png)\`

\---

**# 🔎 Search & Filtering**

The catalog includes search and filtering functionality.

Users can search by:

\- Book title

\- Author

\- ISBN

Users can also filter books by:

\- Category

\- Availability

The interface also supports sorting by:

\- Title

\- Author

\- Newest publications

The search/filter experience is designed to be fast and simple while

maintaining the visual style of the application.

**\*\*Screenshot Placeholder\*\***

\> \`![Search & Filters](assets/screenshots/search-filter.png)\`

\---

**# 📖 Book Details**

Users can open a book's details to view more information about the selected

book.

The details interface provides information about the book and its current

availability.

Book cover images are also supported through the project's cover image

system.

**\*\*Screenshot Placeholder\*\***

\> \`![Book Details](assets/screenshots/book-details.png)\`

\---

**# 📚 Borrowing System**

Members can borrow books directly from the catalog.

The borrowing system follows several important business rules.

**### Borrowing Rules**

A member can borrow a book only when:

1\. At least one copy is available.

2\. The member does not already have the same book borrowed.

When a book is successfully borrowed:

\- A new loan record is created.

\- The book's available copy count decreases by one.

\- The book appears in the member's active loans.

\- A success message is displayed.

**\*\*Screenshot Placeholder\*\***

\> \`![Borrowing](assets/screenshots/book-details.png)\`

\---

**## 🚫 Preventing Invalid Borrowing**

The system prevents users from borrowing the same book twice at the same

time.

It also prevents borrowing when all copies are currently unavailable.

Users receive clear feedback when a borrowing action cannot be completed.

Example:

\> All copies are currently borrowed. Please check back soon.

\---

**# 📋 My Loans**

Authenticated members can access a dedicated **\*\*My Loans\*\*** section.

This section displays the books currently borrowed by the logged-in member.

Each active loan contains information such as:

\- Book

\- Borrow date

\- Current loan status

\- Return action

**\*\*Screenshot Placeholder\*\***

\> \`![My Loans](assets/screenshots/my-loans.png)\`

\---

**# 🔄 Returning Books**

Members can return books that they currently have borrowed.

When a book is returned:

\- The loan status changes to \`Returned\`.

\- The return date is recorded.

\- The book's available copy count increases by one.

\- The book is removed from the member's active loans.

\- A success message is displayed.

A returned book can then be borrowed again if a copy is available.

**\*\*Screenshot Placeholder\*\***

\> \`![Return Book](assets/screenshots/return-book.png)\`

\---

**# ⚙️ Django Admin**

The project uses Django's built-in Admin interface for librarian management.

Librarians can manage:

**### Books**

\- Add books

\- Edit book information

\- Delete books

\- Manage copy counts

\- Manage categories

\- Manage ISBNs

\- Manage publication dates

**### Loans**

\- View loans

\- View borrowing members

\- View borrowed books

\- View borrowing dates

\- View return dates

\- View loan status

No custom administration dashboard was required for the core project.

**\*\*Screenshot Placeholder\*\***

\> \`![Django Admin](assets/screenshots/admin.png)\`

\---

**# 🎨 User Interface & Design**

The application was designed around a \*\*classic library aesthetic combined

with modern web interactions\*\*.

The visual identity uses:

\- Warm cream backgrounds

\- Dark brown typography

\- Olive accents

\- Brass/gold details

\- Serif display typography

\- Modern sans-serif UI typography

The design focuses on creating a recognizable library atmosphere while keeping

the interface readable and easy to use.

\---

**## 🖥️ UI Features**

The frontend includes several additional interface features:

\- Responsive-style layout

\- Book cards

\- Grid/List view switching

\- Interactive buttons

\- Hover effects

\- Animated library entrance

\- Book detail dialogs

\- Visual availability indicators

\- Styled success/error messages

\- Custom form styling

\- Custom audio player

\- Book cover presentation

**\*\*Screenshot Placeholder\*\***

\> \`![Main UI](assets/screenshots/catalog.png)\`

\---

**# 🎵 Ambient Audio Player**

The Reading Room includes an ambient audio player designed to enhance the

library atmosphere.

Available audio tracks include:

\- Cafe Corner

\- Fireplace Crackle

\- Night Garden

\- Piano Waltz

\- Rain Window

The player allows users to interact with the available ambient sounds while

using the library interface.

**\*\*Screenshot Placeholder\*\***

\> \`![Ambient Audio Player](assets/screenshots/audio-player.png)\`

\---

**# 🧩 Technologies Used**

**## Backend**

\- **\*\*Python\*\***

\- **\*\*Django\*\***

\- **\*\*SQLite\*\***

\- **\*\*Django Authentication\*\***

\- **\*\*Django ORM\*\***

\- **\*\*Django Admin\*\***

**## Frontend**

\- **\*\*HTML5\*\***

\- **\*\*CSS3\*\***

\- **\*\*JavaScript\*\***

**## Development Tools**

\- **\*\*Git\*\***

\- **\*\*GitHub\*\***

\- **\*\*Visual Studio Code\*\***

**## External Integration**

\- **\*\*Google Books API\*\*** for book cover-related functionality.

\---

**# 🗂️ Project Structure**

The project is organized into separate Django applications according to their

responsibilities.

\`\`\`text

library\_management\_system/

│

├── accounts/

│   ├── migrations/

│   ├── static/

│   │   └── library/

│   │       ├── audio/

│   │       ├── images/

│   │       ├── cover-images.js

│   │       ├── favicon.svg

│   │       ├── library.css

│   │       └── library.js

│   │

│   ├── templates/

│   │   └── accounts/

│   │       ├── partials/

│   │       ├── base.html

│   │       ├── home.html

│   │       ├── login.html

│   │       └── register.html

│   │

│   ├── forms.py

│   ├── views.py

│   └── ...

│

├── catalog/

│   ├── migrations/

│   ├── models.py

│   └── ...

│

├── loans/

│   ├── migrations/

│   ├── models.py

│   ├── views.py

│   └── ...

│

├── manage.py

├── requirements.txt

├── README.md

└── DESIGN-README.md



















🗄️ Database Models

The project uses Django's ORM to manage the application's database.

📖 Book

The Book model contains:

title

author

isbn

category

total\_copies

available\_copies

publication\_date

Each book has a unique ISBN.

📋 Loan

The Loan model connects a library member with a book.

It contains:

member

book

borrow\_date

return\_date

status

The loan status supports:

Borrowed

Returned

The relationship between User, Loan, and Book allows the system to track

which member currently has which book.

🔐 Authentication Architecture

The project uses Django's built-in authentication framework.

The system relies on Django's:

User

login()

logout()

AuthenticationForm

UserCreationForm

This provides a reliable server-side authentication mechanism without

reinventing Django's authentication system.

🧠 Business Logic

The borrowing workflow was implemented with transaction-safe database

operations.

When borrowing a book, the system:

Checks whether the member already has the book.

Checks whether an available copy exists.

Decreases the available copy count.

Creates the loan.

Shows the appropriate success/error message.

When returning a book, the system:

Verifies that the loan belongs to the logged-in member.

Confirms that the loan is currently active.

Changes the loan status to returned.

Records the return date.

Increases the available copy count.

Shows a success message.

🧪 Testing

The project was manually tested through the complete user workflow.

Authentication Testing

 Register a new account

 Validate required username

 Validate required email

 Validate email format

 Validate password

 Validate password confirmation

 Detect password mismatch

 Login

 Logout

Catalog Testing

 Browse books

 Search by title

 Search by author

 Search by ISBN

 Filter by category

 Filter available books

 Sort books

 View book details

Borrowing Testing

 Borrow an available book

 Decrease available copies

 Create a loan

 Display the loan in My Loans

 Prevent duplicate active borrowing

 Prevent borrowing when copies are unavailable

Returning Testing

 Return an active loan

 Update loan status

 Record return date

 Increase available copies

 Remove the book from active loans

 Borrow the book again after returning it

Interface Testing

 Navigation links

 Buttons

 Search controls

 Filters

 Grid/List view

 Book details dialog

 Audio player

 Browser console checked for JavaScript issues

📸 Project Showcase

A visual showcase of the main features and user experience of the project.

🏛️ Library Entrance

[ SCREENSHOT TO BE ADDED ]

🔐 Registration

[ SCREENSHOT TO BE ADDED ]

🔑 Login

[ SCREENSHOT TO BE ADDED ]

📚 Book Catalog

[ SCREENSHOT TO BE ADDED ]

🔎 Search & Filters

[ SCREENSHOT TO BE ADDED ]

📖 Book Details

[ SCREENSHOT TO BE ADDED ]

📋 My Loans

[ SCREENSHOT TO BE ADDED ]

🔄 Return Book

[ SCREENSHOT TO BE ADDED ]

🎵 Ambient Audio Player

[ SCREENSHOT TO BE ADDED ]

⚙️ Django Admin

[ SCREENSHOT TO BE ADDED ]

🔄 Main User Flow

The main user journey through the application is:

Library Entrance

       │

       ▼

Register / Login

       │

       ▼

Book Catalog

       │

       ├──── Search

       │

       ├──── Filter

       │

       ├──── Sort

       │

       └──── View Details

                    │

                    ▼

                 Borrow

                    │

                    ▼

                My Loans

                    │

                    ▼

                 Return

                    │

                    ▼

              Available Again

👨‍💻 Development Workflow

The project was developed using Git and GitHub for version control and team

collaboration.

The development process was organized into several stages:

Day 1 — Setup & Planning

Project setup

Git repository initialization

GitHub repository setup

Django project structure

Application planning

Day 2 — Core Models & Authentication

Book model

Loan model

Database migrations

User registration

Login/logout

Django authentication

Day 3 — Borrow & Return

Borrow functionality

Return functionality

Availability validation

Duplicate borrowing prevention

Loan management

Day 4 — Frontend

Library interface

Catalog page

My Loans page

Search

Filtering

Client-side validation

UI improvements

Day 5 — Integration

Integrated the main features

Fixed navigation

Tested the complete workflow

Added additional interface features

Day 6 — Testing & Polish

Authentication testing

Catalog testing

Borrow/return testing

JavaScript testing

Browser console testing

UI polishing

Day 7 — Documentation

README documentation

Project showcase preparation

Final testing

GitHub project organization

🌿 Git & GitHub

Git was used throughout the project to track changes and collaborate between

team members.

The project repository is hosted on GitHub.

Repository:

https\://github.com/AbdelazemAlaaEldin/library\_management\_system

⚙️ Installation

1\. Clone the Repository

git clone https\://github.com/AbdelazemAlaaEldin/library\_management\_system.git

2\. Enter the Project Directory

cd library\_management\_system

3\. Create a Virtual Environment

python -m venv .venv

4\. Activate the Virtual Environment

Windows

.venv\Scripts\activate

Git Bash

source .venv/Scripts/activate

5\. Install Dependencies

pip install -r requirements.txt

6\. Apply Database Migrations

python manage.py migrate

7\. Create a Superuser

python manage.py createsuperuser

Follow the prompts to create the administrator account.

8\. Run the Development Server

python manage.py runserver

Then open the local development server in your browser.

👨‍🏫 Django Admin

To access the Django administration panel:

/admin/

Use the superuser account created during installation.

From Django Admin, librarians can manage books and loans.

📋 Requirements

The project dependencies are listed in:

requirements.txt

The main framework used is:

Django

🔮 Future Improvements

The following features were considered as possible future improvements:

Overdue fine calculation

Due-date reminders

Book reservations

Custom librarian dashboard

More advanced reporting

Improved responsive layouts

Expanded book metadata

More advanced recommendation functionality

These features are outside the core requirements of the current project.

👥 Team Members

1\. Abdelazem Alaa Eldin

2\. Adel Alaa Ishak Tossa

3\. Ahmed Mohamed Rabie Ali

4\. Mohamed Mostafa Ali Mahmoud

5\. Youssef Ayman Mohamed Medhat

6\. Khaled Assem Abdelazim

📌 Project Status

Status: Completed

The core Library Management System workflow has been implemented and tested:

Authentication

      ✓

      │

      ▼

Book Catalog

      ✓

      │

      ▼

Search & Filtering

      ✓

      │

      ▼

Borrowing

      ✓

      │

      ▼

My Loans

      ✓

      │

      ▼

Returning

      ✓

      │

      ▼

Django Admin

      ✓

      │

      ▼

Testing & Documentation

      ✓

📚 The Reading Room

A whole world, one little card.

A library management system built with Django,

designed to make discovering, borrowing, and returning books

simple and enjoyable.