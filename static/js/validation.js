// Validate Ip Functiion

function ValidateIPaddress(inputtxt)
 {

     if(inputtxt == "")
     {
        return false;
     }
     var ipformat = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
     if(inputtxt.match(ipformat))
     {
     
        return true;
     }
     else
     {
        return false;
     }
 }


 // Validate Mobile No.

function ValidateMobileNo(inputtxt)
{
  var phoneno = /^\d{10}$/;
  if(inputtxt.match(phoneno))
    {
        return true;
    }
    else
    {
        
        return false;
    }
}

// Validate Mac address

function ValidateMacAddress(inputtxt)
{
  var regexp = /^(([A-Fa-f0-9]{2}[:]){5}[A-Fa-f0-9]{2}[,]?)+$/i;
  // var mac_address = $(this).val();
  if(regexp.test(inputtxt)) {
      return true;
  } else {
      return false;
  }
}

//Validate Email

function ValidateEmail(mail) 
{
  if(mail == "")
     {
        return true;
     }
 if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(mail))
  {
    return true;
  }
    // alert("You have entered an invalid email address!")
    return false;
}


//Checking white space in username

function hasWhiteSpace(s)
{


     // Check for white space
      if(s.match(/^.*[^\s{1,}]\s.*/))
      {
        return false;
      }
      return true;
}
function generateKey() {
  // Math.random should be unique because of its seeding algorithm.
  // Convert it to base 36 (numbers + letters), and grab the first 9 characters
  // after the decimal.
  var str = Math.random().toString(36).substr(2,11);
  return str.toUpperCase();

};


function generateRandomString(length=8,use_numbers=true,use_uppercase=true,use_lowercase=true,use_specialchars=false) {

   var result           = '';
   var numbers = '0123456789';
   var uppercase = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
   var lowercase = 'abcdefghjkmnpqrstuvwxyz';
   var specialchars = "~`!@#$%^&*()-_+=";
   var characters = '';

   if(use_numbers)
    characters += numbers;
   if(use_uppercase)
    characters += uppercase;
   if(use_lowercase)
    characters += lowercase;
   if(use_specialchars)
    characters += specialchars;

   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}