from . import payment_blueprint
from flask import render_template, request, redirect, url_for, current_app
from ..tasks import send_celery_email
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *
from app import db, merchantAuth

@payment_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('payment/donate.html', title="Make a Donation", )
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
        if payment.messages.resultCode == "Ok":
            context = {
                'title': 'Thank you for your Donation',
                'htag': 'Thank you for donating!',
                'ptag': 'Thank you for supporting the Greenville United Football Club. We really appreciate your willingness and action to support our club.'
            }
            return render_template('thank-you.html', title=context['title'], htag=context['htag'], ptag=context['ptag'], donated=True)
        else:
            i = 0
            context = {
                'title': 'Internal Server Error (500)',
                'e_code': payment.messages.message[i].code,
                'e_body': payment.messages.message[i].text
            }
            return render_template('500.html', title=context['title'], e_code=context['e_code'], e_body=context['e_body'])

@payment_blueprint.route('/terms-and-conditions')
def show_donation_toc():
    return render_template('payment/terms.html', title='Donation Policy')

# @payment_blueprint.route('/payment_success/<string:email>')
# def donate(email):
#     message_data = {
#         'subject': 'Hello from flask app',
#         'body': 'Email test using Celery',
#         'recipients': email,
#     }
#     send_celery_email.apply_async(args=[message_data])
#     return render_template('thank-you.html', email=email)

### Helper Functions ###
def create_pay_transaction(amount, form_data):
    email = form_data.get(u'email')
    card_name = form_data.get(u'name')
    phone = form_data.get(u'phone')
    amount = form_data.get(u'donations')
    
    opaqueData = apicontractsv1.opaqueDataType()
    opaqueData.dataDescriptor = form_data['dataDescriptor']
    opaqueData.dataValue = form_data['dataValue']
    
    paymentOne = apicontractsv1.paymentType()
    paymentOne.opaqueData = opaqueData
    
    order = apicontractsv1.orderType()
    order.description = "GUFC Donation"
    
    customerData = apicontractsv1.customerDataType()
    customerData.type = "individual"
    # customerData.firstName = form_data['fName']
    # customerData.lastName = form_data['lName']
    # customerData.email = form_data['email']
    # customerData.phone = form_data['phone']
    
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)
    
    transactRequest = apicontractsv1.transactionRequestType()
    transactRequest.transactionType = "authCaptureTransaction"
    transactRequest.amount = amount
    transactRequest.order = order
    transactRequest.payment = paymentOne
    transactRequest.customer = customerData
    transactRequest.transactionSettings = settings
    
    createTransReq = apicontractsv1.createTransactionRequest()
    createTransReq.merchantAuthentication = merchantAuth
    createTransReq.transactionRequest = transactRequest
    
    createTransCont = createTransactionController(createTransReq)
    createTransCont.execute()
    
    response = createTransCont.getresponse()
    
    if response is not None:
        print(response)
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