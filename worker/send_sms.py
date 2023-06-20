import requests

url='https://www.fast2sms.com/dev/bulkV2'
message='Your otp for LaborSpot is'
numbers=+919645610883
payload=f'sender_id=TXTIND&message={message}&route=v3&language=english&numbers={numbers}'
headers={
    'authorization': "wtDopSlBIrm0GAZEPyse51bUNvzda6uTi2hknJfxFq437XHYcQDzKAef56E1R8IkqZCbht2xjipyu79v",
    'Content-Type': "application/x-www-form-urlencoded"
}

response = requests.request("POST", url, data=payload, headers=headers)
print(response.text)