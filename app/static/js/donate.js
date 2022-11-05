$(document).ready(function(){
    console.log("ready!");
});

$('#radio4').click(() => {
    $('#other-input').removeAttr('readonly').removeClass('form-control-plaintext');
});

$('.s-radio').click(() => {
    $('#other-input').attr('readonly', 'readonly').addClass('form-control-plaintext');
});

// Add checkout amount to pay button
$('#c-btn').click(() => {
    var amount = $('input[name=donations]:checked').val();
    var other = $('#other-input').val();
    if ($('#radio4:checked').length === 1) {
        $('#p-btn').text("Pay $" + other);
    } else {
        $('#p-btn').text("Pay $" + amount);
    }
});


function sendPaymentDataToAnet() {
    var authData = {};
    authData.clientKey = '3k4tmASb94BA92R5ARN3HmELr4xCH4n9gkRrdzW9q6d4RWqvMJnvqaEFH2JK6G5S';
    authData.apiLoginId = '9CnR42ZrQtsQ';

    var cardData = {};
    cardData.fullName = $('#name').val();
    cardData.cardNumber = $('#card').val();
    cardData.month = $('#expm').val();
    cardData.year = $('#expy').val();
    cardData.cardCode = $('#cvv').val();

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
    $('#dataDescriptor').val(opaqueData.dataDescriptor);
    $('#dataValue').val(opaqueData.dataValue);

    // Clear form values
    $('#fName').val("");
    $('#lName').val("");
    $('#email').val("");
    $('#phone').val("");
    $('#name').val("");
    $('#card').val("");
    $('#expm').val("");
    $('#expy').val("");
    $('#cvv').val("");
    
    console.log($('#dataDescriptor').val())
    console.log($('#dataValue').val())

    // Submit Data Form
    $('#paymentForm').submit();
};
