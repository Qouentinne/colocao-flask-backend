# How to start

## FIRST RUN

### Install PostgreSQL 
For MacOS:
    - Install [brew](https://brew.sh/)
    - Run ```brew install postgresql```

For Windows:
    - Install via the [official installer](https://www.postgresql.org/download/windows)

For Linux / WSL:
    - Create the file repository configuration:
    ```sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'```
    - Import the repository signing key
    ```wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -```
    - Update the package lists
    ```sudo apt-get update```
    - Install PostgreSQL
    ```sudo apt-get -y install postgresql```


### Create virual environment
```python -m venv venv```

### Activate virtual environment
For MacOs / Linux : ```source venv/bin/activate``` 
For Windows Powershell = ```venv\Scripts\Activate.ps1```

### Load required dependencies
```pip install -r requirements.txt```

### Setup env variables
Make a copy of .env-local and rename it .env. Then ask a founder for the SECRET_KEY and fill it in your brand new .env file.
**Do not edit the .env-local file**

## EVERYTIME

### Activate virtual environment (if not already runnning)
For MacOs / Linux : ```source venv/bin/activate``` 
For Windows Powershell = ```venv\Scripts\Activate.ps1```

### Start server runtime
```python flaskr/main.py```

## OPS

### Handle requirements

#### Update requirements.txt(local)
```pip freeze > requirements.txt```