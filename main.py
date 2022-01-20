import json
from Crypto.Cipher import AES
from flask import Flask, render_template, redirect, make_response, request, session, g, flash
import datetime
from pdfkit import from_string, configuration
import requests
import pymongo
# PAYTM CHECKSUM CODE
import base64
import string
import random
import hashlib

MONGODB_URI = 'mongodb+srv://admin:admin@cluster0.pjg2t.mongodb.net/?retryWrites=true&w=majority'
MONGODB_URI = "mongodb+srv://admin:admin@cluster0.6a7fj.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = 'srisp'
client = pymongo.MongoClient(MONGODB_URI)
invoice = client[DATABASE_NAME]['Invoice']


# get last invoice id
def get_last_invoice_id():
    last_invoice_id = invoice.find().sort([("id", pymongo.DESCENDING)]).limit(1)
    for x in last_invoice_id:
        return x['id']





IV = "@@@@&&&&####$$$$"
BLOCK_SIZE = 16

path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = configuration(wkhtmltopdf=path_wkhtmltopdf)

billing_from = {
    "name": "rk mart",
    "address1": "186, Arvind Nagar",
                "address2": "CBI Colony, Jagatpura",
                "address3": "Jaipur Rajasthan",
                "contact": "9694603000",
                "email": "office.rkmart@gmail.com",
                "gst_no": "07BHNPS3038P1ZI"
}


