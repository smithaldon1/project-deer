$(document).ready(function(){
    console.log("ready!");
});

$('#radio4').click(() => {
    $('#other-input').removeAttr('readonly').removeClass('form-control-plaintext');
});

$('.s-radio').click(() => {
    $('#other-input').attr('readonly', 'readonly').addClass('form-control-plaintext');
});

$('#c-btn').click(() => {
    var amount = $('input[name=donations]:checked').val();
    var other = $('#radio4').val()
    if ($('#radio4:checked').length === 1) {
        $('#p-btn').text("Pay $" + other);
    } else {
        $('#p-btn').text("Pay $" + amount);
    }
});

$('input[name=paymentRadio]').change(() => {
    if ($(this).text === "Paypal"){}
});

function sendPaymentDataToAnet() {
    var authData = {};
    authData.clientKey = '3k4tmASb94BA92R5ARN3HmELr4xCH4n9gkRrdzW9q6d4RWqvMJnvqaEFH2JK6G5S';
    authData.apiLoginId = '9CnR42ZrQtsQ';

    var cardData = {};
    cardData.cardNumber = $('#card').value;
    cardData.month = $('#expm').value;
    cardData.year = $('#expy').value;
    cardData.cardCode = $('#cvv').value;

    var secureData = {};
    secureData.authData = authData;
    secureData.cardData = cardData;

    Accept.dispatchData(secureData, (response) => {
        if (response.messages.resultCode === "Error") {
            var i = 0;
            while (i < response.messages.length) {
                console.log(
                    response.messages.message[i].code + ": " + response.messages.message[i].text
                );
                i = i + 1;
            }
        } else {
            paymentFormUpdate(response.opaqueData);
        }
    });
    console.log('AuthData: ' + authData, 'CardData: ' + cardData);
};

function paymentFormUpdate(opaqueData) {
    // Update hidden inputs with payment nonce information
    $('#dataDescriptor').value = opaqueData.dataDescriptor;
    $('#dataValue').value = opaqueData.dataValue;

    // Clear form values
    $('#fName').value = "";
    $('#lName').value = "";
    $('#email').value = "";
    $('#phone').value = "";
    $('#name').value = "";
    $('#card').value = "";
    $('#expm').value = "";
    $('#expy').value = "";
    $('#cvv').value = "";
    
    console.log($('#dataDescriptor').value)
    console.log($('#dataValue').value)

    // Submit Data Form
    $('#paymentForm').submit();
};
