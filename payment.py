    from flask import Blueprint, request, jsonify
    from flask_restful import Api, Resource
    from datetime import datetime
    import base64
    import requests
    from models import db, Payment, Transaction
    import os

    payment_bp = Blueprint('payment_bp', __name__, url_prefix='/api/payments')
    payment_api = Api(payment_bp)

    class NewMpesa(Resource):
        def post(self):
            try:
                data = request.json
                print("Received M-Pesa payment request:", data)
                
                mpesa_no = data.get('mpesaNumber')[1:]
                amount = data.get('amount')
                student_id = data.get('student')
                description = data.get('description')

                # Create a new transaction
                transaction = Transaction(
                    status="pending",
                    phone=mpesa_no,
                    amount=amount,
                    trans_id="",
                    desc='',
                    user_description=description,
                    trans_for=student_id,
                    trans_date=datetime.now()
                )
                db.session.add(transaction)
                db.session.commit()
                transaction_id = transaction.id
                print("Transaction created with ID:", transaction_id)

                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                shortcode = "174379"
                passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
                till = "174379"

                password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode('utf-8')).decode('utf-8')

                # M-Pesa API request
                mpesa_response = requests.post(
                    "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                    json={
                        "BusinessShortCode": shortcode,
                        "Password": password,
                        "Timestamp": timestamp,
                        "TransactionType": "CustomerPayBillOnline",
                        "Amount": amount,
                        "PartyA": f"254{mpesa_no}",
                        "PartyB": till,
                        "PhoneNumber": f"254{mpesa_no}",
                        "CallBackURL": "https://e59d-2c0f-fe38-218a-3a6d-6977-ae2a-6c04-a2d4.ngrok-free.app/api/payments/callback",
                        "AccountReference": f"254{mpesa_no}",
                        "TransactionDesc": "Payment of fees",
                    },
                    headers={
                        "Authorization": f"Bearer {os.getenv('MPESA_ACCESS_TOKEN')}"
                    }
                )
                # Print and return M-Pesa response
                print("M-Pesa API response:", mpesa_response.json())
                return jsonify({
                    "success": True,
                    "message": "Payment request in progress",
                    "transactionId": transaction_id,
                }), 200

            except Exception as e:
                print("Error while making M-Pesa request:", e)
                return jsonify({
                    "success": False,
                    "message": "Payment request failed. Please try again.",
                }), 500
    def mpesa_authentication(self, request):
        try:
            consumer_key = "l7ks2cN7DeyUOvLWx31tqxYg6geRY6tZJcjumTi8LrEZJCTG"
            consumer_secret = "YbjWV3iLFUo5nRsPTc91oBtDvTDkcvyY5EHuKjvfgTssCpMG2Ezz0PiAuA4h39oG"
            auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode('utf-8')).decode('utf-8')
            response = requests.get(url,
                                     headers={
                                         "Authorization": f"Basic {auth}"
                                     }
                                       
                                     )
                                     
        
    class ConfirmPayment(Resource):
        def get(self, transid):
            try:
                transaction = Transaction.query.get(transid)
                if transaction:
                    return jsonify({
                        "success": True,
                        "transactionId": transid,
                        "status": transaction.status,
                        "reference": transaction.trans_id,
                    }), 200
                else:
                    return jsonify({
                        "success": False,
                        "message": "Transaction not found",
                    }), 404
            except Exception as e:
                print(e)
                return jsonify({
                    "success": False,
                    "message": "Server error",
                }), 500

    class MpesaCallback(Resource):
        def post(self):
            try:
                callback_data = request.json
                body = callback_data['Body']['stkCallback']

                if 'CallbackMetadata' not in body:
                    return jsonify({"error": "Invalid callback data"}), 400

                metadata = body['CallbackMetadata']
                amount = metadata['Item'][0]['Value']
                trans_id = metadata['Item'][1]['Value']
                trans_date = metadata['Item'][2]['Value']
                phone = metadata['Item'][3]['Value']
                desc = metadata['Item'][4]['Value']

                status = "Success" if body.get('ResultCode') == 0 else "Error"
                update_transaction(status, trans_id, desc)
                return jsonify({"success": True, "message": "Callback processed"}), 200

            except Exception as e:
                print("Error processing callback:", e)
                return jsonify({"error": "Callback processing failed"}), 500

    def update_transaction(status, trans_id, desc):
        try:
            transaction = Transaction.query.filter_by(trans_id=trans_id).first()
            if transaction:
                transaction.status = status
                transaction.desc = desc
                db.session.commit()
                print(f"Updated transaction with id {transaction.id}")
                if status == "Success":
                    save_payment(transaction)
            else:
                print(f"No transactions found with id {trans_id}")
        except Exception as e:
            print("Error updating transaction:", e)

    def save_payment(transaction):
        try:
            payment = Payment(
                student_id=transaction.trans_for,
                amount=transaction.amount,
                transaction_id=transaction.trans_id,
                description=transaction.user_description
            )
            db.session.add(payment)
            db.session.commit()
            print(f"Payment saved for student with id {transaction.phone}")
        except Exception as e:
            print("Error saving payment:", e)

    class SavePayment(Resource):
        def post(self):
            try:
                data = request.json
                student_id = data.get('student_id')
                amount = data.get('amount')
                transaction_id = data.get('transaction_id')
                description = data.get('description', '')

                if transaction_id:
                    transaction = Transaction.query.get(transaction_id)
                    if not transaction:
                        return jsonify({"error": "Transaction not found"}), 404

                payment = Payment(
                    student_id=student_id,
                    amount=amount,
                    transaction_id=transaction_id,
                    description=description
                )
                db.session.add(payment)
                db.session.commit()

                return jsonify({
                    "success": "Payment successfully recorded",
                    "payment_id": payment.id,
                }), 201

            except Exception as e:
                print("Error while saving payment:", e)
                return jsonify({"error": "Internal server error"}), 500

    # Endpoints listing
    payment_api.add_resource(NewMpesa, '/new_mpesa')
    payment_api.add_resource(ConfirmPayment, '/confirm_payment/<int:transid>')
    payment_api.add_resource(MpesaCallback, '/callback')
    payment_api.add_resource(SavePayment, '/save_payment')
