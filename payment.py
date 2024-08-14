import uuid
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime
import base64
import requests
from models import db, Payment, Transaction, Student, User

# Create Blueprint and API
payment_bp = Blueprint('payment_bp', __name__, url_prefix='/api/payments')
payment_api = Api(payment_bp)

# M-Pesa Sandbox Credentials
CONSUMER_KEY = "l7ks2cN7DeyUOvLWx31tqxYg6geRY6tZJcjumTi8LrEZJCTG"
CONSUMER_SECRET = "YbjWV3iLFUo5nRsPTc91oBtDvTDkcvyY5EHuKjvfgTssCpMG2Ezz0PiAuA4h39oG"
SHORTCODE = "174379"
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
TILL = "174379"
CALLBACK_URL = "https://unduly-pleasant-chamois.ngrok-free.app/api/payments/callback"  # Update with your actual URL

class NewMpesa(Resource):
    def post(self):
        try:
            data = request.json
            print("Received data:", data)

            mpesa_no = data.get('phoneNumber')
            if mpesa_no:
                mpesa_no = mpesa_no[1:]  # Stripping the first character
            else:
                return {"success": False, "message": "phoneNumber is missing."}, 400

            amount = data.get('amount')
            if not amount:
                return {"success": False, "message": "amount is missing."}, 400

            student_id = data.get('student')
            description = data.get('description')
            user_id = data.get('user_id')  # Retrieve the user_id from the request data

            if not user_id:
                return {"success": False, "message": "user_id is missing."}, 400

            created_at = datetime.now()

            # Generate a unique identifier using user_id, phone number, and UUID
            unique_identifier = f"{user_id}_{mpesa_no}_{uuid.uuid4().hex}"

            # Create a new transaction
            transaction = Transaction(
                status="pending",
                phone=mpesa_no,
                trans_for=student_id,
                amount=amount,
                trans_date=created_at,
                mpesa_receipt_number=None,
                payer_names="",
                user_description=description,
                user_id=user_id,  # Ensure user_id is passed here
                unique_identifier=None  # Save unique identifier here
            )
            
            db.session.add(transaction)
            db.session.commit()
            transaction_id = transaction.id
            # print("Transaction created with ID:", transaction_id)

            timestamp = created_at.strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode('utf-8')).decode('utf-8')

            token = self.mpesa_authentication()  # Auth token
            if not token:
                return {"success": False, "message": "Failed to get M-Pesa auth token."}, 500

            # M-Pesa API request
            mpesa_response = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                json={
                    "BusinessShortCode": SHORTCODE,
                    "Password": password,
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": amount,
                    "PartyA": f"254{mpesa_no}",
                    "PartyB": TILL,
                    "PhoneNumber": f"254{mpesa_no}",
                    "CallBackURL": CALLBACK_URL,
                    "AccountReference": f"254{mpesa_no}",
                    "TransactionDesc": "Payment of fees",
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )

            if mpesa_response.status_code == 200:
                mpesa_response_json = mpesa_response.json()
                
               # Extract the MerchantRequestID from the response
                merchant_request_id = mpesa_response_json.get("MerchantRequestID")
                # if merchant_request_id:
                print("MerchantRequestID:", merchant_request_id)
                    # Update the transaction with the MerchantRequestID
                try:
                    transaction = Transaction.query.get(transaction_id)
                    if transaction:
                        transaction.unique_identifier = mpesa_response_json.get("MerchantRequestID")
                        db.session.commit()
                        print("MPESA Merchant ID number updated:", transaction.unique_identifier)
                except Exception as e:
                    print("Error updating transaction:", e)
                    
                # transaction.unique_identifier = merchant_request_id
                # db.session.commit()
                print("M-Pesa API response:", mpesa_response_json)

                return {
                    "success": True,
                    "message": "Payment request in progress",
                    "transactionId": transaction_id,
                }, 200
            else:
                return {"success": False, "message": "M-Pesa request failed."}, mpesa_response.status_code

        except Exception as e:
            print("Error while making M-Pesa request:", e)
            return {"success": False, "message": "Payment request failed. Please try again."}, 500

    def mpesa_authentication(self):
        try:
            auth = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode('utf-8')).decode('utf-8')
            response = requests.get(
                "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
                headers={"Authorization": f"Basic {auth}"},
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                raise Exception("Failed to authenticate with M-Pesa API")
        except Exception as e:
            print(f"Error generating token: {e}")
            return None


class ConfirmPayment(Resource):
    def get(self, transid):
        try:
            transaction = Transaction.query.get(transid)
            if transaction:
                return jsonify(transaction.to_dict()), 200
            else:
                return {"success": False, "message": "Transaction not found"}, 404
        except Exception as e:
            print(e)
            return {"success": False, "message": "Server error"}, 500

class MpesaCallback(Resource):
    def post(self):
        try:
            callback_data = request.get_json()
            print("Received M-Pesa callback:", callback_data)

            body = callback_data.get('Body', {}).get('stkCallback', {})
            
            if 'CallbackMetadata' not in body:
                message = body.get('ResultDesc', 'Missing CallbackMetadata')
                return {"error": message, "success": False, "message": message}, 201

            metadata = body.get('CallbackMetadata', {}).get('Item', [])
            
            amount = None
            mpesa_receipt_number = None
            phone_number = None
            transaction_date = None
            payer_names = None

            for item in metadata:
                if item.get('Name') == 'Amount':
                    amount = item.get('Value')
                elif item.get('Name') == 'MpesaReceiptNumber':
                    mpesa_receipt_number = item.get('Value')
                elif item.get('Name') == 'PhoneNumber':
                    phone_number = item.get('Value')
                elif item.get('Name') == 'TransactionDate':
                    try:
                        transaction_date = datetime.strptime(str(item.get('Value')), '%Y%m%d%H%M%S')
                    except ValueError:
                        return {"error": "Invalid transaction date format", "success": False}, 400
                elif item.get('Name') == 'PayerName':
                    payer_names = item.get('Value')

            if not phone_number or amount is None:
                return {"error": "Missing required fields in callback data", "success": False, "message": "Callback processed"}, 400

            unique_identifier = body.get('MerchantRequestID')
            print('Merchant Request ID:', unique_identifier)
            transaction = Transaction.query.filter_by(unique_identifier=unique_identifier).first()

            if not transaction:
                return {"ResultCode": 1, "ResultDesc": "Transaction not found"}, 400

            transaction.status = body['ResultDesc']
            transaction.mpesa_receipt_number = mpesa_receipt_number
            transaction.payer_names = payer_names
            transaction.amount = amount
            transaction.trans_date = transaction_date
            transaction.phone = phone_number
            db.session.commit()

            new_payment = Payment(
                student_id=transaction.trans_for,
                amount=amount,
                payment_date=transaction_date,
                description="M-Pesa payment received"
            )
            db.session.add(new_payment)
            db.session.commit()

            transaction.payment_id = new_payment.id
            db.session.commit()

            return {"ResultCode": 0, "ResultDesc": "Success"}, 200

        except Exception as e:
            print("Error processing callback:", e)
            return jsonify({"error": "Callback processing failed"}), 500
# Add Resources to API
payment_api.add_resource(NewMpesa, '/new')
payment_api.add_resource(ConfirmPayment, '/confirm/<int:transid>')
payment_api.add_resource(MpesaCallback, '/callback')