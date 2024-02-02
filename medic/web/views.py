from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from pandas import read_csv
import requests
from pandas.io.html import read_html
from django.contrib.auth import authenticate
from django.contrib.auth import login as lg
from django.contrib.auth.decorators import login_required
from web.models import Official_Diagnosis
from django.contrib.auth.models import User
from django.core.mail import send_mail
# from django.contrib.staticfiles.storage import staticfiles_storage as storage
# Create your views here.


def symptoms(request):
    symptoms = read_csv("web/datafiles/symptoms.csv", header=None).values[:, 0]
    return render(request, 'web/symptoms.html', {'symptoms_list': symptoms})


def diagnosis(request, diagnosis):
    od_list = Official_Diagnosis.objects.filter(illness=diagnosis)

    # print(ob_list)

    def api_get(PRAMS):
        S = requests.Session()
        URL = "https://en.wikipedia.org/w/api.php"
        try:
            R = S.get(url=URL, params=PRAMS)
            print(R)
        except:
            print("#######----her")

            return None
        else:
            DATA = R.json()
            return DATA

    def get_title(diagnosis):
        # diagnosis = diagnosis
        PRAMS = {
            "action": "query",
            "format": "json",
            "list": "search",
            "redirects": 1,
            "srsearch": diagnosis,
            "srnamespace": "0",
            "srlimit": "1",
            "srprop": "snippet",
            "srsort": "relevance"
        }
        DATA = api_get(PRAMS)
        if DATA:
            out = DATA['query']['search']
            if out == [] and '(' in diagnosis:
                diagnosis = diagnosis.replace('(', '|')
                diagnosis = diagnosis.replace(')', '|')
                search_keys = diagnosis.split('|').reverse()
                for a in search_keys:
                    out = get_title(a)
                    if out:
                        break

            return out[0]

    def get_info(page):
        PRAMS = {
            "action": "query",
            "format": "json",
            "prop": "description|pageimages",
            "titles": page["title"].replace(' ', '_'),
            "piprop": "name|original"
        }
        pageid = str(page["pageid"])
        print(pageid)
        dis = api_get(PRAMS)

        if dis:
            discription = dis['query']['pages'][pageid]

            diagnosis = discription['title']
            page = 'https://en.wikipedia.org/wiki/'+diagnosis.replace(' ', '_')
            try:
                infobox = read_html(page, attrs={"class": "infobox"})[0].values
            except:
                return None
            else:

                infobox = dict((infobox[i][0], infobox[i][1])
                               for i in range(len(infobox)))
                try:
                    infobox['Diagnostic_method'] = infobox['Diagnostic method']
                    del infobox['Diagnostic method']
                except:
                    pass
                out = {"discription": discription, "infobox": infobox}
                return out
    try:
        title = get_title(diagnosis)
        info = get_info(title)
    except:
        return render(request, 'web/error.html', {'message': "no internet connection"})
    else:
        return render(request, 'web/diagnosis.html', {"title": title, "info": info, 'officials': od_list})


def processing(request):
    import tensorflow as tf
    import numpy as np
    model = tf.keras.models.load_model('web/datafiles/medical_prognosis.h5')
    input_field = np.zeros((1, 132))
    params = request.POST

    for a, b in params.items():
        try:
            a, b = int(a), int(b)

        except:
            pass
        else:
            input_field[0][a-1] = b

    pred = model.predict([input_field])
    result = np.argmax(pred, axis=1)
    # print("########--",input_field)

    prediction = read_csv("web/datafiles/diagnosis.csv",
                          header=None).values[:, 0][result][0]
    return HttpResponseRedirect(reverse('web:diagnosis', kwargs={'diagnosis': prediction}))


# -----------------auth----------
def login(request):
    return render(request, "web/login.html")


def login_auth(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        lg(request, user)

        return HttpResponseRedirect(reverse('web:officials'))
    else:
        return HttpResponseRedirect(reverse('web/login.html', kwargs={"error": "invalid login info"}))


@login_required(login_url="web/login")
def officials(request):
    illnesses = read_csv("web/datafiles/diagnosis.csv",
                         header=None).values[:, 0]
    message = ''
    usrname = request.user.username
    print(usrname)
    try:
        official = User.objects.get(username=usrname)
        diagnosis = request.POST['diagnosis']
        illness = request.POST['illness']
    except:
        check = False
    else:
        check = True
    if check:
        q = Official_Diagnosis(
            offical=official, diagnosis=diagnosis, illness=illness)
        q.save()
        message = "success"

    return render(request, 'web/officials.html', {'illnesses': illnesses, 'message': message})


def email(request):
    name = request.POST['firstname']+" "+request.POST['lastname']
    email_to = request.POST['email']
    subject = "MEDICAL DIAGNOSIS"
    email_from = "john@medic.com"
    message = "dear mr %s you most likely have ", name
    try:
        send_mail(
            subject,
            message,
            email_from,
            [email_to],

        )
    except:
        return render(request, "web/error.html")
    else:
        # return
        pass
