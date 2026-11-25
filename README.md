# Stitchbook

A menu-driven terminal app that helps tailors and clothing designers manage their business: customer orders, measurements, payments and delivery dates. Clients can check the status of their own orders.

**Built for Ubuntu / Linux, with notes for Windows at the bottom.** Needs Python 3.10+ and MySQL.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Choose your setup](#choose-your-setup)
- [Part A: Setup with Aiven (cloud database)](#part-a-setup-with-aiven-cloud-database)
  - [A1. Check what you have](#a1-check-what-you-have)
  - [A2. Get the project](#a2-get-the-project)
  - [A3. Install the project's required packages (inside the project only)](#a3-install-the-projects-required-packages-inside-the-project-only)
  - [A4. Get your Aiven details and certificate](#a4-get-your-aiven-details-and-certificate)
  - [A5. Create your settings file](#a5-create-your-settings-file)
  - [A6. Create the tables on Aiven](#a6-create-the-tables-on-aiven)
  - [A7. Check the connection](#a7-check-the-connection)
  - [A8. Set the tailor's details](#a8-set-the-tailors-details)
  - [A9. Run the app](#a9-run-the-app)
- [Part B: Setup with a local database (MySQL on your computer)](#part-b-setup-with-a-local-database-mysql-on-your-computer)
  - [B1. Check what you have](#b1-check-what-you-have)
  - [B2. Start MySQL](#b2-start-mysql)
  - [B3. Get the project](#b3-get-the-project)
  - [B4. Install the project's required packages (inside the project only)](#b4-install-the-projects-required-packages-inside-the-project-only)
  - [B5. Create your settings file](#b5-create-your-settings-file)
  - [B6. Create the database, user and tables](#b6-create-the-database-user-and-tables)
  - [B7. Check the connection](#b7-check-the-connection)
  - [B8. Set the tailor's details](#b8-set-the-tailors-details)
  - [B9. Run the app](#b9-run-the-app)
- [How it works](#how-it-works)
  - [Input rules](#input-rules)
  - [Database](#database)
  - [Error logging](#error-logging)
  - [Course concepts used](#course-concepts-used)
- [Quick test](#quick-test)
- [Problems?](#problems)
- [Windows users](#windows-users)

---

## Features

| Menu                        | What it does                                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 1. Add a new customer order | Registers a customer and saves their first order (clothing type, measurements, delivery date, price, deposit) |
| 2. View / update orders     | View all orders, search a customer, record a payment, change status, add another order, list unpaid orders    |
| 3. Incoming deadlines       | Shows orders not yet delivered, nearest delivery date first, overdue ones marked                              |
| 4. I am a client            | View-only: a client types their phone number and sees status, amount paid, remaining amount and delivery date |

## Tech stack

- Python 3.10+
- MySQL (via `mysql-connector-python`)
- `python-dotenv` for settings
- Runs on Aiven (cloud MySQL) or on a local MySQL, chosen with one setting (`APP_ENV`)

## Project structure

```
stitchbook/
├── main.py                  # starts the app
├── check_connection.py      # checks the database connection and tables
├── requirements.txt         # Python packages
├── .env.example             # settings template (copy to .env)
├── .env                     # your own settings (not committed)
├── .gitignore
├── README.md
│
├── certs/
│   └── ca.pem               # Aiven CA certificate (public, only used with Aiven)
│
├── database/
│   ├── __init__.py
│   ├── connection.py        # reads .env and opens the connection (Aiven or local)
│   └── schema.sql           # creates the customers and orders tables
│
├── models/
│   ├── __init__.py
│   ├── customer.py          # Customer class
│   └── order.py             # Order class (calculates the remaining amount)
│
└── menus/
    ├── __init__.py
    ├── main_menu.py                 # main menu loop (1, 2, 3, 4, 0)
    ├── option1_add_order.py         # option 1
    ├── option2_manage_orders.py     # option 2
    ├── option3_deadlines.py         # option 3
    └── option4_client_menu.py       # option 4 (tailor name and phone are set here)
```

---

## Choose your setup

The app can use one of two databases. Pick one and follow only that part from start to finish. Some steps are repeated in both parts on purpose.

|                                   | Part A: Aiven                                     | Part B: Local                                                        |
| --------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------- |
| Where is the database?            | In the cloud, shared by the team                  | MySQL on your own computer                                           |
| `APP_ENV` value                   | `deployed`                                        | `local`                                                              |
| Settings used in `.env`           | `AIVEN_*`                                         | `LOCAL_DB_*`                                                         |
| Needs the MySQL server installed? | No (only the MySQL client)                        | Yes                                                                  |
| Go to                             | [Part A](#part-a-setup-with-aiven-cloud-database) | [Part B](#part-b-setup-with-a-local-database-mysql-on-your-computer) |

---

## Part A: Setup with Aiven (cloud database)

Follow A1 to A9 in order. Ignore Part B.

### A1. Check what you have

```bash
python3 --version    # needs 3.10 or newer
mysql --version      # the MySQL client is enough, you do not need a MySQL server
git --version
```

If something is missing (Ubuntu / Debian):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip mysql-client git
```

### A2. Get the project

```bash
git clone https://github.com/bajengo-lab/Stitchbook_-Arts-Design-and-Culture-_PLP-2.git stitchbook
cd stitchbook
```

### A3. Install the project's required packages (inside the project only)

This creates a `venv` folder inside the project and installs the packages from `requirements.txt` into it. Nothing is installed on your system.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### A4. Get your Aiven details and certificate

1. Create a MySQL service on Aiven (or ask the person who did for the details).
2. On the service page, copy the **host**, **port**, **user** (usually `avnadmin`), **password** and **database name** (usually `defaultdb`).
3. On the same page, download the **CA certificate** and save it as `certs/ca.pem` in the project. It is a public certificate, so it is safe to commit.

### A5. Create your settings file

```bash
cp .env.example .env
```

Open `.env` and set the mode to `deployed`, then fill the Aiven lines:

```
APP_ENV=deployed

AIVEN_DB_HOST=<host from Aiven>
AIVEN_DB_PORT=<port from Aiven>
AIVEN_DB_USER=avnadmin
AIVEN_DB_PASSWORD=<password from Aiven>
AIVEN_DB_NAME=defaultdb
AIVEN_SSL_CA=certs/ca.pem
```

Leave the `LOCAL_DB_*` lines as they are. They are ignored in this mode.

**Never commit your real `.env`.** It holds the Aiven password. Only `.env.example` (with empty values) goes to GitHub.

### A6. Create the tables on Aiven

Only one person on the team needs to do this, once. The last word (`defaultdb`) is the database the tables go into. When it asks for a password, paste the Aiven password:

```bash
mysql -h <host> -P <port> -u avnadmin -p --ssl-ca=certs/ca.pem defaultdb < database/schema.sql
```

### A7. Check the connection

```bash
python check_connection.py
```

You should see:

```
Connection successful! Mode: deployed | Host: <your Aiven host>
Connected to database 'defaultdb' as 'avnadmin@...' and found both tables ('customers', 'orders').
```

### A8. Set the tailor's details

Open `menus/option4_client_menu.py` and change these two lines at the top. Clients see them on their order screen.

```python
TAILOR_NAME = "Your Name"
TAILOR_PHONE = "07XXXXXXXX"
```

### A9. Run the app

```bash
python main.py
```

Next time, you only need:

```bash
cd stitchbook
source venv/bin/activate
python main.py
```

Press `0` in the main menu to exit.

---

## Part B: Setup with a local database (MySQL on your computer)

Follow B1 to B9 in order. Ignore Part A.

### B1. Check what you have

```bash
python3 --version    # needs 3.10 or newer
mysql --version
git --version
```

If something is missing (Ubuntu / Debian):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip mysql-server git
```

### B2. Start MySQL

```bash
sudo systemctl start mysql
sudo systemctl status mysql    # should say "active (running)"
```

### B3. Get the project

```bash
git clone https://github.com/bajengo-lab/Stitchbook_-Arts-Design-and-Culture-_PLP-2.git stitchbook
cd stitchbook
```

### B4. Install the project's required packages (inside the project only)

This creates a `venv` folder inside the project and installs the packages from `requirements.txt` into it. Nothing is installed on your system.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### B5. Create your settings file

```bash
cp .env.example .env
```

For a local setup, leave the file as it is. `APP_ENV=local` is already set and the defaults match the database setup in B6. The `AIVEN_*` lines stay empty and are ignored.

| Setting             | Default                                 |
| ------------------- | --------------------------------------- |
| `APP_ENV`           | `local`                                 |
| `LOCAL_DB_HOST`     | `localhost`                             |
| `LOCAL_DB_PORT`     | `3306`                                  |
| `LOCAL_DB_USER`     | `stitchbook_user`                       |
| `LOCAL_DB_PASSWORD` | `stitchbook_pass` (local-only password) |
| `LOCAL_DB_NAME`     | `stitchbook`                            |

### B6. Create the database, user and tables

**a)** Create the database and the app user (run once, as the MySQL admin):

```bash
sudo mysql -e "CREATE DATABASE IF NOT EXISTS stitchbook; CREATE USER IF NOT EXISTS 'stitchbook_user'@'localhost' IDENTIFIED BY 'stitchbook_pass'; GRANT ALL PRIVILEGES ON stitchbook.* TO 'stitchbook_user'@'localhost'; FLUSH PRIVILEGES;"
```

(If `sudo mysql` is refused, run `mysql -u root -p -e "..."` with the same SQL inside the quotes.)

**b)** Create the tables. The last word (`stitchbook`) is the database the tables go into. When it asks for a password, type `stitchbook_pass`:

```bash
mysql -u stitchbook_user -p stitchbook < database/schema.sql
```

### B7. Check the connection

```bash
python check_connection.py
```

You should see:

```
Connection successful! Mode: local | Host: localhost
Connected to database 'stitchbook' as 'stitchbook_user@localhost' and found both tables ('customers', 'orders').
```

### B8. Set the tailor's details

Open `menus/option4_client_menu.py` and change these two lines at the top. Clients see them on their order screen.

```python
TAILOR_NAME = "Your Name"
TAILOR_PHONE = "07XXXXXXXX"
```

### B9. Run the app

```bash
python main.py
```

Next time, you only need:

```bash
cd stitchbook
source venv/bin/activate
python main.py
```

Press `0` in the main menu to exit.

---

## How it works

### Input rules

| Field         | Rule                                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Customer name | 3 to 12 letters or digits, no spaces, at least one letter. Must be unique (capital letters are ignored)                        |
| Phone number  | 10 digits starting with `07`. Must be unique. It is also the customer's **order number**                                       |
| Clothing type | `shirt`, `pant`, `suit`, `hat` or `shoes`                                                                                      |
| Measurements  | In cm, separated by commas. Shirt and suit: chest, waist, length. Pant: waist, hip, length. Hat: head size. Shoes: foot length |
| Delivery date | `yy/mm/dd` (example `27/12/25` is 25 December 2027). Dates in the past are rejected                                            |
| Money         | Whole numbers in RWF. Commas are allowed (`20,000`). The deposit cannot be more than the total price                           |
| Status        | `Pending`, `In progress`, `Ready` or `Delivered`                                                                               |

The **remaining amount** is never typed. It is always `total price - amount paid`.

A customer can have several orders. All of them use the same phone number. When a customer has more than one order, the tailor picks the order by its `Order #`.

### Database

| Table       | Columns                                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `customers` | `phone` (primary key), `name` (unique), `date_registered`                                                                                |
| `orders`    | `id`, `customer_phone` (links to `customers`), `clothing_type`, `measurements`, `delivery_date`, `total_price`, `deposit_paid`, `status` |

With a local database, the app runs as a limited MySQL user (`stitchbook_user`) that only has access to the `stitchbook` database, never as root.

### Error logging

Typing mistakes (wrong phone format, bad date, and so on) just show a short message and ask again. Real problems (database errors, bad settings, missing certificate) show a short message on screen and the full error is written to the terminal's error output (stderr). To keep a copy in a file:

```bash
python main.py 2> errors.log
```

### Course concepts used

- Loops and if/else: the menus and input checks
- Dictionaries: `MEASUREMENT_PROMPTS` maps each clothing type to its measurements
- Exceptions: bad input never crashes the app, and database errors are logged to the terminal
- Classes and objects: `Customer` and `Order`
- SQL database: MySQL with parameterized queries

---

## Quick test

Works the same in Part A and Part B.

| Step             | Type                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------- |
| Add an order     | `1`, then `jean`, `0788123456`, `shirt`, `96, 82, 70`, `27/12/25`, `20,000`, `15,000` |
| Record a payment | `2`, `2`, `jean`, `a`, `5,000`                                                        |
| Check deadlines  | `3`                                                                                   |
| Client view      | `4`, `1`, `0788123456`                                                                |
| Exit             | `0`                                                                                   |

## Problems?

**Both parts**

| Error                                                     | Fix                                                                                      |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `ModuleNotFoundError`                                     | `source venv/bin/activate` then `pip install -r requirements.txt`                        |
| `python: command not found`                               | Activate the virtual environment first (`source venv/bin/activate`), or use `python3`    |
| `APP_ENV in your .env file must be "local" or "deployed"` | Fix the `APP_ENV` line in `.env`                                                         |
| Old `DB_HOST` / `DB_USER` names in `.env`                 | Rename them to `LOCAL_DB_HOST`, `LOCAL_DB_USER`, and so on, or copy `.env.example` again |

**Part A (Aiven)**

| Error                                               | Fix                                                                              |
| --------------------------------------------------- | -------------------------------------------------------------------------------- |
| `Aiven settings are missing in your .env file`      | Fill every `AIVEN_*` line (the message lists which ones are empty)               |
| `The Aiven SSL certificate file was not found`      | Save the Aiven CA certificate as `certs/ca.pem`, or fix `AIVEN_SSL_CA`           |
| `Unknown MySQL server host` or connection timed out | Check `AIVEN_DB_HOST` and `AIVEN_DB_PORT`, and that the Aiven service is running |
| `Access denied for user`                            | Check `AIVEN_DB_USER` and `AIVEN_DB_PASSWORD`                                    |
| `Table '...orders' doesn't exist`                   | Re-run step A6                                                                   |

**Part B (local)**

| Error                                      | Fix                                                               |
| ------------------------------------------ | ----------------------------------------------------------------- |
| `Access denied for user 'stitchbook_user'` | Re-run step B6a and check that your `.env` matches `.env.example` |
| `Can't connect to MySQL server`            | `sudo systemctl start mysql`                                      |
| `Unknown database 'stitchbook'`            | Re-run step B6a                                                   |
| `Table 'stitchbook.orders' doesn't exist`  | Re-run step B6b                                                   |

---

## Windows users

The app runs on Windows too. Follow Part A or Part B as written, but use these commands instead:

| Step                        | Ubuntu / Linux                    | Windows                                                                                                                                                                                                                                                                                          |
| --------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Install tools               | `sudo apt install ...`            | Install Python from python.org (tick "Add Python to PATH"), Git from git-scm.com, and MySQL from dev.mysql.com/downloads/installer. Part A (Aiven) only needs the client: choose "Client only" in the installer, or Custom and select only the client programs. Part B (local) needs the server. |
| Create the venv             | `python3 -m venv venv`            | `python -m venv venv`                                                                                                                                                                                                                                                                            |
| Activate the venv           | `source venv/bin/activate`        | `venv\Scripts\activate`                                                                                                                                                                                                                                                                          |
| Copy the settings file      | `cp .env.example .env`            | `copy .env.example .env`                                                                                                                                                                                                                                                                         |
| Start MySQL (Part B)        | `sudo systemctl start mysql`      | MySQL runs as a Windows service after install. Start it from the Services app if needed.                                                                                                                                                                                                         |
| Create DB and user (Part B) | `sudo mysql -e "..."`             | `mysql -u root -p -e "..."` with the same SQL inside the quotes                                                                                                                                                                                                                                  |
| Load the tables             | `mysql ... < database/schema.sql` | Use Command Prompt (`cmd`) with the same command. In PowerShell use `Get-Content database\schema.sql \| mysql ...` with the same options                                                                                                                                                         |

## Windows users

Follow Part A or Part B as written. When you reach one of these steps, use the Windows version instead. Everything else stays the same.

**Install the tools** (instead of `sudo apt install ...`)

- Python: [python.org](https://www.python.org/downloads/) (tick "Add Python to PATH")
- Git: [git-scm.com](https://git-scm.com/downloads)
- MySQL: [MySQL Installer](https://dev.mysql.com/downloads/installer/). For Part A, install only the client ("Client only", or select the client programs under "Custom"). For Part B, install the server too.

**Check Python** (instead of `python3 --version`)

```bat
python --version
```

**Create the virtual environment** (instead of `python3 -m venv venv`)

```bat
python -m venv venv
```

**Activate it** (instead of `source venv/bin/activate`)

```bat
venv\Scripts\activate
```

**Copy the settings file** (instead of `cp .env.example .env`)

```bat
copy .env.example .env
```

**Start MySQL, Part B only** (instead of `sudo systemctl start mysql`)

MySQL usually runs as a Windows service after install. If it is not running, start it from the **Services** app.

**Create the database and user, Part B only** (instead of `sudo mysql -e "..."`)

```bat
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS stitchbook; CREATE USER IF NOT EXISTS 'stitchbook_user'@'localhost' IDENTIFIED BY 'stitchbook_pass'; GRANT ALL PRIVILEGES ON stitchbook.* TO 'stitchbook_user'@'localhost'; FLUSH PRIVILEGES;"
```

**Create the tables** (steps A6 and B6b)

In Command Prompt, use the same command as in the step. PowerShell does not support `<`, so use one of these there:

```powershell
# Part A (Aiven)
Get-Content database\schema.sql | mysql -h <host> -P <port> -u avnadmin -p --ssl-ca=certs/ca.pem defaultdb

# Part B (local)
Get-Content database\schema.sql | mysql -u stitchbook_user -p stitchbook
```

Two Windows tips:

- If `mysql` is not recognized, add `C:\Program Files\MySQL\MySQL Server 8.0\bin` to your `Path` (the folder name may differ with the version) and open a new terminal.
- If PowerShell says running scripts is disabled when you activate the venv, run this once and try again: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
