# Bank Transactions - API

## Using Flask, Docker, MongoDB

<br>

### Table of Resource Method Chart

| Resources         | URLs      | Method | Parameters                              | status codes            |
| ----------------- | --------- | ------ | --------------------------------------- | ----------------------- |
| **Register**      | /register | POST   | username, password                      | 200, 300, 301           |
| **Add**           | /add      | POST   | username, password, ammount             | 200, 300, 301, 304      |
| **Transfere**     | /transfer | POST   | username, password, to_account, ammount | 200, 300, 301, 303, 304 |
| **Check Balance** | /balance  | POST   | username, password                      | 200, 300, 301           |
| **Take Loan**     | /takeloan | POST   | username, password, amount              | 200, 300, 301, 304      |
| **Pay Loan**      | /payloan  | POST   | username, password, amount              | 200, 300, 301, 304      |

<br>

### Satus codes:

| Status Code | Description          |
| ----------- | -------------------- |
| **200**     | OK                   |
| **301**     | Invalid username     |
| **302**     | Invalid password     |
| **303**     | Not engough money    |
| **304**     | Negative transaction |
