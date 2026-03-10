# Machine Learning with CICD



## Environment variable for APPS

### AWS Integration

- `PREDICTION_API_URL`: API Gateway Prediction URL (format: `https://<id-apigateway>.execute-api.<region>.amazonaws.com/<stage>/predictions`) **(Required)**
- `FORECAST_API_URL`: API Gateway Forecast URL (format: `https://<id-apigateway>.execute-api.<region>.amazonaws.com/<stage>/forecasts`) **(Required)**
- `API_GATEWAY_KEY`: API Gateway Key **(Optional)**

### AWS Credential

- `AWS_ACCESS_KEY_ID`: sts assume-role access key id **(Required)**
- `AWS_SECRET_ACCESS_KEY`: sts assume-role secret access key **(Required)**
- `AWS_SESSION_TOKEN`: sts assume-role session token **(Required)**

### Flask Config

- `FLASK_HOST`: Host **(Optional)**
- `FLASK_PORT`: Port **(Optional)**
- `FLASK_DEBUG`: Debug **(Optional)**