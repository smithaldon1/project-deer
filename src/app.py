from flask import Flask, render_template, request, session, make_response, jsonify, redirect
from flask_session import Session
import firebase_admin
from firebase_admin import credentials, firestore
from configparser import ConfigParser
import os
import time
from authorizenet import *
from authorizenet.apicontrollers import *
from decimal import *


# Initializations
# --------------------------------------------------------------
# Flask
app = Flask(__name__, static_url_path='', static_folder='static/', template_folder='templates/')

# Flask_sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ConfigParser
config = ConfigParser()
config.read('config.ini')

# Firebase
# --------------------------------------------------------------
cred = credentials.Certificate(config['firebase']['cred'])
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()


# Function Definitions
# --------------------------------------------------------------
def format_server_time():
    server_time = time.localtime()
    return time.strftime("%I:%M:%S %p", server_time)

def update_donation_db(f_data):
    update_time, data_ref = doc_ref.add(f_data)
    return print(f'Added document with id: {data_ref}')

def create_pay_transaction(amount, form_data):
    merchantAuth = authorizenet.apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = config['authnet']['apiLoginId']
    merchantAuth.transactionKey = config['authnet']['transactionKey']
    
    refId = "ref {}".format(format_server_time())
    
    opaqueData = authorizenet.apicontractsv1.opaqueDataType()
    opaqueData.dataDescriptor = form_data.dataDescriptor
    opaqueData.dataValue = form_data.dataValue
    
    paymentOne = authorizenet.apicontractsv1.paymentType()
    paymentOne.opaqueData = opaqueData
    
    order = authorizenet.apicontractsv1.orderType()
    order.description = "GUFC Donation"
    
    customerData = authorizenet.apicontractsv1.customerDataType()
    customerData.type = "individual"
    customerData.firstName = form_data.fName
    customerData.lastName = form_data.lName
    customerData.email = form_data.email
    customerData.phone = form_data.phone
    
    duplicateWindowSetting = authorizenet.apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)
    
    transactRequest = authorizenet.apicontractsv1.transactionRequestType()
    transactRequest.transactionType = "authCaptureTransaction"
    transactRequest.amount = amount
    transactRequest.order = order
    transactRequest.payment = paymentOne
    transactRequest.customer = customerData
    transactRequest.transactionSettings = settings
    
    createTransReq = authorizenet.apicontractsv1.createTransactionRequest()
    createTransReq.merchantAuthentication = merchantAuth
    createTransReq.refId = refId
    createTransReq.transactionRequest = transactRequest
    
    createTransCont = createTransactionController(createTransReq)
    createTransCont.execute()
    
    response = createTransCont.getresponse()
    
    if response is not None:
        if response.messages.resultCode == "Ok":
            if hasattr(response.transactionResponse, 'messages') == True:
                print ('Successfully created transaction with Transaction ID: %s' % response.transactionResponse.transId)
                print ('Transaction Response Code: %s' % response.transactionResponse.responseCode)
                print ('Message Code: %s' % response.transactionResponse.messages.message[0].code)
                print ('Auth Code: %s' % response.transactionResponse.authCode)
                print ('Description: %s' % response.transactionResponse.messages.message[0].description)
            else:
                print ('Failed Transaction.')
                if hasattr(response.transactionResponse, 'errors') == True:
                    print ('Error Code:  %s' % str(response.transactionResponse.errors.error[0].errorCode))
                    print ('Error Message: %s' % response.transactionResponse.errors.error[0].errorText)
        # Or, print errors if the API request wasn't successful
        else:
            print ('Failed Transaction.')
            if hasattr(response, 'transactionResponse') == True and hasattr(response.transactionResponse, 'errors') == True:
                print ('Error Code: %s' % str(response.transactionResponse.errors.error[0].errorCode))
                print ('Error Message: %s' % response.transactionResponse.errors.error[0].errorText)
            else:
                print ('Error Code: %s' % response.messages.message[0]['code'].text)
                print ('Error Message: %s' % response.messages.message[0]['text'].text)
    else:
        print ('Null Response.')

    return response
    

# Routes
# --------------------------------------------------------------

# Index 
@app.route("/", methods=['GET', 'POST'])
def index():
    context = { 
        'server_time': format_server_time(),
        'goal': '50,000.00',
        'amount': '1,000.00'
    }
    resp = make_response(render_template("index.html", server_time=context['server_time'], d_amount=context['amount'], goal=context['goal']))
    resp.set_cookie('amount', context['amount'])
    resp.set_cookie('goal', context['goal'])
    return resp

# Donation 
@app.route("/donate", methods=['GET', 'POST'])
def show_dp():
    if request.method == 'POST':
        # Get form values
        form_data = request.form
        email = form_data.get(u'email')
        card_name = form_data.get(u'name')
        phone = form_data.get(u'phone')
        amount = form_data.get(u'donations')
        # Create data structure to be sent to Firestore
        f_data = {u'email': email, u'name': card_name, u'phone': phone, u'amount': amount}
        doc_ref = db.collection(u'donations')
                  
        
        
        payment = create_pay_transaction(amount=amount, form_data=form_data)
        if payment.response.messages.resultCode == "Ok":
            context = {
                'title': 'Thank you for your Donation - Greenville United Football Club',
                'htag': 'Thank you for donating!',
                'ptag': 'Thank you for supporting the Greenville United Football Club. We really appreciate your willingness and action to support our club.'
            }
            return render_template('thank-you.html', title=context['title'], htag=context['htag'], ptag=context['ptag'])
        else:
            i = 0
            context = {
                'e_head': payment.response.messages.message[i].code,
                'e_body': payment.response.messages.message[i].text
            }
            len = length(payment.response.messages.message)
            return render_template('error.html', len=len, e_head=context['e_head'], e_body=context['e_body'])
    elif request.method == 'GET':
        return render_template('donate.html')

@app.route("/newsletter", methods=['POST'])
def add_email():
    if request.method == 'POST':
        email = request.form.get(u'email')
        f_data = { u'email': email, u'has_donated': u'false', u'is_subscribed': 'true'}
        doc_ref = db.collection(u'newsletter_dl').document(email)
        
        if doc_ref.get().exists:
            doc_ref.update(f_data)
            context = {}
            return render_template('thank-you.html', context=context)
        else:
            doc_ref.set(f_data)
            context = {
                'title': 'Newsletter - Greenville United Football Club',
                'htag': 'Thank you for subscribing!',
                'ptag': 'Thank you for subscribing to the Greenville United Football club newsletter. We hope you will consider donating to our organization to help better all of Eastern NC'
            }
            return render_template('thank-you.html', title=context['title'], htag=context['htag'], ptag=context['ptag'])
    else:
        redirect(404)
        
@app.route('/toc/donation')
def show_d_toc():
    context = {}
    return render_template('terms.html', context=context)

@app.route('/toc/website')
def show_w_toc():
    
    context = {
        'htag': 'Greenville United Football Club – Website Terms and Conditions',
        'ptag': 'The following documents represent Greenville United Football Club\'s Terms and Conditions as they apply to the business\'s website and donations.'
    }
    return render_template('terms.html', htag=context['htag'], ptag=context['ptag'])

@app.route('/privacy-policy')
def show_pp():
    return render_template('privacy-policy.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, ssl_context='adhoc')
    # ssl_context=('cert.pem', 'key.pem')