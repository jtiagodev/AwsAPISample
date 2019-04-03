'use strict';

// Reading Parameters
// event['pathParameters']['param1']
// event["queryStringParameters"]['queryparam1']
// event['requestContext']['identity']['userAgent']
// event['requestContext']['identity']['sourceIP']
// event['headers']['day']
// event['body']['time'] // let body = JSON.parse(event.body)



exports.handler = (event, context) => {

  // Imports
  const mysql = require('mysql')
  const util = require('util');
  //require('dotenv').config();

  // Custom Error
  function LambdaError(message) {
    this.name = "LambdaError";
    this.message = message;
  }
  LambdaError.prototype = new Error();

  // Connecting to RDS
  const options = {
    host: process.env.RDS_MYSQL_HOST,
    port: process.env.RDS_MYSQL_PORT,
    user: process.env.RDS_MYSQL_USER,
    password: process.env.RDS_MYSQL_PW,
    database: process.env.RDS_MYSQL_DB
  }
  const connection = mysql.createConnection(options)

  connection.connect(err => {
    if (err) {
      throw new LambdaError("An error occurred while connecting to the DB");
    }
  });

  // Promisifying Queries
  const query = util.promisify(connection.query).bind(connection);

  // Querying
  let response = (async () => {
    try {
      if (event.pathParameters && event.pathParameters.id) {
        let forceId = event.pathParameters.id;
        const officers = await query(`select name, rank, bio from officers WHERE force_id = '${forceId}'`);
        let resBody = { 'officers':
        officers
        };
        let res = {
          'isBase64Encoded': false,
          'statusCode': 200,
          'body': JSON.stringify(resBody)
        };
        return res;
      }
    } catch (e) {
      throw new LambdaError(e.message);
    }
  })()

  // Returns the response
  return response;

};

// exports.GetForces();
// exports.GetForcesInfoById({ pathParameters: { id: 'cheshire' }});
// exports.GetForcesPeopleById({ pathParameters: { id: 'essex' }});
// exports.DeleteForceById({ pathParameters: { id: 'cheshire' }});
//  exports.InsertForce({ body: 
// {
//   id: "cheshire",
//   description:
//    "<p>Cheshire Constabulary is responsible for policing the unitary authorities of Cheshire East, Cheshire West and Chester, Halton and Warrington</p>",
//   name: "Cheshire Constabulary",
//   telephone: 101,
//   url: "http://www.cheshire.police.uk" 
// }
// });


// {
//   "id": "cheshire",
//   "description":
//    "<p>Cheshire Constabulary is responsible for policing the unitary authorities of Cheshire East, Cheshire West and Chester, Halton and Warrington</p>",
//   "name": "Cheshire Constabulary",
//   "telephone": 101,
//   "url": "http://www.cheshire.police.uk"
//   }