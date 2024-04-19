# ChatApp   

## Server

Navigate to the server directory:
```bash
cd server
```

Install dependencies: 
```bash
pip install -r requirements.txt
```
Create a .env file with the following content:
```bash
# server/.env
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
MONGO_URI=your_mongodb_uri_here
```

To run the server application:
```bash
python app.py
```
## Client 

Navigate to the client directory:
```bash
cd client
```

Install dependencies: 
```bash
pip install -r requirements.txt
```
Create a .env file with the following content:
```bash
# client/.env
BACKEND_URL=http://your-backend-url.com
```

To run the client application:
```bash
python app.py
```
