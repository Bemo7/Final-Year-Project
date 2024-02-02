# requirments:
you'd require the to install the following 

- **python** 

    you can get it at [python official site](https://www.python.org/downloads/)

- **✨django✨** 

    run this on your terminal to install

    `python -m pip install Django`


    or  visit the [official site](https://docs.djangoproject.com/en/4.0/topics/install/)



- **tensorflow** 

    run this on your terminal to install

    `python3 -m pip install tensorflow`


    or  visit the [official site](https://www.tensorflow.org/install/pip#windows)

    ### Verify install:
        python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

- **pandas** 

    visit the [official docs](https://pandas.pydata.org/docs/getting_started/install.html) or use

    `pip install pandas`

    ### Verify install:
        python3 -c "import pandas as pd; print(pd.test())"

- **other**

    its best to install all to avoid any suprises

    - `pip install html5lib`
    - `python -m pip install -U matplotlib`
    - `pip install numpy`
    - `pip install lxml`


# usage
## running the app

to run the server

1. make sure you're in the ./MEDIC directory

2. write in your terminal

    `python manage.py runserver`

    output

        You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.

        Run 'python manage.py migrate' to apply them.
        July 14, 2022 - 23:40:04
        Django version 4.0.5, using settings 'medic.settings'

        Starting development server at http://127.0.0.1:8000/web
        Quit the server with CTRL-BREAK.
    visit http://127.0.0.1:8000/symptoms/web

## sitemap
- symptoms - http://127.0.0.1:8000/web/symptoms
- diagnosis - http://127.0.0.1:8000/web/diagnosis
- login(officials) - http://127.0.0.1:8000/web/login
- officals - http://127.0.0.1:8000/web/officials

