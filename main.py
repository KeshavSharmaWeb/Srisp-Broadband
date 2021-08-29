from flask import Flask, render_template, redirect, make_response, request, session, g, flash
import datetime
from pdfkit import from_string, configuration
import requests
import json

# PAYTM CHECKSUM CODE
import base64
import string
import random
import hashlib

from Crypto.Cipher import AES

IV = "@@@@&&&&####$$$$"
BLOCK_SIZE = 16


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

MERCHANT_ID = "eSNoWE46724710693818"
MERCHANT_KEY = "jHLlK_Mhjn!Y1k!F"
WEBSITE_NAME = "WEBSTAGING"
INDUSTRY_TYPE_ID = "Retail"
BASE_URL = "https://securegw-stage.paytm.in"


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


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main.html')


@app.route('/generate_invoice', methods=['GET', 'POST'])
def gen_inv():
    params = request.get_json()
    dt = datetime.datetime.now()

    total = int(params['plan_details']['qty']) * \
        int(params['plan_details']['rate'])

    gen_datetime = {
        "date": dt.day,
        "month": str(dt.strftime("%B")).upper(),
        "year": dt.year,
        "hours": dt.hour,
        "minutes": dt.minute
    }

    if params['gst'] == True:
        """
        ############ GST BILL FORMAT ##########
        params = {
            "gst" : True | False,
            "generated_datetime" : "",
            "billing_from" : {
                "name" : "",
                "address1" : "",
                "address2" : "",
                "address3" : "",
                "contact": "",
                "email" : "",
                "gst_no" : "MANDATORY"
            }
            "billing_to" : {
                "name" : "",
                "address1" : "",
                "address2" : "",
                "address3" : "",
                "contact": "",
                "email" : "",
                "gst_no" : "MANDATORY"
            },
            "plan_details" : {
                "name" : "",
                "duration" : "",
                "data" : "",
                "onlineTime" : "",
                "expiry_date" : "",
                "qty" : "",
                "rate" : "",
                "amount": "",
            }
            "items" : [ IN THIS FORMAT  : -
                "name" : "",
                "qty" : "",
                "rate" : "",
                "amount": "", ]

            "subtotal": "",
            "cgst": "",
            "sgst": "",
            "grand_total": ""
        }

        """
        companyGstStateCode = str(
            params['billing_from']['gst_no'][0]) + str(params['billing_from']['gst_no'][1])
        customerGstStateCode = str(
            params['billing_to']['gst_no'][0]) + str(params['billing_to']['gst_no'][1])

        amt_with_tax = int(total) * 1.18
        tax_amt = int(amt_with_tax) - int(total)

        cgst_ = tax_amt/2
        sgst_ = cgst_
        igst_ = tax_amt

        rendered = render_template('invoice/gst_inv.html', params=params, url=request.url_root,
                                   gen_datetime=gen_datetime, billing_from=params['billing_from'],
                                   billing_to=params['billing_to'], plan=params['plan_details'],
                                   total=total, customerGstStateCode=customerGstStateCode,
                                   companyGstStateCode=companyGstStateCode,
                                   igst=igst_,
                                   cgst=cgst_,
                                   sgst=sgst_,
                                   grand_total=int(amt_with_tax)
                                   )
    else:
        """
    ############ NON GST BILL FORMAT ##########
    params = {
        "gst" : True | False,
        "generated_datetime" : "",
        "billing_from" : {
            "name" : "",
            "address1" : "",
            "address2" : "",
            "address3" : "",
            "contact": "",
            "email" : ""
        }
        "billing_to" : {
            "name" : "",
            "address1" : "",
            "address2" : "",
            "address3" : "",
            "contact": "",
            "email" : "",
            "gst_no" : "N/A"
        }
        "plan_details" : {
                "name" : "",
                "duration" : "",
                "data" : "",
                "onlineTime" : "",
                "expiry_date" : "",
                "qty" : "",
                "rate" : "",
                "amount": "",
            }
            "items" : [ IN THIS FORMAT  : -
                "name" : "",
                "qty" : "",
                "rate" : "",
                "amount": "", ]
        "subtotal": "",
        "grand_total": ""
    }

    """
        rendered = render_template(
            'invoice/nongst_inv.html',
            params=params, url=request.url_root, gen_datetime=gen_datetime,
            billing_from=params['billing_from'], billing_to=params['billing_to'],
            plan=params['plan_details'],
            total=total
        )

    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = from_string(rendered, False, configuration=config)

    dt = str(dt).replace(':', '')
    with open(f'./static/invoices/invoice-{dt}.pdf', 'wb') as f:
        f.write(pdf)
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

    return "True"


@app.route('/login', methods=['GET', 'POST'])
def login():

    if "is_remembered" in session:
        return redirect('/user')

    if request.method == 'POST':
        u_name = request.form.get('u_name')
        u_pass = request.form.get('u_pass')
        remember_me = request.form.get('remember')

        try:
            url = api + "ft_user.php"
            response = requests.get(url).json()
            u_name_match = [d for d in response if d["u_name"] == u_name][0]
        except IndexError:
            u_name_match = []

        if u_name_match and u_name_match['u_password_pt'] == u_pass:
            session['user_id'] = u_name_match['u_id']
            user_data = [d for d in response if d["u_id"]
                         == u_name_match['u_id']][0]
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
        total += int(float(i['grand_total']))
        paid += int(float(i['paid_amount']))

        result = [d for d in plan_res if d['s_id'] == i['s_id']][0]

        i['plan'] = result['s_name']

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
            # "CALLBACK_URL": f"{request.url_root}generate_invoice"
            "CALLBACK_URL": f"{request.url_root}after_payment/{session['user_data']['u_id']}/{request.form['s_id']}"
        }

        # Generate checksum hash
        transaction_data["CHECKSUMHASH"] = generate_checksum(
            transaction_data, MERCHANT_KEY)

        url = BASE_URL + '/theia/processTransaction'

        return render_template('user/payment_summary.html', plan=final_plan, url=url, data=transaction_data, user_data=session['user_data']
                               )

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    return render_template('admin/index.html', user_data=session['user_data'])