def generate_checksum(param_dict, merchant_key, salt=None):
    params_string = __get_param_string__(param_dict)
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (params_string, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest()

    hash_string += salt

    return __encode__(hash_string, IV, merchant_key)


def generate_refund_checksum(param_dict, merchant_key, salt=None):
    for i in param_dict:
        if ("|" in param_dict[i]):
            param_dict = {}
            exit()
    params_string = __get_param_string__(param_dict)
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (params_string, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest()

    hash_string += salt

    return __encode__(hash_string, IV, merchant_key)


def generate_checksum_by_str(param_str, merchant_key, salt=None):
    params_string = param_str
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (params_string, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest()

    hash_string += salt

    return __encode__(hash_string, IV, merchant_key)


def verify_checksum(param_dict, merchant_key, checksum):
    # Remove checksum
    if 'CHECKSUMHASH' in param_dict:
        param_dict.pop('CHECKSUMHASH')

    # Get salt
    paytm_hash = __decode__(checksum, IV, merchant_key)
    salt = paytm_hash[-4:]
    calculated_checksum = generate_checksum(
        param_dict, merchant_key, salt=salt)
    return calculated_checksum == checksum


def verify_checksum_by_str(param_str, merchant_key, checksum):
    # Remove checksum
    # if 'CHECKSUMHASH' in param_dict:
    # param_dict.pop('CHECKSUMHASH')

    # Get salt
    paytm_hash = __decode__(checksum, IV, merchant_key)
    salt = paytm_hash[-4:]
    calculated_checksum = generate_checksum_by_str(
        param_str, merchant_key, salt=salt)
    return calculated_checksum == checksum


def __id_generator__(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


def __get_param_string__(params):
    params_string = []
    for key in sorted(params.keys()):
        if ("REFUND" in params[key] or "|" in params[key]):
            respons_dict = {}
            exit()
        value = params[key]
        params_string.append('' if value == 'null' else str(value))
    return '|'.join(params_string)


def __pad__(s): return s + (BLOCK_SIZE - len(s) %
                            BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)


def __unpad__(s): return s[0:-ord(s[-1])]


def __encode__(to_encode, iv, key):
    # Pad
    to_encode = __pad__(to_encode)
    # Encrypt
    c = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    to_encode = c.encrypt(to_encode.encode('utf-8'))

    # Encode
    to_encode = base64.b64encode(to_encode)
    return to_encode.decode("utf-8")


def __decode__(to_decode, iv, key):
    # Decode
    to_decode = base64.b64decode(to_decode)
    # Decrypt
    c = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    to_decode = c.decrypt(to_decode)
    if type(to_decode) == bytes:
        # convert bytes array to str.
        to_decode = to_decode.decode()
    # remove pad
    return __unpad__(to_decode)

# MAIN APP CODE


app = Flask(__name__)

# Staging configs:
# Keys from https://dashboard.paytm.com/next/apikeys

WEBSITE_NAME = "WEBSTAGING"
INDUSTRY_TYPE_ID = "Retail"
BASE_URL = "https://securegw-stage.paytm.in"
MERCHANT_ID = "eSNoWE46724710693818"
MERCHANT_KEY = "jHLlK_Mhjn!Y1k!F"


# Production configs:
# Keys from https://dashboard.paytm.com/next/apikeys
# MERCHANT_ID = "<MERCHANT_ID>"
# MERCHANT_KEY = "<MERCHANT_KEY>"
# WEBSITE_NAME = "<WEBSITE_NAME>"
# INDUSTRY_TYPE_ID = "<INDUSTRY_TYPE_ID>"
# BASE_URL = "https://securegw.paytm.in"


app.config['SECRET_KEY'] = "super_secret_key"

# api = 'http://103.146.110.30/topup/api/old/'
api = 'http://103.146.110.30/topup/api/'

userUrl = api + "ft_user.php"
users_data = requests.get(userUrl).json()


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main.html')


@app.route('/generate_invoice/<int:invoice_no>', methods=['GET', 'POST'])
def gen_inv(invoice_no):
    url = api + "ft_invoice_nw.php?u_id=" + session['user_data']['u_id']
    all_invoices = requests.get(url).json()
    invoice = [i for i in all_invoices if i['id'] == str(invoice_no)][0]
    inv_no = invoice.get('invoice_no')
    user_id = invoice.get('u_id')
    plan_id = invoice.get('s_id')
    userUrl = api + "ft_user.php"
    userResponse = requests.get(userUrl).json()

    planUrl = api + "ft_services.php"
    planResponse = requests.get(planUrl).json()

    user_details = [i for i in userResponse if i['u_id'] == user_id][0]
    plan_details = [i for i in planResponse if i['s_id'] == plan_id][0]
    gen_datetime = datetime.datetime.now().strftime('%d-$m-$Y')

    if user_details['u_taxno'] in ["", None]:
        gst = False
        gst_no = "N/A"
    else:
        gst = True
        gst_no = user_details['u_taxno']

    dt = str(invoice['invoice_date'])
    full_date, full_time = dt.split(' ')
    year, month, date = full_date.split('-')
    hours, minutes, seconds = full_time.split(':')

    dt = datetime.datetime(int(year), int(
        month), int(date), int(hours), int(minutes))
    year_str = str(dt.year)
    gen_datetime = {
        "date": dt.day,
        "month": dt.month,
        "year": year_str[-2] + year_str[-1],
        "hours": dt.hour,
        "minutes": dt.minute
    }

    params = {
        "gst": gst,
        "generated_datetime": gen_datetime,
        "billing_from": billing_from,
        "billing_to": {
            "name": user_details.get('u_fullname'),
            "address1": user_details.get('u_address'),
            "address2": user_details.get('u_city'),
            "address3": user_details.get('u_state') + ' ' + user_details.get('u_zip'),
            "contact": user_details.get('u_mobileno'),
            "email": user_details.get('u_email'),
            "gst_no": gst_no
        },
        "plan_details": {
            "name": plan_details.get('s_name'),
            "duration": "Unlimited",
            "data": "Unlimited",
            "onlineTime": plan_details.get('s_onlinelimit'),
            "expiry_date": invoice['expr_date'],
            "qty": 1,
            "rate": plan_details.get('s_price'),
            "amount": plan_details.get('s_pricewithtax')
        },
        "subtotal": plan_details.get('s_price'),
        "grand_total": plan_details.get('s_pricewithtax')
    }

    total = int(params['plan_details']['qty']) * \
        int(params['plan_details']['rate'])

    if params['gst'] == True:
        companyGstStateCode = str(
            params['billing_from']['gst_no'][0]) + str(params['billing_from']['gst_no'][1])
        customerGstStateCode = str(
            params['billing_to']['gst_no'][0]) + str(params['billing_to']['gst_no'][1])

        amt_with_tax = int(total) / 1.18
        tax_amt = int(total) - int(amt_with_tax)

        sgst_ = cgst_ = tax_amt/2
        igst_ = tax_amt

        rendered = render_template('invoice/gst_inv.html', params=params, url=request.url_root,
                                   gen_datetime=gen_datetime, billing_from=params['billing_from'],
                                   billing_to=params['billing_to'], plan=params['plan_details'],
                                   total=total, customerGstStateCode=customerGstStateCode,
                                   companyGstStateCode=companyGstStateCode, igst=igst_, cgst=cgst_,
                                   sgst=sgst_, grand_total=int(amt_with_tax), inv_no=inv_no)
    else:
        rendered = render_template(
            'invoice/nongst_inv.html',
            params=params, url=request.url_root, gen_datetime=gen_datetime,
            billing_from=params['billing_from'], billing_to=params['billing_to'],
            plan=params['plan_details'],
            total=total,
            inv_no=inv_no)

    pdf = from_string(rendered, False, configuration=config)
    # with open(f'./static/invoices/invoice-{dt}.pdf', 'wb') as f:
    #     f.write(pdf)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'

    return response


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    msg_send = request.form['msg_send']
    t_id = request.form['t_id']
    send_by = request.form['send_by']
    u_id = request.form['u_id']

    payload = {
        "ticket_id": str(t_id),
        "comment": str(msg_send),
        "attachment": "",
        "commenter_type": "",
        "m_id": str(u_id),
        "created_date": str(datetime.datetime.now()),
        "created_by": str(send_by)
    }

    HEADERS = {
        "content-type": "application/json"
    }

    r = requests.post(api+"ft_tickets_comment.php",
                      json=payload, headers=HEADERS)

    return


@app.route('/login', methods=['GET', 'POST'])
def login():

    if "is_remembered" in session:
        return redirect('/user')

    if request.method == 'POST':
        u_name = request.form.get('u_name')
        u_pass = request.form.get('u_pass')
        remember_me = request.form.get('remember')

        try:

            u_name_match = [d for d in users_data if d["u_name"] == u_name][0]
        except IndexError:
            u_name_match = []

        if u_name_match and u_name_match['u_password_pt'] == u_pass:
            session['user_id'] = u_name_match['u_id']
            user_data = [d for d in users_data if d["u_id"] == u_name_match['u_id']][0]
            session['user_data'] = user_data
            if remember_me == 'on':
                session['is_remembered'] = True
            return redirect('/user')
        return redirect('/login')

    return render_template('login_form/index.html')


@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    if 'is_remembered' in session:
        session.pop('is_remembered')
    return redirect('/')


@app.route('/user', methods=['GET', 'POST'])
def index():
    if not 'user_id' in session:
        return redirect('/login')

    dateLimit = session['user_data']['u_datelimit']

    today = str(datetime.date.today())
    today = today.split('-')

    dateLimit = dateLimit.strip(" 00:00:00")
    dateLimit = dateLimit.split('-')

    today = datetime.date(int(today[0]), int(today[1]), int(today[2]))

    try:
        dateLimit = datetime.date(int(dateLimit[0]), int(
            dateLimit[1]), int(dateLimit[2]))

        remain_days = today - dateLimit

        if remain_days.days >= 0:
            pass

        else:
            remain_days = "N/A"

    except ValueError:
        remain_days = "N/A"

    return render_template('user/index.html', remain_days=remain_days, user_data=session['user_data'])


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not 'user_id' in session:
        return redirect('/login')
    url = api + "ft_user.php?u_id="+str(session['user_data']['u_id'])
    profile_response = requests.get(url).json()[0]
    return render_template('user/profile.html', user=profile_response, user_data=session['user_data'])


@app.route('/payment_history', methods=['GET', 'POST'])
def payment_history():
    if not 'user_id' in session:
        return redirect('/login')

    url = api + "ft_userstatements.php?u_id=" + session['user_data']['u_id']
    res = requests.get(url).json()

    return render_template('user/payment_history.html', statements=res, user_data=session['user_data'])


@app.route('/service_history', methods=['GET', 'POST'])
def service_history():
    if not 'user_id' in session:
        return redirect('/login')

    url = api + "ft_srvhistory.php?u_id=" + session['user_data']['u_id']
    res = requests.get(url).json()

    return render_template('user/service_history.html', service_history=res, user_data=session['user_data'])


@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if not 'user_id' in session:
        return redirect('/login')

    url = api + "ft_transactions.php?u_id="+str(session['user_data']['u_id'])
    res = requests.get(url).json()

    return render_template('user/transactions.html', trans=res, user_data=session['user_data'])


@app.route('/list_invoice', methods=['GET', 'POST'])
def list_invoice():
    if not 'user_id' in session:
        return redirect('/login')

    url = api + "ft_invoice_nw.php?u_id=" + session['user_data']['u_id']
    res = requests.get(url).json()
    plan_url = api + "ft_services.php"
    plan_res = requests.get(plan_url).json()

    total = 0
    paid = 0

    for i in res:
        print(i, '**************')
        total += int(float(i['grand_total']))
        paid += int(float(i['paid_amount']))
        try:
            result = [d for d in plan_res if d['s_id'] == i['s_id']][0]
        except Exception as e:
            result = {'s_name': 'N/A', 's_price': '0'}

        i['plan'] = result['s_name']
        i['plan_price'] = result['s_price']
        i['tax_amt'] = 18/100 * int(result['s_price'])

        if str(str(i['invoice_no']).split('-')[0]).lower() == 'tx':
            i['tax_per'] = "18%"
        else:
            i['tax_per'] = "0%"

    unpaid = int(total) - int(paid)

    return render_template('user/list_invoice.html', user_data=session['user_data'], invoices=res, total=float(total), paid=float(paid), unpaid=float(unpaid))


@app.route('/ticket_list', methods=['GET', 'POST'])
def ticket_list():
    if not 'user_id' in session:
        return redirect('/login')

    r = requests.get(api+'ft_tickets.php')

    tickets = [i for i in r.json() if i['u_id'] ==
               session['user_data']['u_id']]
    return render_template('user/ticket_list.html', tickets=tickets, user_data=session['user_data'])


@app.route('/ticket_create', methods=['GET', 'POST'])
def ticket_create():
    if not 'user_id' in session:
        return redirect('/login')

    if request.method == 'POST':
        sub = request.form.get('group')
        data = {
            "subject": sub,
            "message": sub,
            "attachment": "",
            "priority": "",
            "group": "",
            "status": 0,  # 0 = Open, 1 = Resolved, 2 = Closed
            "tag": None,
            "close_otp_ver": "0",
            "close_otp": None,
            "person_called": None,
            "due_date": "",
            "u_name": session['user_data']['u_name'],
            "u_id": session['user_data']['u_id'],
            "instance_id": "",
            "op_id": "",
            "m_id": "",
            "resolved_date": "",
            "closed_date": "",
            "created_date": str(datetime.datetime.now()),
            "created_by": f"{session['user_data']['u_name']} (User Self)",
            "updated_date": "",
            "updated_by": ""
        }
        r = requests.post(api+"ft_tickets.php", json=data,
                          headers={"content-type": "application/json"})
        return redirect('/ticket_list')

    return render_template('user/ticket_create.html', user_data=session['user_data'])


@app.route('/resolve_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def res_ticket(ticket_id):
    return redirect('/ticket_list')


@app.route('/ticket_desc/<int:ticket_id>', methods=['GET', 'POST'])
def ticket_desc(ticket_id):
    if not 'user_id' in session:
        return redirect('/login')

    r = requests.get(api+'ft_tickets.php')
    r_comment = requests.get(api+'ft_tickets_comment.php')

    chats = [d for d in r_comment.json() if d['m_id'] == session['user_data']
             ['u_id'] and d['ticket_id'] == str(ticket_id)]
    ticket = [i for i in r.json() if i['u_id'] == session['user_data']
              ['u_id'] and i['id'] == str(ticket_id)][0]

    return render_template('user/ticket_desc.html', chats=chats, ticket_id=ticket_id, ticket=ticket, user_data=session['user_data'])


@app.route('/recharge_topup', methods=['GET', 'POST'])
def recharge_topup():
    global ft_services_res
    global all_plans
    global current_plan

    if not 'user_id' in session:
        return redirect('/login')

    url = api + f"ft_user.php?u_id="+str(session['user_data']['u_id'])
    response = requests.get(url).json()[0]
    m_id = response['m_id']
    s_id = response['s_id']
    s_groupname = response['s_groupname']

    ft_services = api + f"ft_services.php?m_id={m_id}"
    ft_services_res = requests.get(ft_services).json()

    all_plans = []
    publish_plan = [
        x for x in ft_services_res if x['s_groupname'] == s_groupname]

    for i in publish_plan:
        try:
            all_plans.append(i['s_name'])
        except NameError:
            pass

    current_plan_dict = [d for d in ft_services_res if d['s_id'] == s_id][0]

    return render_template('user/recharge_topup.html', plans=all_plans, current_plan=current_plan_dict, s_groupname=s_groupname, user_data=session['user_data'])


@app.route('/show_plan', methods=['POST'])
def show_plan():
    ft_services = api + f"ft_services.php"
    ft_services_res = requests.get(ft_services).json()
    selected_option = request.form['selected_option']
    plan_content = [d for d in ft_services_res if d['s_name']
                    == selected_option][0]
    return plan_content


@app.route('/rec_payment_summary', methods=['POST'])
def payment_summary():
    if not 'user_id' in session:
        return redirect('/login')

    if request.method == 'POST':
        try:
            a = eval(request.form['selected_option'])
            a = a['s_name']
        except SyntaxError as e:
            a = request.form['selected_option']
        final_plan = {
            "s_id": request.form['s_id'],
            "s_name": a,
            "s_rate": request.form['inp_rate'],
            "s_date_limit": request.form['inp_expiration_limit'],
            "s_price": request.form['inp_price']
        }

        floated_amt = "{:.2f}".format(int(request.form['inp_price']))
        transaction_data = {
            "MID": MERCHANT_ID,
            "WEBSITE": WEBSITE_NAME,
            "INDUSTRY_TYPE_ID": INDUSTRY_TYPE_ID,
            "ORDER_ID": str(datetime.datetime.now().timestamp()),
            "CUST_ID": session['user_data']['u_id'],
            "TXN_AMOUNT": floated_amt,
            "CHANNEL_ID": "WEB",
            "CALLBACK_URL": f"{request.url_root}after_payment/{session['user_data']['u_id']}/{request.form['s_id']}"
        }

        # Generate checksum hash
        transaction_data["CHECKSUMHASH"] = generate_checksum(
            transaction_data, MERCHANT_KEY)

        url = BASE_URL + '/theia/processTransaction'

        total = int(final_plan['s_price'])

        userUrl = api + "ft_user.php"
        userResponse = requests.get(userUrl).json()
        user_details = [i for i in userResponse if i['u_id']
                        == session['user_id']][0]

        if user_details['u_taxno'] in ["", None]:
            gst = False
            gst_no = "N/A"
        else:
            gst = True
            gst_no = user_details['u_taxno']

        companyGstStateCode = str(
            billing_from['gst_no'][0]) + str(billing_from['gst_no'][1])
        customerGstStateCode = str(gst_no[0]) + str(gst_no[1])

        if gst == True:
            subtotal = int(final_plan['s_price']) / 1.18
            amt_with_tax = int(total) / 1.18
            tax_amt = int(total) - int(amt_with_tax)

            sgst_ = cgst_ = tax_amt/2
            igst_ = tax_amt
        else:
            subtotal = int(final_plan['s_price'])
            sgst_ = cgst_ = igst_ = 0

        return render_template('user/payment_summary.html', plan=final_plan, url=url, data=transaction_data, user_data=session['user_data'],
                               companyGstStateCode=companyGstStateCode, customerGstStateCode=customerGstStateCode, sgst_=sgst_, cgst_=cgst_, igst_=igst_, gst=gst, subtotal=subtotal
                               )


@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    return render_template('admin/index.html', user_data=session['user_data'])


@app.route('/after_payment/<string:user_id>/<string:plan_id>', methods=['POST'])
def after_payment(user_id, plan_id):
    ft_services = api + f"ft_services.php"
    ft_services_res = requests.get(ft_services).json()
    user = [i for i in users_data if i['u_id'] == user_id][0]
    plan_details = [i for i in ft_services_res if i['s_id'] == plan_id][0]
    current_datetime = datetime.datetime.now()
    current_datetime.strftime("%Y-%m-%d %H:%M:%S")
     # log the callback response payload returned:
    callback_response = request.form.to_dict()
    # get current year
    current_year = current_datetime.year
    if user['u_taxno'] in ["", None]:
        taxType = 'WT'
    else:
        taxType = 'TX'


    payload = {
        "inv_type": "1",
        "invoice_no": f"{taxType}-{current_year}-{int(get_last_invoice_id())}",
        "credit_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "invoice_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "paid_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expr_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "2", # paid
        "s_name": plan_details['s_name'],
        "s_totallimitprint": "Unlimited",
        "s_onlinelimitprint": "Unlimited",
        "s_datelimitprint": "1 Month(s)",
        "s_uprate": plan_details['s_uprate'],
        "s_downrate": plan_details['s_downrate'],
        "s_id": plan_id,
        "u_name": user['u_name'],
        "buyer_name": user['u_fullname'],
        "buyer_address":"",
        "buyer_mobileno": "",
        "quantity": "1",
        "unit_price": str(plan_details['s_price']),
        "sub_total": str(plan_details['s_price']),
        "discount_enable": "0",
        "discount_per": "0",
        "discount_amount": "0.00",
        "tax1_enable": "0",
        "tax1_name": "",
        "tax1_per": "0",
        "tax1_amount": "0.00",
        "tax2_enable": "0",
        "tax2_name": "",
        "tax2_per": "0",
        "tax2_amount": "0.00",
        "othertax_enable": "0",
        "othertax_name": "OtherCharge",
        "othertax_per": "0",
        "othertax_amount": "0.00",
        "totaltax_per": "0",
        "totaltax_amount": "0.00",
        "grand_total": str(plan_details['s_price']),
        "paid_amount": str(plan_details['s_price']),
        "payment_mode": "Cash",
        "buyer_taxno": user['u_taxno'],
        "invoice_commit": "0",
        "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": "crisppl.srisp",
        "updated_by": "crisppl.srisp",
        "u_id": user['u_id'],
        "m_id": user['m_id'],
        "comment": "",
        "rollback_comment": "sending from application *****",
        "unique_id": "568268099600961d08491f8.59761503",
        "txn_id": user['u_taxno'],
    }


    invoice_url = api + "ft_invoice_nw.php?u_id=" + \
        user['u_id']
    if callback_response['STATUS'] == 'TXN_SUCCESS':
        print('adding to invoices!')
        invoice_res = requests.post(invoice_url, json=payload).json()
        print('invoice added, details = ', invoice_res)
        invoice.insert_one({"id": int(get_last_invoice_id()) + 1})


   
    # verify callback response checksum:
    checksum_verification_status = verify_checksum(callback_response, MERCHANT_KEY,callback_response.get("CHECKSUMHASH"))

    # verify transaction status:
    transaction_verify_payload = {
        "MID": callback_response.get("MID"),
        "ORDERID": callback_response.get("ORDERID"),
        "CHECKSUMHASH": callback_response.get("CHECKSUMHASH")
    }
    url = BASE_URL + '/order/status'
    verification_response = requests.post(
        url=url, json=transaction_verify_payload)

    if callback_response['STATUS'] == 'TXN_SUCCESS':
        status = 'success'
    else:
        status = 'fail'

    url = api + f"ft_userstatements.php?u_id={user_id}"
    res = requests.get(url).json()

    # return render_template('user/list_invoice.html', callback_response=callback_response,
    #                        checksum_verification_status=checksum_verification_status,
    #                        verification_response=verification_response.json(), statements=res,status=status, user_data=res)

    return redirect('/list_invoice')

@app.route('/admin_chat/<int:id>', methods=['GET', 'POST'])
def admin_chat(id):
    r = requests.get(api+'ft_tickets.php')
    tickets = [d for d in r.json() if d['id'] == str(id)][0]

    r_comment = requests.get(api+'ft_tickets_comment.php')
    chats = [d for d in r_comment.json() if d['ticket_id'] == str(id)]

    return render_template('admin/tickets.html', id=id, tickets=tickets, chats=chats, user_data=session['user_data'])


@app.route('/admin_tickets', methods=['GET', 'POST'])
def admin_tickets():
    tickets = (requests.get(api+'ft_tickets.php')).json()
    return render_template('admin/ticket_list.html', tickets=tickets, user_data=session['user_data'])


def plan(s_id):
    ft_services = api + f"ft_services.php"
    ft_services_res = requests.get(ft_services).json()
    plan = [x for x in ft_services_res if x['s_id'] == s_id][0]

    return plan
