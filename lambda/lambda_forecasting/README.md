# Lambda Forecasting

## ENVIRONMENT VARIABLES

`FORECASTING_MODEL_BUCKET=your bucket model`<br/>
`FORECASTING_MODEL_KEY=models/hybrid_model.pkl`<br/>
`PRODUCT_EMBEDDINGS_TABLE=ProductEmbeddings`<br/>
`SALES_HISTORY_TABLE=SalesHistory`<br/>
`USER_INTERACTIONS_TABLE=UserInteractions`


## Method POST Testing
```json
{
  "method": "moving_average",
  "periods": 30,
  "metric": "amount"
}