@app.route('/after_payment/<string:user_id>/<string:plan_id>', methods=['POST'])
def after_payment(user_id, plan_id):
    userUrl = api + "ft_user.php"
    userResponse = requests.get(userUrl).json()

    planUrl = api + "ft_services.php"
    planResponse = requests.get(planUrl).json()

    user_details = [i for i in userResponse if i['u_id'] == user_id][0]
    plan_details = [i for i in planResponse if i['s_id'] == plan_id][0]

    gen_datetime = datetime.datetime.now().strftime('%d-$m-$Y')

    if user_details.get('u_taxno') == "":
        gst = False
        gst_no = "N/A"
    else:
        gst = True
        gst_no = user_details.get('u_taxno')

    payload = {
        "gst": gst,
        "generated_datetime": gen_datetime,
        "billing_from": {
            "name": "rk mart",
            "address1": "186, Arvind Nagar",
            "address2": "CBI Colony, Jagatpura",
            "address3": "Jaipur Rajasthan",
            "contact": "9694603000",
            "email": "office.rkmart@gmail.com",
            "gst_no": "07BHNPS3038P1ZI"
        },
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
            "data": "3000",
            "onlineTime": plan_details.get('s_onlinelimit'),
            "expiry_date": "In 1 min",
            "qty": 1,
            "rate": plan_details.get('s_price'),
            "amount": plan_details.get('s_pricewithtax')
        },
        "subtotal": plan_details.get('s_price'),
        "grand_total": plan_details.get('s_pricewithtax')
    }

    # log the callback response payload returned:
    callback_response = request.form.to_dict()
    # verify callback response checksum:
    checksum_verification_status = verify_checksum(callback_response, MERCHANT_KEY,
                                                   callback_response.get("CHECKSUMHASH"))

    # verify transaction status:
    transaction_verify_payload = {
        "MID": callback_response.get("MID"),
        "ORDERID": callback_response.get("ORDERID"),
        "CHECKSUMHASH": callback_response.get("CHECKSUMHASH")
    }
    url = BASE_URL + '/order/status'
    verification_response = requests.post(
        url=url, json=transaction_verify_payload)

    post_json = {
        "id": "inv-gen_datetime",
        "inv_type": "1",
        "invoice_no": "WT-2020-0364",
        "credit_date": "2020-01-22 10:59:49",
        "invoice_date": "2020-02-01 15:22:38",
        "paid_date": "2021-01-21 16:22:05",
        "expr_date": "2020-02-21 00:00:00",
        "status": "1",
        "s_name": "8M-1Month",
        "s_totallimitprint": "Unlimited",
        "s_onlinelimitprint": "Unlimited",
        "s_datelimitprint": "1 Month(s)",
        "s_uprate": "8000 Kbps",
        "s_downrate": "8000 Kbps",
        "s_id": "7",
        "u_name": "sr_addy",
        "buyer_name": "Addy",
        "buyer_address": "near salu home,delhi-",
        "buyer_mobileno": "8800454595",
        "quantity": "1",
        "unit_price": "5000.00",
        "sub_total": "5000.00",
        "discount_enable": "0",
        "discount_per": "0",
        "discount_amount": "0.00",
        "tax1_enable": "0",
        "tax1_name": "CGST",
        "tax1_per": "0",
        "tax1_amount": "0.00",
        "tax2_enable": "0",
        "tax2_name": "GGST",
        "tax2_per": "0",
        "tax2_amount": "0.00",
        "othertax_enable": "0",
        "othertax_name": "OtherCharge",
        "othertax_per": "0",
        "othertax_amount": "0.00",
        "totaltax_per": "0",
        "totaltax_amount": "0.00",
        "grand_total": "5000.00",
        "paid_amount": "3300.00",
        "payment_mode": "Cash",
        "buyer_taxno": "",
        "invoice_commit": "0",
        "created_date": "2020-01-22 10:59:49",
        "updated_date": "2021-01-21 16:22:05",
        "created_by": "crisppl.srisp",
        "updated_by": "crisppl.srisp",
        "u_id": "2",
        "m_id": "1",
        "comment": "",
        "rollback_comment": None,
        "unique_id": "16833040005e27ddcd01db70.95271028",
        "txn_id": None
}

    if callback_response['STATUS'] == 'TXN_SUCCESS':
        status = 'success'
        requests.post(f"{request.url_root}generate_invoice", json=payload)
        post_url = api + "ft_invoice_nw.php?u_id=" + session['user_data']['u_id']
        res = requests.post(post_url, json=post_json)
    else:
        status = 'fail'

    url = api + f"ft_userstatements.php?u_id={user_id}"
    res = requests.get(url).json()

    return render_template('user/list_invoice.html', callback_response=callback_response,
                           checksum_verification_status=checksum_verification_status,
                           verification_response=verification_response.json(), statements=res, status=status, user_data=res)


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
